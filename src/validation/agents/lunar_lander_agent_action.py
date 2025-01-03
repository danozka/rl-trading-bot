from enum import IntEnum


class LunarLanderAgentAction(IntEnum):
    do_nothing = 0
    fire_left_orientation_engine = 1
    fire_main_engine = 2
    fire_right_orientation_engine = 3
