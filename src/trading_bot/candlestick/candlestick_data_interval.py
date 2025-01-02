from enum import StrEnum


class CandlestickDataInterval(StrEnum):
    five_minutes = '5m'
    fifteen_minutes = '15m'
    thirty_minutes = '30m'
    one_hour = '1h'
    two_hours = '2h'
    four_hours = '4h'
    one_day = '1d'

    def to_seconds(self) -> float:
        mapping: dict[str, float] = {
            '5m': 5 * 60.0,
            '15m': 15 * 60.0,
            '30m': 30 * 60.0,
            '1h': 60 * 60.0,
            '2h': 2 * 60.0 * 60.0,
            '4h': 4 * 60.0 * 60.0,
            '1d': 24 * 60.0 * 60.0
        }
        return mapping[self.value]
