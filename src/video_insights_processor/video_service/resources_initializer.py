from dependency_injector.resources import Resource
from dependency_injector.wiring import inject, Provide

from .services.i_computer_vision_model import IComputerVisionModel


class ResourcesInitializer(Resource):

    @inject
    def init(self, computer_vision_model: IComputerVisionModel = Provide['computer_vision_model']) -> None:
        pass
