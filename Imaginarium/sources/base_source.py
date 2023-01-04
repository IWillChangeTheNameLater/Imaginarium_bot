import abc
from typing import Collection, Any

from .. import rules_setup


class BaseSource(abc.ABC):
	def __init__(self,
	             link: str,
	             included_types: Collection = rules_setup.included_types,
	             excluded_types: Collection = rules_setup.excluded_types) -> None:
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

	@abc.abstractmethod
	def get_random_card(self) -> str:
		pass
