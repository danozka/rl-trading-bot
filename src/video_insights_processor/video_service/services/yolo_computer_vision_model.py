import logging
import random
import time
from datetime import datetime, timedelta
from logging import Logger
from uuid import UUID, uuid4

from ..domain.aircraft_attitude import AircraftAttitude
from ..domain.aircraft_model import AircraftModel
from ..domain.enemy_aircraft import EnemyAircraft
from ..domain.missile_model import MissileModel
from ..domain.target_engagement import TargetEngagement
from ..domain.video import Video
from ..domain.video_insights import VideoInsights
from .i_computer_vision_model import IComputerVisionModel


class YoloComputerVisionModel(IComputerVisionModel):
    _log: Logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._log.debug('Starting computer vision model...')
        self._log.debug('Computer vision model started')

    def extract_video_insights(self, video: Video) -> VideoInsights:
        self._log.debug(f'Extracting insights from {video}...')
        time.sleep(10.0)
        current_time: datetime = datetime.utcnow()
        aircraft_attitude_history: list[AircraftAttitude] = []
        i: int
        for i in range(10):
            aircraft_attitude_history.append(
                AircraftAttitude(
                    timestamp=(current_time + timedelta(minutes=((i + 1) * 5.0))),
                    heading_angle_degrees=random.uniform(a=-180.0, b=180.0),
                    roll_angle_degrees=random.uniform(a=-180.0, b=180.0),
                    yaw_angle_degrees=random.uniform(a=-180.0, b=180.0)
                )
            )
        enemy_aircraft_detections: list[EnemyAircraft] = []
        number_of_detections: int = random.randint(a=1, b=5)
        for _ in range(number_of_detections):
            enemy_aircraft_id: UUID = uuid4()
            enemy_aircraft_model: AircraftModel = random.choice(list(AircraftModel))
            enemy_aircraft_engagements: list[TargetEngagement] = []
            number_of_engagements: int = random.randint(a=0, b=5)
            for _ in range(number_of_engagements):
                enemy_aircraft_engagements.append(
                    TargetEngagement(
                        target_id=enemy_aircraft_id,
                        engagement_timestamp=(current_time + timedelta(minutes=(random.randint(a=1, b=5) * 5.0))),
                        weapon_used_on_enemy=random.choice(list(MissileModel)),
                        enemy_target_was_hit=bool(random.randint(a=0, b=1))
                    )
                )
            enemy_aircraft_detections.append(
                EnemyAircraft(
                    enemy_aircraft_id=enemy_aircraft_id,
                    enemy_aircraft_model=enemy_aircraft_model,
                    engagements_on_enemy=enemy_aircraft_engagements
                )
            )
        result: VideoInsights = VideoInsights(
            video_id=video.id,
            total_mission_duration_minutes=random.uniform(a=30.0, b=120.0),
            aircraft_attitude_history=aircraft_attitude_history,
            enemy_aircraft_detected=enemy_aircraft_detections
        )
        self._log.debug(f'Insights from {video} extracted')
        return result
