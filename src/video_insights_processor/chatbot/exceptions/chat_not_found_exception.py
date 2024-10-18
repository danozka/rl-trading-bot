from uuid import UUID


class ChatNotFoundException(Exception):

    def __init__(self, chat_id: UUID) -> None:
        super().__init__(f'Chat with ID \'{chat_id}\' not found')
