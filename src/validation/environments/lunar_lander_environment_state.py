from dataclasses import dataclass

from reinforcement_learning import EnvironmentState


@dataclass
class LunarLanderEnvironmentState(EnvironmentState):
    x_coordinate: float
    y_coordinate: float
    x_velocity: float
    y_velocity: float
    angle: float
    angular_velocity: float
    left_leg_in_contact_with_ground: bool
    right_leg_in_contact_with_ground: bool
