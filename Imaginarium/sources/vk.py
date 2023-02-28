from random import randrange, shuffle
import os
from typing import Mapping, Container, MutableSequence

import dotenv
import vk_api

from . import BaseSource
from .. import exceptions

dotenv.load_dotenv()

vk_requests = vk_api.VkApi(token=os.environ['VK_PARSER_TOKEN']).get_api()


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

    @property
    def cards_amount(self) -> int:
        """Return the number of posts in the specified group."""
        return vk_requests.wall.get(domain=self._domain, count=1)['count']

    def get_random_card(self) -> str:
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

        def extract_content_from_attachment(attachment: Mapping) -> str:
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

                    return vk_requests.video.get(videos=video_id)['items'][0]['player']

        # Check if there are any posts in the specified group to look for
        if self.cards_amount == 0:
            raise exceptions.NoAnyPosts()

        # Get a random post from the specified group
        post = vk_requests.wall.get(domain=self._domain,
                                    offset=randrange(self.cards_amount),
                                    count=1)

        # Extract attachments from the received post
        try:
            attachments = extract_attachments_from_post(post)
        # VK post JSON contains empty attachments list instead of NULL,
        # so the error will never be raised,
        # but I'll leave it here just in case.
        except KeyError:
            return self.get_random_card()

        # Shuffle attachments order to get the first random suitable attachment
        shuffle(attachments)

        # Get the first suitable attachment
        for attachment in attachments:
            if attachment['type'] not in self._excluded_types:
                if self._included_types and attachment['type'] not in self._included_types:
                    continue
                return extract_content_from_attachment(attachment)

        # Search for the next card if there were no suitable attachments
        return self.get_random_card()
