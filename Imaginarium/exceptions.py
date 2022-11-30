class UnexpectedSource(ValueError):
	pass


class NoAnyPosts(LookupError):
	pass


class GameIsStarted(Exception):
	pass


class NoAnyUsedSources(Exception):
	pass


class NotEnoughPlayers(TypeError):
	pass


class GameIsEnded(Exception):
	pass
