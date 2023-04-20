class ImaginariumException(Exception):
    """Base exception class for Imaginarium package
    raised when errors related to Imaginarium game occurred."""

    def __init__(self, msg=None):
        super().__init__(
            msg or
            'An error occurred during the game.'
        )


class InvalidSource(ImaginariumException):
    """Exception raised when the source does not work."""

    def __init__(self, msg=None):
        super().__init__(
            msg or
            'The source is currently unavailable.'
        )


class NoAnyCards(InvalidSource, LookupError):
    """Exception raised when there are no cards in the source."""

    def __init__(self):
        super().__init__(
            'This source does not contain any cards that can be received.'
        )


class UnsupportedSource(InvalidSource, ValueError):
    """Exception raised when the source is not supported."""

    def __init__(self, source=None):
        if source:
            msg = f'The "{source}" source is unsupported.'
        else:
            msg = 'The source is unsupported.'

        super().__init__(msg)


class GameIsStarted(ImaginariumException):
    """Exception raised when trying to do something
    that cannot be changed during the game."""

    def __init__(self, msg=None):
        super().__init__(
            msg or
            'You cannot perform this action if the game has started.'
        )


class GameIsEnded(ImaginariumException):
    """Exception raised when trying to do something
    that cannot be done after the game."""

    def __init__(self, msg=None):
        super().__init__(
            msg or
            'You cannot perform this action if the game has ended.'
        )


class NoAnyUsedSources(ImaginariumException):
    """Exception raised when there are no sources to use."""

    def __init__(self):
        super().__init__(
            'There are no sources to use.'
        )


class NotEnoughPlayers(ImaginariumException, TypeError):
    """Exception raised when there are not enough players to perform an action."""

    def __init__(self, msg=None):
        super().__init__(
            msg or
            'There are not enough players to perform the action.'
        )


class PlayerAlreadyJoined(ImaginariumException, ValueError):
    """Exception raised when the player is already joined the game."""

    def __init__(self, player=None):
        if player:
            msg = f'The "{player}" player has already joined.'
        else:
            msg = 'The player has already joined.'

        super().__init__(msg)


class PlayerAlreadyLeft(ImaginariumException, ValueError):
    """Exception raised when the player is already left the game."""

    def __init__(self, player=None):
        if player:
            msg = f'The "{player}" player has already left.'
        else:
            msg = 'The player has already left.'

        super().__init__(msg)
