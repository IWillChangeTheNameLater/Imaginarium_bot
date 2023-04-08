from random import randrange, shuffle
from os import environ
from typing import Mapping, Container, MutableSequence
from functools import wraps

import dotenv
import aiovk2
from aiovk2.exceptions import VkException

from . import BaseSource
from .. import exceptions

dotenv.load_dotenv()

aiovk_api = aiovk2.API(aiovk2.TokenSession(access_token=environ['VK_PARSER_TOKEN']))


def is_valid_request(func):
    """Make the function check if the source is valid.

    Make the passed function raise the InvalidSource exception
    if the source is invalid because of vk_api error."""

    @wraps(func)
    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except VkException as e:
            raise exceptions.InvalidSource(
                f'The resource is unavailable due to the VK API side issues.'
            ) from e

    return inner


class Vk(BaseSource):
    """Class that inherits from "BaseSource" and is used to get cards from vk.com."""
    _types_map = {'photo': 'photo',
                  'video': 'video'}
    """Map of types that are supported by vk.com and types that are used in the code."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._domain: str = self._link[self._link.rfind(r'/') + 1:]
        # Specify types to vk attachment types
        self._included_types: Container = {y for i in self._included_types if (y := Vk._types_map.get(i))}
        self._excluded_types: Container = {y for i in self._excluded_types if (y := Vk._types_map.get(i))}

    @is_valid_request
    async def get_cards_count(self) -> int:
        """Return the number of posts in the specified group."""
        return (await aiovk_api.wall.get(domain=self._domain, count=1))['count']

    @is_valid_request
    async def is_valid(self) -> True:
        """Check if the source itself is valid.

		:return: True if the source is valid, False otherwise.

		:raises InvalidSource: If the source is invalid for some reason.
		:raises NoAnyPosts: If the source is invalid due to
		the lack of single card.

		.. note:: The source is invalid if it does not exist or is closed."""
        if await self.get_cards_count() == 0:
            raise exceptions.NoAnyPosts

        return True

    @is_valid_request
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

            :param post: JSON with a VK post.

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

                    return (await aiovk_api.video.get(video_id=video_id))['items'][0]['player']

        if await self.get_cards_count() == 0:
            raise exceptions.NoAnyPosts()

        # Get a random post from the specified group
        post = await aiovk_api.wall.get(domain=self._domain,
                                        offset=randrange(await self.get_cards_count()),
                                        count=1)

        try:
            attachments = extract_attachments_from_post(post)
        # VK post JSON contains empty attachments list instead of NULL,
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
