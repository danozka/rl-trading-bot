import torch
from torch import device, Tensor
from torch.nn import Linear, ReLU, Sequential, Softmax

from reinforcement_learning import PpoPolicy, PpoPolicyOutput
from validation.environments.lunar_lander_environment_state import LunarLanderEnvironmentState


class LunarLanderPpoPolicy(PpoPolicy):
    _device: device = device('cuda') if torch.cuda.is_available() else device('cpu')
    _shared_layers_out_features: int = 128
    _shared_layers: Sequential
    _actor: Sequential
    _critic: Sequential

    def __init__(self) -> None:
        super().__init__()
        self._shared_layers = Sequential(
            Linear(in_features=8, out_features=32),
            ReLU(),
            Linear(in_features=32, out_features=64),
            ReLU(),
            Linear(in_features=64, out_features=self._shared_layers_out_features),
            ReLU()
        )
        self._actor = Sequential(
            Linear(in_features=self._shared_layers_out_features, out_features=64),
            ReLU(),
            Linear(in_features=64, out_features=32),
            ReLU(),
            Linear(in_features=32, out_features=4),
            Softmax(dim=-1)
        )
        self._critic = Sequential(
            Linear(in_features=self._shared_layers_out_features, out_features=64),
            ReLU(),
            Linear(in_features=64, out_features=32),
            ReLU(),
            Linear(in_features=32, out_features=1)
        )
        self.to(self._device)

    def forward(self, environment_states: list[LunarLanderEnvironmentState]) -> PpoPolicyOutput:
        shared_features: Tensor = torch.stack([self._get_shared_features(x) for x in environment_states])
        return PpoPolicyOutput(
            action_probabilities=self._actor(shared_features),
            state_values=self._critic(shared_features)
        )

    def get_device(self) -> device:
        return self._device

    def _get_shared_features(self, environment_state: LunarLanderEnvironmentState) -> Tensor:
        environment_state_input_tensor: Tensor = torch.tensor(
            data=[
                environment_state.x_coordinate,
                environment_state.y_coordinate,
                environment_state.x_velocity,
                environment_state.y_velocity,
                environment_state.angle,
                environment_state.angular_velocity,
                float(environment_state.left_leg_in_contact_with_ground),
                float(environment_state.right_leg_in_contact_with_ground)
            ],
            device=self._device,
            dtype=torch.float32
        )
        return self._shared_layers(environment_state_input_tensor)
