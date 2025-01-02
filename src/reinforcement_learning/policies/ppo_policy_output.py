from dataclasses import dataclass

from torch import Tensor


@dataclass
class PpoPolicyOutput:
    action_probabilities: Tensor
    state_values: Tensor
