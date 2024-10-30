import logging
import time
from datetime import datetime, timedelta, timezone
from logging import Logger

import pandas as pd
from httpx import Client, RequestError, Response
from pandas import DataFrame

from rl_trading_bot.domain.candlestick_data_interval import CandlestickDataInterval
from rl_trading_bot.services.i_candlestick_data_repository import ICandlestickDataRepository


class BinanceCandlestickDataRepository(ICandlestickDataRepository):
    _log: Logger = logging.getLogger(__name__)
    _url_template: str = (
        'https://api.binance.com/api/v3/klines?'
        'symbol={base_asset}{quote_asset}&'
        'interval={interval}&'
        'endTime={end_timestamp}&'
        'limit=1000'
    )
    _http_client: Client
    _sleep_seconds_between_request_failures: float

    def __init__(
        self,
        http_client: Client = Client(),
        sleep_seconds_between_request_failures: float = 1.0
    ) -> None:
        self._http_client = http_client
        self._sleep_seconds_between_request_failures = sleep_seconds_between_request_failures

    def get_symbol_candlestick_data(
        self,
        base_asset: str,
        quote_asset: str, 
        interval: CandlestickDataInterval
    ) -> DataFrame:
        self._log.debug(
            f'Getting candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and interval '
            f'\'{interval}\'...'
        )
        data: DataFrame = DataFrame()
        start_datetime: datetime = datetime.now(timezone.utc)
        end_datetime: datetime = datetime.now(timezone.utc)
        while True:
            data_chunk: DataFrame = self._get_data_chunk(
                base_asset=base_asset,
                quote_asset=quote_asset,
                interval=interval,
                end_datetime=end_datetime
            )
            data = pd.concat(objs=[data_chunk, data], ignore_index=True)
            data = data.drop_duplicates(subset='open_time', ignore_index=True)
            data = data.sort_values(by='open_time', ascending=True)
            current_start_datetime: datetime = data['open_time'].iloc[0].to_pydatetime()
            if start_datetime != current_start_datetime:
                start_datetime = current_start_datetime
                end_datetime = current_start_datetime
            else:
                break
        result: DataFrame = self._fill_missing_values(data=data, interval_in_seconds=interval.to_seconds())
        self._log.debug(
            f'Candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and interval '
            f'\'{interval}\' retrieved'
        )
        return result

    def _get_data_chunk(
        self,
        base_asset: str,
        quote_asset: str,
        interval: CandlestickDataInterval,
        end_datetime: datetime
    ) -> DataFrame:
        url: str = self._url_template.format(
            base_asset=base_asset,
            quote_asset=quote_asset,
            interval=interval.value,
            end_timestamp=int(datetime.timestamp(end_datetime) * 1000)
        )
        while True:
            try:
                response: Response = self._http_client.get(url)
                response.raise_for_status()
                return self._adapt_message_to_dataframe(response.json())
            except RequestError:
                self._log.error(
                    f'Exception found while downloading data chunk for base asset \'{base_asset}\', quote asset '
                    f'\'{quote_asset}\' and interval \'{interval}\'. Retrying download in '
                    f'{self._sleep_seconds_between_request_failures} seconds...'
                )
                time.sleep(self._sleep_seconds_between_request_failures)

    @staticmethod
    def _adapt_message_to_dataframe(message: list[list[int | str]]) -> DataFrame:
        result: DataFrame = DataFrame()
        result['open_time'] = [datetime.fromtimestamp(x[0] / 1000, tz=timezone.utc) for x in message]
        result['close_time'] = [datetime.fromtimestamp(x[6] / 1000, tz=timezone.utc) for x in message]
        result['open'] = [float(x[1]) for x in message]
        result['close'] = [float(x[4]) for x in message]
        result['high'] = [float(x[2]) for x in message]
        result['low'] = [float(x[3]) for x in message]
        return result

    @staticmethod
    def _fill_missing_values(data: DataFrame, interval_in_seconds: float) -> DataFrame:
        data.set_index(keys='open_time', inplace=True)
        data = data.reindex(
            pd.date_range(
                start=data.index.min(),
                end=data.index.max(),
                freq=timedelta(seconds=interval_in_seconds),
                tz=timezone.utc
            )
        )
        data.ffill(inplace=True)
        data['close_time'] = data.index + pd.Timedelta(seconds=interval_in_seconds)
        data.reset_index(inplace=True)
        data.rename(columns={'index': 'open_time'}, inplace=True)
        return data
