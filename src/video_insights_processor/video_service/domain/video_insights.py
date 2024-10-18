from uuid import UUID

from pydantic import BaseModel

from .aircraft_attitude import AircraftAttitude
from .enemy_aircraft import EnemyAircraft


class VideoInsights(BaseModel):
    video_id: UUID
    total_mission_duration_minutes: float
    aircraft_attitude_history: list[AircraftAttitude]
    enemy_aircraft_detected: list[EnemyAircraft]
