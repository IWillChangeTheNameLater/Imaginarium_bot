import collections as _collections

from .texts import *
from . import languages_maps

from . import English
from . import Russian
from . import Ukrainian

users_languages = _collections.defaultdict(lambda: None)
