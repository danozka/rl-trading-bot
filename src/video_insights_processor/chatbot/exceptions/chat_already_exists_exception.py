from uuid import UUID


class ChatAlreadyExistsException(Exception):

    def __init__(self, chat_id: UUID) -> None:
        super().__init__(f'Chat with ID \'{chat_id}\' already exists in the system')
