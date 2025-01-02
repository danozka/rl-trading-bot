import torch
from torch import device, Tensor
from torch.distributions import Categorical
from torch.nn import MSELoss
from torch.nn.utils import clip_grad_norm_
from torch.optim import Adam

from reinforcement_learning.agents.ppo_agent_selected_action import PpoAgentSelectedAction
from reinforcement_learning.environments.environment_state import EnvironmentState
from reinforcement_learning.policies.ppo_policy import PpoPolicy
from reinforcement_learning.policies.ppo_policy_output import PpoPolicyOutput


class PpoAgent:
    _ppo_policy: PpoPolicy
    _ppo_policy_old: PpoPolicy
    _device: device
    _optimizer: Adam
    _mse_loss: MSELoss
    _gamma: float
    _eps_clip: float
    _update_epochs: int

    def __init__(
        self,
        ppo_policy: PpoPolicy,
        ppo_policy_old: PpoPolicy,
        learning_rate: float,
        gamma: float,
        eps_clip: float,
        update_epochs: int
    ) -> None:
        self._ppo_policy = ppo_policy
        self._ppo_policy_old = ppo_policy_old
        self._device = ppo_policy.get_device()
        self._optimizer = Adam(params=self._ppo_policy.parameters(), lr=learning_rate)
        self._mse_loss = MSELoss()
        self._gamma = gamma
        self._eps_clip = eps_clip
        self._update_epochs = update_epochs

    def select_action(self, environment_state: EnvironmentState) -> PpoAgentSelectedAction:
        with torch.no_grad():
            ppo_policy_output: PpoPolicyOutput = self._ppo_policy_old([environment_state])
        distribution: Categorical = Categorical(ppo_policy_output.action_probabilities)
        action: Tensor = distribution.sample()
        return PpoAgentSelectedAction(action_id=action.item(), log_probability=distribution.log_prob(action).item())

    def update(
        self,
        environment_states: list[EnvironmentState],
        ppo_agent_selected_actions: list[PpoAgentSelectedAction],
        rewards: list[float],
        dones: list[bool]
    ) -> None:
        actions: Tensor = torch.tensor(
            data=[x.action_id for x in ppo_agent_selected_actions],
            device=self._device,
            dtype=torch.long
        )
        old_log_probabilities: Tensor = torch.tensor(
            data=[x.log_probability for x in ppo_agent_selected_actions],
            device=self._device,
            dtype=torch.float32
        )
        rewards: Tensor = torch.tensor(
            data=rewards,
            device=self._device,
            dtype=torch.float32
        )
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-8)
        dones: Tensor = torch.tensor(
            data=dones,
            device=self._device,
            dtype=torch.float32
        )
        with torch.no_grad():
            ppo_policy_output: PpoPolicyOutput = self._ppo_policy_old(environment_states)
            values: Tensor = ppo_policy_output.state_values.squeeze()
            values = torch.cat((values, torch.tensor(data=[0.0], device=self._device)))  # Bootstrap value
            advantages: Tensor = self._compute_advantages(rewards, dones, values)
            returns = advantages + values[:-1]
        for _ in range(self._update_epochs):
            ppo_policy_output: PpoPolicyOutput = self._ppo_policy(environment_states)
            distribution: Categorical = Categorical(ppo_policy_output.action_probabilities)
            log_probabilities: Tensor = distribution.log_prob(actions)
            ratios: Tensor = torch.exp(log_probabilities - old_log_probabilities.detach())
            surrogate_1: Tensor = ratios * advantages
            surrogate_2: Tensor = torch.clamp(
                input=ratios,
                min=(1.0 - self._eps_clip),
                max=(1.0 + self._eps_clip)
            ) * advantages
            actor_loss: Tensor = -torch.min(surrogate_1, surrogate_2).mean()
            critic_loss: Tensor = self._mse_loss(
                input=ppo_policy_output.state_values.squeeze(),
                target=returns.detach()
            )
            entropy_loss: Tensor = distribution.entropy().mean()
            loss: Tensor = actor_loss + 0.5 * critic_loss - 0.01 * entropy_loss
            self._optimizer.zero_grad()
            loss.backward()
            clip_grad_norm_(self._ppo_policy.parameters(), max_norm=0.5)
            self._optimizer.step()
        self._ppo_policy_old.load_state_dict(self._ppo_policy.state_dict())

    def _compute_advantages(self, rewards: Tensor, dones: Tensor, values: Tensor) -> Tensor:
        advantages: list[Tensor] = []
        gae: Tensor = torch.tensor(data=0.0, device=self._device, dtype=torch.float32)
        step: int
        for step in reversed(range(len(rewards))):
            delta: Tensor = rewards[step] + self._gamma * values[step + 1] * (1 - dones[step]) - values[step]
            gae = delta + self._gamma * gae
            advantages.insert(0, gae)
        result: Tensor = torch.tensor(data=advantages, device=self._device, dtype=torch.float32)
        result = (result - result.mean()) / (result.std() + 1e-8)
        return result
