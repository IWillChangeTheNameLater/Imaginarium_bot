class UnsupportedSource(ValueError):
    """Raised when the source is not supported."""
    pass


class InvalidSource(UnsupportedSource):
    """Raised when the source does not work."""
    pass


class NoAnyPosts(LookupError, InvalidSource):
    """Raised when there are no posts in the source."""
    pass


class GameIsStarted(Exception):
    """Raised when trying to change something that cannot be changed during the game."""
    pass


class GameIsEnded(Exception):
    """Raised when trying to change something that cannot be changed after the game."""
    pass


class NoAnyUsedSources(Exception):
    """Raised when there are no sources to use."""
    pass


class NotEnoughPlayers(TypeError):
    """Raised when there are not enough players."""
    pass


class PlayerAlreadyJoined(ValueError):
    """Raised when the player is already joined the game."""
    pass


class PlayerAlreadyLeft(ValueError):
    """Raised when the player is already left the game."""
    pass
