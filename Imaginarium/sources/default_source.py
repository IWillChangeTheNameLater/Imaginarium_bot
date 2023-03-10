from typing import Collection

import dotenv
import requests

from . import BaseSource
from .. import rules_setup

dotenv.load_dotenv()


class DefaultSource(BaseSource):
    """Class that inherits from "BaseSource" and is used as a default source."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, link=r'https://api.rand.by/image', **kwargs)

        self.included_types: Collection = rules_setup.included_types
        self.excluded_types: Collection = rules_setup.excluded_types

    @property
    def cards_count(self) -> float('inf'):
        """Return infinity because the cards count is unlimited."""
        return float('inf')

    def is_valid(self) -> True:
        return True

    def get_random_card(self) -> str:
        """Return a random image from the site: https://api.rand.by/image

        :return: Link to an image."""
        return requests.get(self._link).json()['urls']['raw']
