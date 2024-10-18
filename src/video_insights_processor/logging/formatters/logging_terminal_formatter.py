from logging import Formatter, LogRecord


class LoggingTerminalFormatter(Formatter):
    _date_format: str = '%d-%m-%Y %H:%M:%S'
    _main_format: str = '%(asctime)s.%(msecs)03d - [%(context)s] - [%(levelname)s] - [%(name)s] - %(message)s'

    def __init__(self) -> None:
        super().__init__(fmt=self._main_format, datefmt=self._date_format)

    def format(self, record: LogRecord) -> str:
        record.msg = record.msg.replace('"', "'")
        return super().format(record)
