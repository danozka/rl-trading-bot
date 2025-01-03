import gymnasium as gym
import numpy as np
from gymnasium import Env
from numpy.typing import NDArray

from reinforcement_learning import Environment
from validation.environments.lunar_lander_environment_state import LunarLanderEnvironmentState


class LunarLanderEnvironment(Environment):
    _env: Env

    def __init__(self) -> None:
        self._env = gym.make(
            id='LunarLander-v3', 
            continuous=False, 
            gravity=-10.0, 
            enable_wind=False, 
            wind_power=15.0, 
            turbulence_power=1.5
        )

    def reset(self, max_time_steps: int) -> LunarLanderEnvironmentState:
        observation: NDArray[np.float32] = self._env.reset()[0]
        return self._get_current_state(observation)

    def make_step(self, agent_action_id: int) -> LunarLanderEnvironmentState:
        observation: NDArray[np.float32]
        reward: float
        terminated: bool
        truncated: bool
        observation, reward, terminated, truncated, _ = self._env.step(agent_action_id)
        return self._get_current_state(observation=observation, reward=reward, done=(terminated or truncated))

    @staticmethod
    def _get_current_state(
        observation: NDArray[np.float32],
        reward: float = 0.0,
        done: bool = False
    ) -> LunarLanderEnvironmentState:
        return LunarLanderEnvironmentState(
            reward=reward,
            done=done,
            x_coordinate=float(observation[0]),
            y_coordinate=float(observation[1]),
            x_velocity=float(observation[2]),
            y_velocity=float(observation[3]),
            angle=float(observation[4]),
            angular_velocity=float(observation[5]),
            left_leg_in_contact_with_ground=bool(observation[6]),
            right_leg_in_contact_with_ground=bool(observation[7])
        )
