class ImaginariumException(Exception):
    """Base exception class for Imaginarium package
    raised when errors related to Imaginarium game occurred."""

    def __init__(self, message=None):
        super().__init__(
            message or
            'An error occurred during the game.'
        )


class InvalidSource(ImaginariumException):
    """Exception raised when the source does not work."""

    def __init__(self, message=None):
        super().__init__(
            message or
            'The source is currently unavailable.'
        )


class NoAnyCards(InvalidSource, LookupError):
    """Exception raised when there are no cards in the source."""

    def __init__(self, source=None):
        self.source = source

        if source:
            message = (f'The "{source}" source does not contain any cards '
                       f'that can be received.')
        else:
            message = 'This source does not contain any cards that can be received.'

        self.message = message

        super().__init__(message)


class UnsupportedSource(InvalidSource, ValueError):
    """Exception raised when the source is not supported."""

    def __init__(self, source=None):
        self.source = source

        if source:
            message = f'The "{source}" source is unsupported.'
        else:
            message = 'The source is unsupported.'

        self.message = message

        super().__init__(message)


class GameIsStarted(ImaginariumException):
    """Exception raised when trying to do something
    that cannot be changed during the game."""

    def __init__(self, message=None):
        super().__init__(
            message or
            'You cannot perform this action if the game has started.'
        )


class GameIsEnded(ImaginariumException):
    """Exception raised when trying to do something
    that cannot be done after the game."""

    def __init__(self, message=None):
        super().__init__(
            message or
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

    def __init__(self, message=None):
        super().__init__(
            message or
            'There are not enough players to perform the action.'
        )


class PlayerAlreadyJoined(ImaginariumException, ValueError):
    """Exception raised when the player is already joined the game."""

    def __init__(self, player=None):
        self.player = player

        if player:
            message = f'The "{player}" player has already joined.'
        else:
            message = 'The player has already joined.'

        self.message = message

        super().__init__(message)


class PlayerAlreadyLeft(ImaginariumException, ValueError):
    """Exception raised when the player is already left the game."""

    def __init__(self, player=None):
        self.player = player

        if player:
            message = f'The "{player}" player has already left.'
        else:
            message = 'The player has already left.'

        self.message = message

        super().__init__(message)
