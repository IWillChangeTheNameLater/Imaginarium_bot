from random import randrange, shuffle
import os
from typing import Mapping, Container

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

        self._cards_quantity: int | None = None

    def _get_cards_quantity(self) -> int:
        """Return the number of posts in the specified group."""
        return vk_requests.wall.get(domain=self._domain, count=1)['count']

    def _set_cards_quantity(self, quantity: float = None) -> None:
        """Set the number of posts in the specified group."""
        if quantity is None:
            self._cards_quantity = self._get_cards_quantity()
        else:
            self._cards_quantity = quantity

    def get_random_card(self) -> str:
        """Return a random post from the specified group
        and extract its random suitable attachment.

        :return: Link to the attachment.

        :raises NoAnyPosts: If there are no posts in the specified group.

        .. note:: The source tries to find the card until it succeeds,
        so it can do it forever.
        """

        def extract_content_from_attachment(attachment: Mapping) -> str:
            """Extract the link to the suitable attachment from the attachment.

            :param attachment: Attachment from a post.

            :return: Link to the attachment."""
            match attachment['type']:
                case 'photo':
                    return attachment[attachment['type']]['sizes'][-1]['url']
                case 'video':
                    video_id = str(attachment[attachment['type']]['owner_id'])
                    video_id += '_' + str(attachment[attachment['type']]['id'])

                    return vk_requests.video.get(videos=video_id)['items'][0]['player']

        # Check if there are any posts in the specified group to look for
        self._set_cards_quantity()
        if self._cards_quantity == 0:
            raise exceptions.NoAnyPosts()

        # Get a random post from the specified group
        post = vk_requests.wall.get(domain=self._domain,
                                    offset=randrange(self._cards_quantity),
                                    count=1)

        # Extract attachments from the received post
        try:
            attachments = post['items'][0]['attachments']
        # If the received post has no attachments, try the next one
        except KeyError:
            return self.get_random_card()

        # Shuffle attachments order to get the first random suitable attachment
        shuffle(attachments)

        # Get the first suitable attachment
        for a in attachments:
            if a['type'] not in self._excluded_types:
                if self._included_types:
                    if a['type'] not in self._included_types:
                        continue
                return extract_content_from_attachment(a)

        # I do not know do I need this, but I will leave it
        return self.get_random_card()
