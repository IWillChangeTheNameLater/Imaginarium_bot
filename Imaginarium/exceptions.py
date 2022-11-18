class UnexpectedSource(ValueError):
    pass


class NoAnyPosts(LookupError):
    pass


class GameIsStarted(Exception):
    pass


class GameIsEnded(Exception):
    pass
