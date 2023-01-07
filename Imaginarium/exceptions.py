class UnexpectedSource(ValueError):
	"""Raised when the source is not supported."""
	pass


class NoAnyPosts(LookupError):
	"""Raised when there are no posts in the source."""
	pass


class GameIsStarted(Exception):
	"""Raised when trying to change something that cannot be changed during the game."""
	pass


class NoAnyUsedSources(Exception):
	"""Raised when there are no sources to use."""
	pass


class NotEnoughPlayers(TypeError):
	"""Raised when there are not enough players."""
	pass


class GameIsEnded(Exception):
	"""Raised when trying to change something that cannot be changed after the game."""
	pass


class PlayerAlreadyJoined(ValueError):
	"""Raised when the player is already joined the game."""
	pass


class PlayerAlreadyLeft(ValueError):
	"""Raised when the player is already left the game."""
	pass
