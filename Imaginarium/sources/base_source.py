import abc

from .. import rules_setup


class BaseSource(abc.ABC):
    def __init__(self,
                 link,
                 included_types=rules_setup.included_types,
                 excluded_types=rules_setup.excluded_types):
        self.link = link
        self._included_types = included_types
        self._excluded_types = excluded_types

    def __eq__(self, other):
        return self.link == other

    def __ne__(self, other):
        return self.link != other

    def __str__(self):
        return self.link

    def __hash__(self):
        return hash(self.link)

    @abc.abstractmethod
    def get_random_card(self):
        pass
