import abc
from typing import Collection, Any

from .. import rules_setup


class BaseSource(abc.ABC):
    """Abstract class of source for receiving cards."""

    def __init__(self,
                 link: str,
                 included_types: Collection = rules_setup.included_types,
                 excluded_types: Collection = rules_setup.excluded_types) -> None:
        """Initialize the source.

        :param link: Link to the source.
        :param included_types: Types of cards that will be received from the source.
        :param excluded_types: Types of cards that will not be received from the source.
        """
        self._link: str = link
        self._included_types: Collection = included_types
        self._excluded_types: Collection = excluded_types

    def __eq__(self, other: Any) -> bool:
        try:
            return self._link == other._link
        except AttributeError:
            return self._link == other

    def __ne__(self, other: Any) -> bool:
        try:
            return self._link != other._link
        except AttributeError:
            return self._link != other

    def __str__(self) -> str:
        return self._link

    def __hash__(self) -> int:
        return hash(self._link)

    @property
    @abc.abstractmethod
    def cards_count(self) -> int:
        """The cards count the source can provide."""

    @abc.abstractmethod
    def get_random_card(self) -> str:
        """Get a random card from the source if it is available
        and the type of the card is not excluded.

        :return: A random card from the source."""
