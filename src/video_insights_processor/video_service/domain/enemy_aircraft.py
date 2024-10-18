from uuid import UUID

from pydantic import BaseModel

from .aircraft_model import AircraftModel
from .target_engagement import TargetEngagement


class EnemyAircraft(BaseModel):
    enemy_aircraft_id: UUID
    enemy_aircraft_model: AircraftModel
    engagements_on_enemy: list[TargetEngagement]
