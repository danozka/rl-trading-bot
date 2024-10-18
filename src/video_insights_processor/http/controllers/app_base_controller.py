from abc import ABC, abstractmethod

from fastapi import APIRouter


class AppBaseController(ABC):

    @property
    @abstractmethod
    def api_router(self) -> APIRouter:
        raise NotImplementedError

    @staticmethod
    def _format_exception(exception: Exception) -> str:
        return f'{exception.__class__.__name__} - {exception}'
