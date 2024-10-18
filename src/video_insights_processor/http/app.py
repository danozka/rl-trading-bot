import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .controllers.chats_controller import ChatsController
from .controllers.videos_controller import VideosController
from .middleware.request_identification_middleware import RequestIdentificationMiddleware
from .settings.app_settings import AppSettings
from ..logging.use_cases.logging_configuration_getter import LoggingConfigurationGetter
from ..logging.use_cases.logging_level_getter import LoggingLevelGetter


class App(FastAPI):
    _app_settings: AppSettings

    def __init__(self, app_settings: AppSettings = AppSettings()) -> None:
        self._app_settings = app_settings
        super().__init__(title=self._app_settings.name)
        self.add_middleware(
            middleware_class=CORSMiddleware,
            allow_origins=['*'],
            allow_methods=['*'],
            allow_headers=['*'],
            allow_credentials=True
        )
        self.add_middleware(RequestIdentificationMiddleware)
        self.include_router(ChatsController().api_router)
        self.include_router(VideosController().api_router)
        self.mount(path='/', app=StaticFiles(directory=self._app_settings.frontend_path, html=True, check_dir=False))

    def start(self) -> None:
        uvicorn.run(
            app=self,
            host=self._app_settings.host,
            port=self._app_settings.port,
            log_level=logging.getLevelName(LoggingLevelGetter().get_logging_level().value),
            log_config=LoggingConfigurationGetter().get_logging_configuration()
        )
