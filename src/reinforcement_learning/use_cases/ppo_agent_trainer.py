import logging
from collections import deque
from logging import Logger
from uuid import UUID

from reinforcement_learning.agents.ppo_agent import PpoAgent
from reinforcement_learning.agents.ppo_agent_selected_action import PpoAgentSelectedAction
from reinforcement_learning.environments.environment import Environment
from reinforcement_learning.environments.environment_state import EnvironmentState
from reinforcement_learning.policies.i_ppo_policies_persistence import IPpoPoliciesPersistence
from reinforcement_learning.policies.ppo_policy import PpoPolicy


class PpoAgentTrainer:
    _log: Logger = logging.getLogger(__name__)
    _environment: Environment
    _ppo_policies_persistence: IPpoPoliciesPersistence
    _episodes: int
    _max_time_steps: int
    _policy_save_rate: int
    _rewards_memory: int
    _learning_rate: float
    _gamma: float
    _eps_clip: float
    _update_epochs: int
    _environment_states: list[EnvironmentState]
    _ppo_agent_selected_actions: list[PpoAgentSelectedAction]
    _rewards: list[float]
    _dones: list[bool]

    def __init__(
        self,
        environment: Environment,
        ppo_policies_persistence: IPpoPoliciesPersistence,
        episodes: int,
        max_time_steps: int,
        policy_save_rate: int = 10,
        rewards_memory: int = 100,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        eps_clip: float = 0.2,
        update_epochs: int = 4
    ) -> None:
        self._environment = environment
        self._ppo_policies_persistence = ppo_policies_persistence
        self._episodes = episodes
        self._max_time_steps = max_time_steps
        self._policy_save_rate = policy_save_rate
        self._rewards_memory = rewards_memory
        self._learning_rate = learning_rate
        self._gamma = gamma
        self._eps_clip = eps_clip
        self._update_epochs = update_epochs
        self._reset_buffer()

    def train_ppo_agent(self, ppo_policy_id: UUID) -> None:
        self._log.info(f'Training PPO agent with policy ID \'{ppo_policy_id}\'...')
        ppo_policy: PpoPolicy = self._ppo_policies_persistence.load_ppo_policy(ppo_policy_id)
        ppo_policy_old: PpoPolicy = self._ppo_policies_persistence.load_ppo_policy(ppo_policy_id)
        ppo_agent: PpoAgent = PpoAgent(
            ppo_policy=ppo_policy,
            ppo_policy_old=ppo_policy_old,
            learning_rate=self._learning_rate,
            gamma=self._gamma,
            eps_clip=self._eps_clip,
            update_epochs=self._update_epochs
        )
        episode_rewards: deque[float] = deque(maxlen=self._rewards_memory)
        episode: int
        for episode in range(self._episodes):
            episode_reward: float = 0.0
            environment_state: EnvironmentState = self._environment.reset(self._max_time_steps)
            for _ in range(self._max_time_steps):
                ppo_agent_selected_action: PpoAgentSelectedAction = ppo_agent.select_action(environment_state)
                environment_next_state: EnvironmentState = self._environment.make_step(
                    ppo_agent_selected_action.action_id
                )
                episode_reward += environment_next_state.reward
                self._add_to_buffer(
                    environment_state=environment_state,
                    ppo_agent_selected_action=ppo_agent_selected_action,
                    reward=environment_next_state.reward,
                    done=environment_next_state.done
                )
                environment_state = environment_next_state
                if environment_state.done:
                    break
            ppo_agent.update(
                environment_states=self._environment_states,
                ppo_agent_selected_actions=self._ppo_agent_selected_actions,
                rewards=self._rewards,
                dones=self._dones
            )
            self._reset_buffer()
            episode_rewards.append(episode_reward)
            mean_episode_rewards: float = sum(episode_rewards) / len(episode_rewards)
            self._log.info(
                f'Episode {episode} - Reward {episode_reward:0.3f} - Mean reward {mean_episode_rewards:0.3f} - '
                f'{self._environment.get_episode_summary()}'
            )
            if episode % self._policy_save_rate == 0:
                self._ppo_policies_persistence.save_ppo_policy(ppo_policy)
        self._log.info(f'PPO agent with policy ID \'{ppo_policy_id}\' training completed')

    def _reset_buffer(self) -> None:
        self._environment_states = []
        self._ppo_agent_selected_actions = []
        self._rewards = []
        self._dones = []

    def _add_to_buffer(
        self,
        environment_state: EnvironmentState,
        ppo_agent_selected_action: PpoAgentSelectedAction,
        reward: float,
        done: bool
    ) -> None:
        self._environment_states.append(environment_state)
        self._ppo_agent_selected_actions.append(ppo_agent_selected_action)
        self._rewards.append(reward)
        self._dones.append(done)
