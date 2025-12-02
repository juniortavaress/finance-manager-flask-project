import os 
import pandas as pd 
import requests
from datetime import datetime, date, timedelta
from app import database as db
from app.models import CompanyDatas
from app.models import PersonalTradeStatement, Assets, CriptoDatas, CompanyDatas
import time 

class CompanyPricesFetcher():
    @staticmethod
    def run_api_company_history_prices(unique_tickers=None):
        """
        Updates historical company prices using the Alpha Vantage API.
        Only fetches data if the latest entry is older than 2 days.
        """
        print("Updating company prices database...")
        updated_any = False
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "XXLAA77N45E5YG4S")  # Ideal: usar variável de ambiente

        if not unique_tickers:
            assets = Assets.query.distinct(Assets.company).all()
        else: 
            assets = Assets.query.filter(Assets.company.in_(unique_tickers)).all()

        for asset in assets:
            ticker = asset.company

            trade = PersonalTradeStatement.query.filter_by(ticker=asset.company).first()
            brokerage = trade.brokerage.lower() if trade and trade.brokerage else ""
            is_foreign = "nomad" in brokerage
   
            ticker_symbol = f"{ticker}.SAO" if not is_foreign else ticker

            last_entry = CompanyDatas.query.filter_by(company=ticker).order_by(CompanyDatas.date.desc()).first()
            last_date = last_entry.date if last_entry else None

            search = False
            if last_date:
                if last_date != date.today() and last_date != (date.today() - timedelta(days=1)):
                    if last_date.weekday() != 4:
                        db.session.delete(last_entry)
                        db.session.commit()
                        last_date = None
                    search = True
            else:
                search = True

            # search = True

            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker_symbol}&apikey={api_key}"
            # url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker_symbol}&apikey={api_key}"

            if search:
                try:
                    request = requests.get(url)
                    request.raise_for_status()
                    data = request.json()
                except requests.RequestException:
                    print(f"Requisition Error for {ticker_symbol}")
                    continue

                # Validate API response
                time_series = data.get("Weekly Time Series")
                # print(data)

                # time_series = data.get("Time Series (Daily)")
                
                if not time_series:
                    print(f"Time Series Error for {ticker_symbol}")
                    continue

                new_records = []

                # Process each weekly entry
                cutoff_date = last_date if last_date else asset.start_date
                time_series_dates = []
                for date_str, values in time_series.items():
                    try:
                        # print(f'\n\n\n\n\n\nTIME SERIES ({date_str})\n\n', values)
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        if date_obj < cutoff_date:
                            continue
                        
                        close_price = float(values['4. close'])
                        time_series_dates.append((date_obj, close_price))
                    except (ValueError, KeyError):
                        continue  

                time_series_dates.sort()

                daily_records = []
                if time_series_dates:
                    for i in range(len(time_series_dates)):
                        current_date, current_price = time_series_dates[i]

                        # Próxima data ou hoje (caso última semana)
                        next_date = (time_series_dates[i + 1][0] 
                                    if i + 1 < len(time_series_dates) 
                                    else date.today())

                        # Preenche dias até a próxima data (exclusivo)
                        day = current_date
                        while day <= next_date:
                            exists = CompanyDatas.query.filter_by(company=ticker, date=day).first()
                            if not exists and day >= cutoff_date:
                                daily_records.append(CompanyDatas(
                                    date=day,
                                    company=ticker,
                                    current_price=current_price
                                ))
                            day += timedelta(days=1)

                # Save new records to the database
                if daily_records:
                    db.session.add_all(daily_records)
                    db.session.commit()
                    updated_any = True
                        
        return updated_any




    def run_api_crypto_history_prices_brl(tickers=["BTCBRL"], interval="1d"):
        print("Updating crypto prices database...")
        limit = 1000  # max 
        url = "https://api.binance.com/api/v3/klines"

        for symbol in tickers:
            all_data = []

            print(symbol)
            last_entry = CriptoDatas.query.filter_by(coin=symbol[:len(symbol)-3], currency=symbol[len(symbol)-3:]).order_by(CriptoDatas.date.desc()).first()
            last_date = last_entry.date if last_entry else None

            start_dt = last_date - timedelta(days=1) if last_date else datetime(2023, 1, 1)
            start_dt = datetime.combine(start_dt, datetime.min.time())
            start_ts = int(start_dt.timestamp() * 1000)

            print("start_dt", start_dt)
            while True:
                params = {
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit,
                    "startTime": start_ts
                }

                response = requests.get(url, params=params)
                batch = response.json()

                # print("batch size:", batch)
                if isinstance(batch, dict) and "code" in batch:
                    print("Error Binance:", batch)
                    break

                if not batch:
                    break

                all_data.extend(batch)

                # próximo bloco começa depois da última vela retornada
                last_open_time = batch[-1][0]
                start_ts = last_open_time + 1

                # Evitar rate limit
                time.sleep(0.25)

                print("aqui")
                # Se retornou menos de 1000, acabou o histórico
                if len(batch) < 1000:
                    break

            df = pd.DataFrame(all_data, columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "num_trades", "taker_buy_base", "taker_buy_quote", "ignore"])
            df.drop(columns=["open", "high", "low", "volume", "close_time", "quote_volume", "num_trades", "taker_buy_base", "taker_buy_quote", "ignore"], inplace=True)
            df["close"] = df["close"].astype(float)
            df["coin"] = symbol[:3]
            df["currency"] = symbol[3:]
            df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')

            print(df.tail())
            for _, row in df.iterrows():
                db.session.query(CriptoDatas).filter_by(coin=row["coin"], currency=row["currency"], date=row["open_time"]).delete()
                db.session.add(CriptoDatas(date=row["open_time"], coin=row["coin"], currency=row["currency"], current_price=row["close"]))
            db.session.commit()

