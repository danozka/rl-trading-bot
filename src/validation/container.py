from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton

from reinforcement_learning import IPpoPoliciesPersistence
from validation import use_cases
from validation.policies.lunar_lander_ppo_policies_persistence import LunarLanderPpoPoliciesPersistence


class Container(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(packages=[use_cases])
    ppo_policies_persistence: Singleton[IPpoPoliciesPersistence] = Singleton(LunarLanderPpoPoliciesPersistence)
