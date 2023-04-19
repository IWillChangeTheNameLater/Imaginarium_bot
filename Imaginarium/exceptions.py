class UnsupportedSource(ValueError):
    """Exception raised when the source is not supported."""
    pass


class InvalidSource(UnsupportedSource):
    """Exception raised when the source does not work."""
    pass


class NoAnyPosts(LookupError, InvalidSource):
    """Exception raised when there are no posts in the source."""
    pass


class GameIsStarted(Exception):
    """Exception raised when trying to change something that cannot be changed during the game."""
    pass


class GameIsEnded(Exception):
    """Exception raised when trying to change something that cannot be changed after the game."""
    pass


class NoAnyUsedSources(Exception):
    """Exception raised when there are no sources to use."""
    pass


class NotEnoughPlayers(TypeError):
    """Exception raised when there are not enough players."""
    pass


class PlayerAlreadyJoined(ValueError):
    """Exception raised when the player is already joined the game."""
    pass


class PlayerAlreadyLeft(ValueError):
    """Exception raised when the player is already left the game."""
    pass
