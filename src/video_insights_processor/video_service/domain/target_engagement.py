from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .missile_model import MissileModel


class TargetEngagement(BaseModel):
    target_id: UUID
    engagement_timestamp: datetime
    weapon_used_on_enemy: MissileModel
    enemy_target_was_hit: bool
