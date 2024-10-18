from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Factory, Resource, Singleton

from . import resources_initializer, use_cases
from .persistence.i_videos_repository import IVideosRepository
from .persistence.in_memory_videos_repository import InMemoryVideosRepository
from .resources_initializer import ResourcesInitializer
from .services.i_computer_vision_model import IComputerVisionModel
from .services.yolo_computer_vision_model import YoloComputerVisionModel
from .settings.i_files_settings import IFilesSettings
from .settings.files_settings import FilesSettings


class Container(DeclarativeContainer):
    videos_repository: Singleton[IVideosRepository] = Singleton(InMemoryVideosRepository)
    computer_vision_model: Singleton[IComputerVisionModel] = Singleton(YoloComputerVisionModel)
    files_settings: Factory[IFilesSettings] = Factory(FilesSettings)
    wiring_config: WiringConfiguration = WiringConfiguration(modules=[resources_initializer], packages=[use_cases])
    resources_initializer = Resource(ResourcesInitializer)
