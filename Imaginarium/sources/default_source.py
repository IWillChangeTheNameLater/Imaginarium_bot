from typing import Collection

import aiohttp

from . import BaseSource
from .. import rules_setup


class DefaultSource(BaseSource):
    """Class that inherits from "BaseSource" and is used as a default source."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, link=r'https://api.rand.by/image', **kwargs)

        self.included_types: Collection = rules_setup.included_types
        self.excluded_types: Collection = rules_setup.excluded_types

    async def get_cards_count(self) -> float('inf'):
        """Return infinity because the cards count is unlimited."""
        return float('inf')

    async def is_valid(self) -> True:
        return True

    async def get_random_card(self) -> str:
        """Return a random image from the site: https://api.rand.by/image

        :return: Link to an image."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self._link) as response:
                response_json = await response.json()
                return response_json['urls']['raw']
