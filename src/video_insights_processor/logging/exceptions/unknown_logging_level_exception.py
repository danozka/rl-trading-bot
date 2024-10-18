class UnknownLoggingLevelException(Exception):

    def __init__(self, value: str) -> None:
        super().__init__(f'Logging level \'{value}\' is an unknown value')
