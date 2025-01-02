import torch
from torch import device, Tensor
from torch.nn import Conv1d, Linear, ReLU, Sequential, Softmax

from reinforcement_learning import PpoPolicy, PpoPolicyOutput
from trading_bot.environments.trading_environment_state import TradingEnvironmentState


class TradingPpoPolicy(PpoPolicy):
    _device: device = device('cuda') if torch.cuda.is_available() else device('cpu')
    _higher_interval_candlestick_data_conv1d_out_channels: int = 100
    _lower_interval_candlestick_data_conv1d_out_channels: int = 100
    _trading_environment_state_linear_out_features: int = 100
    _higher_interval_candlestick_data_layers: Sequential
    _lower_interval_candlestick_data_layers: Sequential
    _trading_environment_state_layers: Sequential
    _actor: Sequential
    _critic: Sequential

    def __init__(self) -> None:
        super().__init__()
        self._higher_interval_candlestick_data_layers = Sequential(
            Conv1d(
                in_channels=5, 
                out_channels=self._higher_interval_candlestick_data_conv1d_out_channels, 
                kernel_size=20
            ),
            ReLU()
        )
        self._lower_interval_candlestick_data_layers = Sequential(
            Conv1d(
                in_channels=5,
                out_channels=self._lower_interval_candlestick_data_conv1d_out_channels,
                kernel_size=200
            ),
            ReLU()
        )
        self._trading_environment_state_layers = Sequential(
            Linear(
                in_features=(
                    self._higher_interval_candlestick_data_conv1d_out_channels +
                    self._lower_interval_candlestick_data_conv1d_out_channels +
                    3
                ),
                out_features=self._trading_environment_state_linear_out_features
            ),
            ReLU()
        )
        self._actor = Sequential(
            Linear(in_features=self._trading_environment_state_linear_out_features, out_features=50),
            ReLU(),
            Linear(in_features=50, out_features=3),
            Softmax(dim=-1)
        )
        self._critic = Sequential(
            Linear(in_features=self._trading_environment_state_linear_out_features, out_features=50),
            ReLU(),
            Linear(in_features=50, out_features=1)
        )
        self.to(self._device)

    def forward(self, environment_states: list[TradingEnvironmentState]) -> PpoPolicyOutput:
        shared_features: Tensor = torch.stack([self._get_shared_features(x) for x in environment_states])
        return PpoPolicyOutput(
            action_probabilities=self._actor(shared_features),
            state_values=self._critic(shared_features)
        )

    def get_device(self) -> device:
        return self._device

    def _get_shared_features(self, environment_state: TradingEnvironmentState) -> Tensor:
        higher_interval_candlestick_data_features: Tensor = self._higher_interval_candlestick_data_layers(
            torch.tensor(
                data=environment_state.higher_interval_candlestick_data.values.T,
                device=self._device,
                dtype=torch.float32
            )
        )
        lower_interval_candlestick_data_features: Tensor = self._lower_interval_candlestick_data_layers(
            torch.tensor(
                data=environment_state.lower_interval_candlestick_data.values.T,
                device=self._device,
                dtype=torch.float32
            )
        )
        trading_environment_state_input_tensor: Tensor = torch.cat(
            [
                higher_interval_candlestick_data_features.squeeze(),
                lower_interval_candlestick_data_features.squeeze(),
                torch.tensor(
                    data=[environment_state.is_position_open],
                    device=self._device,
                    dtype=torch.float32
                ),
                torch.tensor(
                    data=[environment_state.open_position_gain_or_loss],
                    device=self._device,
                    dtype=torch.float32
                ),
                torch.tensor(
                    data=[environment_state.open_position_age],
                    device=self._device,
                    dtype=torch.float32
                )
            ]
        )
        return self._trading_environment_state_layers(trading_environment_state_input_tensor)
