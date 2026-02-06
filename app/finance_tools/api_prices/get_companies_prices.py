import requests
from app import database as db
from datetime import datetime, date, timedelta
from app.models import Assets, CompanyDatas, PersonalTradeStatement


class CompanyPricesFetcher:
    """
    Fetches and stores historical company prices.

    Design principles:
    - Batch execution only
    - Idempotent
    - Fetches ONLY missing date ranges
    - Asset start_date defines minimum required history
    """

    API_URL = "https://www.alphavantage.co/query"
    FUNCTION = "TIME_SERIES_WEEKLY"
    ALPHA_VANTAGE_API_KEY = "XXLAA77N45E5YG4S"


    @staticmethod
    def run_api_company_history_prices(tickers=None):
        """
        Executes a batch update of historical company prices.

        If tickers are provided, only those assets are processed.
        If tickers is None, all assets in the database are updated.

        """
        assets = CompanyPricesFetcher._get_assets(tickers)
        for asset in assets:
            CompanyPricesFetcher._process_asset(asset)

        
    @staticmethod
    def _get_assets(tickers):
        if tickers:
            return Assets.query.filter(Assets.company.in_(tickers)).all()
        return Assets.query.all()


    @staticmethod
    def _process_asset(asset):
        """
        Processes a single asset by:
        - Resolving its correct market symbol
        - Detecting missing historical price ranges
        - Fetching and persisting missing prices
        """
        ticker = asset.company

        # Skip crypto 
        if ticker.endswith("BRL"):
            return

        ticker_symbol = CompanyPricesFetcher._resolve_symbol(asset)

        prices = (CompanyDatas.query.filter_by(company=ticker).order_by(CompanyDatas.date.asc()).all())
        first_price = prices[0].date if prices else None
        last_price = prices[-1].date if prices else None

        missing_ranges = CompanyPricesFetcher._compute_missing_ranges(asset.start_date, first_price, last_price)

        for start_dt, end_dt in missing_ranges:
            CompanyPricesFetcher._fetch_and_persist(ticker, ticker_symbol, start_dt, end_dt)


    @staticmethod
    def _resolve_symbol(asset):
        """
        Resolves the correct market symbol for the asset.

        Rules:
        - Brazilian equities use '.SAO'
        - Foreign equities (e.g. Nomad brokerage) use raw ticker
        """
        ticker = asset.company
        trade = (PersonalTradeStatement.query.filter_by(ticker=ticker).order_by(PersonalTradeStatement.date.asc()).first())
        brokerage = trade.brokerage.lower() if trade and trade.brokerage else ""
        is_foreign = "nomad" in brokerage
        return ticker if is_foreign else f"{ticker}.SAO"


    @staticmethod
    def _compute_missing_ranges(asset_start, first_price, last_price):
        """
        Computes missing date ranges for price history.
        """
        today = date.today()
        ranges = []

        if not first_price:
            return [(asset_start, today)]

        if asset_start < first_price:
            ranges.append((asset_start, first_price))

        if last_price < today:
            ranges.append((last_price - timedelta(days=4), today))

        return ranges


    @staticmethod
    def _fetch_and_persist(ticker, symbol, start_date, end_date):
        """
        Fetches weekly prices from Alpha Vantage and persists them
        as daily forward-filled records.
        """

        api_key = CompanyPricesFetcher.ALPHA_VANTAGE_API_KEY
        params = {"function": CompanyPricesFetcher.FUNCTION, "symbol": symbol, "apikey": api_key}
        response = requests.get(CompanyPricesFetcher.API_URL, params=params, timeout=20)
        data = response.json()

        time_series = data.get("Weekly Time Series")
        if not time_series:
            print("TIME SERIES ERROR: ", symbol)
            return

        weekly_prices = []
        for date_str, values in time_series.items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_obj < start_date:
                    continue

                close_price = float(values["4. close"])
                weekly_prices.append((date_obj, close_price))

            except (ValueError, KeyError):
                continue

        if not weekly_prices:
            return

        weekly_prices.sort(key=lambda x: x[0])

        daily_records = CompanyPricesFetcher._expand_weekly_to_daily(ticker, weekly_prices, start_date, end_date)

        for record in daily_records:
            db.session.query(CompanyDatas).filter_by(
                company=record.company,
                date=record.date
            ).delete()

            db.session.add(record)

        db.session.commit()


    @staticmethod
    def _expand_weekly_to_daily(ticker, weekly_prices, start_date, end_date):
        """
        Expands weekly prices into daily prices using forward-fill.
        """
        daily_records = []

        for i, (current_date, price) in enumerate(weekly_prices):
            next_date = (
                weekly_prices[i + 1][0]
                if i + 1 < len(weekly_prices)
                else end_date
            )

            day = current_date
            while day <= next_date:
                if start_date <= day <= end_date:
                    daily_records.append(
                        CompanyDatas(
                            company=ticker,
                            date=day,
                            current_price=price
                        )
                    )
                day += timedelta(days=1)

        return daily_records
    

