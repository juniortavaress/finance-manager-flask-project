import time
import requests
import pandas as pd
from app import database as db
from app.models import Assets, CriptoDatas
from datetime import datetime, date, timedelta


class CriptoPricesFetcher():
    """
    Fetches and stores historical daily crypto prices (BRL) using Binance API.

    Design principles:
    - Batch execution only (daily scheduler)
    - Idempotent (safe to run multiple times)
    - Fetches ONLY missing date ranges
    - Does not decide which tickers to fetch
    """

    API_URL = "https://api.binance.com/api/v3/klines"
    INTERVAL = "1d"
    LIMIT = 1000
    RATE_LIMIT_DELAY = 0.25
   

    @staticmethod
    def run_api_cripto_history_prices_brl(tickers):
        """
        Fetch and persist historical crypto prices for the given tickers.

        Assumptions:
        - Tickers are valid Binance symbols (e.g. BTCBRL)
        - This method may be executed repeatedly (idempotent)

        Parameters:
        - tickers (list[str]): list of crypto symbols to update
        """
        for symbol in tickers:
            CriptoPricesFetcher._process_symbol(symbol)


    @staticmethod
    def _process_symbol(symbol):
        """
        Processes a single crypto symbol by:
        - Determining required historical ranges
        - Fetching missing candles from Binance
        - Persisting normalized price data
        """
        assets = Assets.query.filter_by(company=symbol).all()
        if not assets:
            return

        asset_start_date = min(a.start_date for a in assets if a.start_date is not None)
        
        prices = (CriptoDatas.query.filter_by(coin=symbol[:-3], currency=symbol[-3:]).order_by(CriptoDatas.date.asc()).all())
        first_price_date = prices[0].date if prices else None
        last_price_date = prices[-1].date if prices else None

        missing_ranges = CriptoPricesFetcher._compute_missing_ranges(asset_start_date, first_price_date, last_price_date)

        for start_dt, end_dt in missing_ranges:
            candles = CriptoPricesFetcher._fetch_binance_candles(symbol, start_dt, end_dt)
            if not candles:
                continue

            df = CriptoPricesFetcher._normalize_dataframe(symbol, candles)
            CriptoPricesFetcher._persist_prices(df)


    @staticmethod
    def _compute_missing_ranges(asset_start, first_price, last_price):
        """
        Determines which date ranges are missing in the database.

        Rules:
        - If no prices exist → fetch from asset_start to today
        - If prices start after asset_start → fetch backward
        - If prices end before today → fetch forward
        """

        today = date.today()
        ranges = []

        if not first_price:
            ranges.append((asset_start, today))
            return ranges

        if asset_start < first_price:
            ranges.append((asset_start, first_price - timedelta(days=1)))

        if last_price < today:
            ranges.append((last_price + timedelta(days=1), today))

        return ranges
    

    # --------------------------------------------------
    # Binance API
    # --------------------------------------------------
    @staticmethod
    def _fetch_binance_candles(symbol, start_date, end_date):
        """
        Fetches candles from Binance for a given date range.
        """

        start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        end_ts = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)

        all_candles = []

        while True:
            params = {
                "symbol": symbol,
                "interval": CriptoPricesFetcher.INTERVAL,
                "limit": CriptoPricesFetcher.LIMIT,
                "startTime": start_ts,
                "endTime": end_ts,
            }

            response = requests.get(CriptoPricesFetcher.API_URL, params=params, timeout=15)
            data = response.json()

            # Binance error or empty payload
            if not data or isinstance(data, dict):
                break

            all_candles.extend(data)

            last_open_time = data[-1][0]
            start_ts = last_open_time + 1

            if len(data) < CriptoPricesFetcher.LIMIT:
                break

            time.sleep(CriptoPricesFetcher.RATE_LIMIT_DELAY)
        return all_candles


    @staticmethod
    def _normalize_dataframe(symbol, candles):
        """
        Converts raw Binance candles into normalized price records.
        """

        df = pd.DataFrame(
            candles,
            columns=[
                "open_time", "open", "high", "low", "close",
                "volume", "close_time", "quote_volume",
                "num_trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ]
        )

        df = df[["open_time", "close"]].copy()
        df["price"] = df["close"].astype(float)
        df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.date
        df["coin"] = symbol[:-3]
        df["currency"] = symbol[-3:]
        return df[["date", "coin", "currency", "price"]]


    @staticmethod
    def _persist_prices(df):
        """
        Persists normalized crypto prices into the database.
        """

        for _, row in df.iterrows():
            db.session.query(CriptoDatas).filter_by(
                coin=row["coin"],
                currency=row["currency"],
                date=row["date"]
            ).delete()

            db.session.add(
                CriptoDatas(
                    date=row["date"],
                    coin=row["coin"],
                    currency=row["currency"],
                    current_price=row["price"]
                )
            )
        db.session.commit()