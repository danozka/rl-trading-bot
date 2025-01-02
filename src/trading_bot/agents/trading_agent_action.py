from enum import IntEnum


class TradingAgentAction(IntEnum):
    do_nothing = 0
    open_position = 1
    close_position = 2
