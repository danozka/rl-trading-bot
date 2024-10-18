import logging
from logging import Logger
from typing import Iterator

from llama_cpp import Llama
from llama_cpp.llama_types import (
    ChatCompletionRequestMessage,
    ChatCompletionRequestSystemMessage,
    ChatCompletionStreamResponseDelta,
    CreateChatCompletionStreamResponse
)

from .i_large_language_model import ILargeLanguageModel
from ..domain.chat_message import ChatMessage
from ..domain.chat_message_role_type import ChatMessageRoleType
from ..exceptions.unknown_chat_message_role_type_exception import UnknownChatMessageRoleTypeException
from ..settings.large_language_model_settings import LargeLanguageModelSettings


class LargeLanguageModel(Llama, ILargeLanguageModel):
    _log: Logger = logging.getLogger(__name__)

    def __init__(
        self,
        large_language_model_settings: LargeLanguageModelSettings = LargeLanguageModelSettings()
    ) -> None:
        self._log.debug('Starting large language model...')
        super().__init__(
            model_path=str(large_language_model_settings.model_path),
            n_ctx=large_language_model_settings.context_length,
            n_gpu_layers=large_language_model_settings.number_of_gpu_layers,
            verbose=False
        )
        self._log.debug('Large language model started')

    def stream_chat_response_message(self, system_prompt: str, chat_messages: list[ChatMessage]) -> Iterator[str]:
        self._log.debug('Streaming chat response message...')
        system_message: ChatCompletionRequestSystemMessage = {
            'role': 'system',
            'content': system_prompt
        }
        chat_completion_iterator: Iterator[CreateChatCompletionStreamResponse] = self.create_chat_completion(
            messages=([system_message] + [self._adapt_input_message(message) for message in chat_messages]),
            stream=True
        )
        stream_message: CreateChatCompletionStreamResponse
        for stream_message in chat_completion_iterator:
            content: str | None = self._adapt_output_message_content(stream_message)
            if content is not None:
                yield content
        self._log.debug('Chat response message streaming completed')

    @staticmethod
    def _adapt_input_message(message: ChatMessage) -> ChatCompletionRequestMessage:
        role: str
        if message.role_type == ChatMessageRoleType.assistant:
            role = 'assistant'
        elif message.role_type == ChatMessageRoleType.system:
            role = 'system'
        elif message.role_type == ChatMessageRoleType.user:
            role = 'user'
        else:
            raise UnknownChatMessageRoleTypeException(message.role_type.value)
        return {'role': role, 'content': message.content}

    @staticmethod
    def _adapt_output_message_content(stream_message: CreateChatCompletionStreamResponse) -> str | None:
        stream_message_delta: ChatCompletionStreamResponseDelta = stream_message['choices'][0]['delta']
        if 'content' in stream_message_delta:
            return stream_message_delta['content']
        else:
            return None
