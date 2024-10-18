from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Resource, Singleton

from . import resources_initializer, use_cases
from .persistence.i_chats_repository import IChatsRepository
from .persistence.in_memory_chats_repository import InMemoryChatsRepository
from .resources_initializer import ResourcesInitializer
from .services.i_large_language_model import ILargeLanguageModel
from .services.large_language_model import LargeLanguageModel


class Container(DeclarativeContainer):
    chats_repository: Singleton[IChatsRepository] = Singleton(InMemoryChatsRepository)
    large_language_model: Singleton[ILargeLanguageModel] = Singleton(LargeLanguageModel)
    wiring_config: WiringConfiguration = WiringConfiguration(modules=[resources_initializer], packages=[use_cases])
    resources_initializer: Resource[ResourcesInitializer] = Resource(ResourcesInitializer)
