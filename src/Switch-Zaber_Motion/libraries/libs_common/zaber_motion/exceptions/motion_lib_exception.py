class MotionLibException(Exception):

    @property
    def message(self) -> str:
        """
        Error message of the exception.
        """
        return self._message

    def __init__(self, message: str):
        self._message = message
        Exception.__init__(self, self._message)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self._message}"

    def __repr__(self) -> str:
        return self.__str__()
