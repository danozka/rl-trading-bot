from .chatbot import container as chatbot_container
from .logging.use_cases.logging_builder import LoggingBuilder
from .video_service import container as video_service_container


LoggingBuilder().build()
