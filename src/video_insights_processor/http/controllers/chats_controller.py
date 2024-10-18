import logging
from logging import Logger
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .app_base_controller import AppBaseController
from ..adapters.chat_adapter import ChatAdapter
from ..dtos.chat_dto import ChatDto
from ..dtos.video_chat_message_dto import VideoChatMessageDto
from ...chatbot.exceptions.chat_already_exists_exception import ChatAlreadyExistsException
from ...chatbot.exceptions.chat_not_found_exception import ChatNotFoundException
from ...chatbot.use_cases.chat_response_streamer import ChatResponseStreamer
from ...chatbot.use_cases.chats_adder import ChatsAdder
from ...chatbot.use_cases.chats_deleter import ChatsDeleter
from ...chatbot.use_cases.chats_getter import ChatsGetter
from ...video_service.exceptions.video_insights_not_found_exception import VideoInsightsNotFoundException
from ...video_service.exceptions.video_not_found_exception import VideoNotFoundException
from ...video_service.use_cases.video_insights_getter import VideoInsightsGetter


class ChatsController(AppBaseController):
    _log: Logger = logging.getLogger(__name__)
    _api_router: APIRouter = APIRouter(prefix='/api/chats', tags=['chats'])
    _chat_adapter: ChatAdapter

    def __init__(self, chat_adapter: ChatAdapter = ChatAdapter()) -> None:
        self._api_router.add_api_route(path='', endpoint=self.get_all_chats, methods=['GET'], response_model=None)
        self._api_router.add_api_route(path='/{chat_id}', endpoint=self.add_chat, methods=['PUT'])
        self._api_router.add_api_route(path='/{chat_id}', endpoint=self.delete_chat, methods=['DELETE'])
        self._api_router.add_api_route(
            path='/response/stream',
            endpoint=self.stream_chat_response_message,
            methods=['POST']
        )
        self._chat_adapter = chat_adapter

    @property
    def api_router(self) -> APIRouter:
        return self._api_router

    async def get_all_chats(self) -> list[ChatDto]:
        self._log.info('Getting all chats...')
        try:
            result: list[ChatDto] = [
                self._chat_adapter.adapt_chat(chat) for chat in await ChatsGetter().get_all_chats()
            ]
            self._log.info('All chats retrieved')
            return result
        except Exception as exception:
            self._log.error(f'Exception found while getting all chats: {self._format_exception(exception)}')
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def add_chat(self, chat_id: UUID) -> None:
        self._log.info(f'Adding chat \'{chat_id}\'...')
        try:
            await ChatsAdder().add_chat(chat_id)
            self._log.info(f'Chat \'{chat_id}\' added')
        except ChatAlreadyExistsException as exception:
            self._log.error(f'Exception found while adding chat \'{chat_id}\': {self._format_exception(exception)}')
            raise HTTPException(status_code=409, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(f'Exception found while adding chat \'{chat_id}\': {self._format_exception(exception)}')
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def delete_chat(self, chat_id: UUID) -> None:
        self._log.info(f'Deleting chat \'{chat_id}\'...')
        try:
            await ChatsDeleter().delete_chat(chat_id)
            self._log.info(f'Chat \'{chat_id}\' deleted')
        except ChatNotFoundException as exception:
            self._log.error(f'Exception found while deleting chat \'{chat_id}\': {self._format_exception(exception)}')
            raise HTTPException(status_code=404, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(f'Exception found while deleting chat \'{chat_id}\': {self._format_exception(exception)}')
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def stream_chat_response_message(self, video_chat_message_dto: VideoChatMessageDto) -> StreamingResponse:
        self._log.info(f'Streaming response for {video_chat_message_dto}...')
        try:
            system_prompt: str = (
                f'You are a helpful assistant that analyzes data extracted from military aircraft videos and answers '
                f'questions related to it in a summarized way. The following data was obtained for the current video: '
                f'{await VideoInsightsGetter().get_video_insights_as_string(video_chat_message_dto.video_id)}'
            )
            result: StreamingResponse = StreamingResponse(
                ChatResponseStreamer().stream_chat_response_message(
                    system_prompt=system_prompt,
                    chat_message=self._chat_adapter.adapt_video_chat_message_dto(video_chat_message_dto)
                )
            )
            self._log.info(f'Response streaming for {video_chat_message_dto} completed')
            return result
        except VideoNotFoundException as exception:
            self._log.error(
                f'Exception found while streaming response for {video_chat_message_dto}: '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=404, detail=self._format_exception(exception))
        except VideoInsightsNotFoundException as exception:
            self._log.error(
                f'Exception found while streaming response for {video_chat_message_dto}: '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=404, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(
                f'Exception found while streaming response for {video_chat_message_dto}: '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=500, detail=self._format_exception(exception))
