from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseJsonDto(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    def __str__(self) -> str:
        return self.__repr__()
