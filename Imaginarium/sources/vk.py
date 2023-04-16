from asyncio import sleep
from random import randrange, shuffle
from os import environ
from functools import partial
from typing import (
    Mapping,
    Container,
    MutableSequence,
    Callable,
    Awaitable,
    Any
)

from dotenv import load_dotenv
import aiovk2
from aiovk2.exceptions import VkException
from aiovk2.api import Request

from . import BaseSource
from ..exceptions import InvalidSource, NoAnyPosts

load_dotenv()


async def async_handle_vk_exception(func: Callable[[None], Awaitable[Any]]) \
        -> Awaitable[Any]:
    """Handle Vk API errors caused by the function.

    Handle VkException from aiovk2 which are caused by the passed function.
    Raise the InvalidSource exception instead of the occurred VkException.

    Wait 1 second if an error code of the occurred exception is 6
    (too many requrests per second).

    :param func: The asynchronous function that might raise VkException
    from the aiovk2 library.

    :return: The result of the passed function.

    :raise InvalidSource: If the VkException has occurred."""
    try:
        return await func()
    except VkException as e:
        match e.args[0]['error_code']:
            case 6:
                await sleep(1)
                return await async_handle_vk_exception(func)
            case _:
                raise InvalidSource(
                    f'The source is unavailable due to the Vk API side issues.'
                ) from e


class VkRequest(Request):
    """A subclass which overrides the Request class methods."""

    def __getattr__(self, method_name):
        """Overrides the method of Request class.

        Return VkRequest instead of aiovk2.Request class."""
        return VkRequest(self._api, self._method_name + '.' + method_name)

    async def __call__(self, **method_args):
        """Overrides the method of Request class.

        Handle Vk API errors caused by the aiovk2."""
        return await async_handle_vk_exception(
            partial(super().__call__, **method_args))


class VkAPI(aiovk2.API):
    """A subclass which overrides the Request class methods."""

    def __getattr__(self, method_name):
        """Overrides the method of Request class.

        Return VkRequest instead of aiovk2.Request class."""
        return VkRequest(self, method_name)

    async def __call__(self, method_name, **method_kwargs):
        """Overrides the method of Request class.

        Handle Vk API errors caused by the aiovk2."""
        return await async_handle_vk_exception(
            partial(super().__call__, method_name, **method_kwargs))


vk_api = VkAPI(aiovk2.TokenSession(access_token=environ['VK_PARSER_TOKEN']))


class Vk(BaseSource):
    """Class that inherits from "BaseSource" and is used to get cards from vk.com."""
    _types_map = {'photo': 'photo',
                  'video': 'video'}
    """Map of types that are supported by a Vk API and types that are used in the code."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._domain: str = self._link[self._link.rfind(r'/') + 1:]
        # Specify types to vk attachment types
        self._included_types: Container = {y for i in self._included_types if (y := Vk._types_map.get(i))}
        self._excluded_types: Container = {y for i in self._excluded_types if (y := Vk._types_map.get(i))}

    async def get_cards_count(self) -> int:
        """Return the number of posts in the specified group."""
        return (await vk_api.wall.get(domain=self._domain, count=1))['count']

    async def is_valid(self) -> True:
        """Check if the source itself is valid.

		:return: True if the source is valid, False otherwise.

		:raises InvalidSource: If the source is invalid for some reason.
		:raises NoAnyPosts: If the source is invalid due to
		the lack of single card.

		.. note:: The source is invalid if it does not exist or is closed."""
        if await self.get_cards_count() == 0:
            raise NoAnyPosts()

        return True

    async def get_random_card(self) -> str:
        """Return a random post from the specified group
        and extract its random suitable attachment.

        :return: Link to the attachment.

        :raises NoAnyPosts: If there are no posts in the specified group.

        .. note:: The source tries to find the card until it succeeds,
        so it can do it forever.
        """

        def extract_attachments_from_post(post: Mapping) -> MutableSequence:
            """Extract attachments from the post.

            :param post: JSON with a Vk post.

            :return: JSON with an attachments from the post.

            :raise KeyError: If there is no attachments to be extracted."""
            items = post['items'][0]
            if 'copy_history' in items:
                items = items['copy_history'][0]

            return items['attachments']

        async def extract_content_from_attachment(attachment: Mapping) -> str:
            """Extract the link to the suitable attachment from the attachment.

            :param attachment: JSON with an attachment from a post.

            :return: Link to the attachment."""
            attachment_type = attachment['type']
            multimedia = attachment[attachment_type]
            match attachment_type:
                case 'photo':
                    return multimedia['sizes'][-1]['url']
                case 'video':
                    video_id = str(multimedia['owner_id'])
                    video_id += '_' + str(multimedia['id'])

                    return (await vk_api.video.get(video_id=video_id))['items'][0]['player']

        if await self.get_cards_count() == 0:
            raise NoAnyPosts()

        # Get a random post from the specified group
        post = await vk_api.wall.get(domain=self._domain,
                                     offset=randrange(await self.get_cards_count()),
                                     count=1)

        try:
            attachments = extract_attachments_from_post(post)
        # Vk post JSON contains empty attachments list instead of NULL,
        # so the error will never be raised,
        # but I'll leave it here just in case.
        except (KeyError, IndexError):
            return await self.get_random_card()

        # Shuffle attachments order to get the first random suitable attachment
        shuffle(attachments)

        # Get the first suitable attachment
        for attachment in attachments:
            if attachment['type'] not in self._excluded_types:
                if self._included_types and attachment['type'] not in self._included_types:
                    continue

                return await extract_content_from_attachment(attachment)

        return await self.get_random_card()
