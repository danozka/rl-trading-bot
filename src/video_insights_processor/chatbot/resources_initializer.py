from dependency_injector.resources import Resource
from dependency_injector.wiring import inject, Provide

from .services.i_large_language_model import ILargeLanguageModel


class ResourcesInitializer(Resource):

    @inject
    def init(self, large_language_model: ILargeLanguageModel = Provide['large_language_model']) -> None:
        pass
