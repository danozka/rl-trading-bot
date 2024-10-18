from datetime import datetime

from pydantic import BaseModel


class AircraftAttitude(BaseModel):
    timestamp: datetime
    heading_angle_degrees: float
    roll_angle_degrees: float
    yaw_angle_degrees: float
