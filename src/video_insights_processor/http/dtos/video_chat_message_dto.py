from uuid import UUID

from .chat_message_dto import ChatMessageDto


class VideoChatMessageDto(ChatMessageDto):
    video_id: UUID
