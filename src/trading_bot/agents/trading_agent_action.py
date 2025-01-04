from enum import IntEnum


class TradingAgentAction(IntEnum):
    do_nothing = 0
    open_long_position = 1
    close_long_position = 2
