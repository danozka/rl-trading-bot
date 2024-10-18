class UnknownChatMessageRoleTypeException(Exception):

    def __init__(self, value: str) -> None:
        super().__init__(f'Message role type \'{value}\' is an unknown value')
