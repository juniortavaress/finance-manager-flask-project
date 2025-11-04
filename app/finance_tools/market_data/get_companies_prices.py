import os 
import requests
from datetime import datetime, date, timedelta
from app import database as db
from app.models import CompanyDatas
from app.models import PersonalTradeStatement

class CompanyPricesFetcher():
    @staticmethod
    def run_api_company_history_prices(assets):
        """
        Updates historical company prices using the Alpha Vantage API.
        Only fetches data if the latest entry is older than 2 days.
        """
        print("Updating company prices database...")
        updated_any = False
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "XXLAA77N45E5YG4S")  # Ideal: usar variável de ambiente

        for asset in assets:
            # print(asset)
            ticker = asset.company

            trade = PersonalTradeStatement.query.filter_by(ticker=asset.company).first()
            brokerage = trade.brokerage.lower() if trade and trade.brokerage else ""
            is_foreign = "nomad" in brokerage
            # print(brokerage)
            # print(is_foreign)
            ticker_symbol = f"{ticker}.SAO" if not is_foreign else ticker

            # if is_foreign:
            # Get the latest entry
            last_entry = CompanyDatas.query.filter_by(company=ticker).order_by(CompanyDatas.date.desc()).first()
            last_date = last_entry.date if last_entry else None

            # If last date is from current week but not Friday or today, delete it
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

            # Prepare API request
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker_symbol}&apikey={api_key}"

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
                if not time_series:
                    print(f"Time Series Error for {ticker_symbol}")
                    continue

                new_records = []

                # Process each weekly entry
                cutoff_date = last_date if last_date else asset.start_date
                for date_str, values in time_series.items():
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        if date_obj < cutoff_date:
                            continue
                        
                        exists = CompanyDatas.query.filter_by(company=ticker, date=date_obj).first()
                        if not exists:
                            new_records.append(CompanyDatas(
                                date=date_obj,
                                company=ticker,
                                current_price=float(values['4. close'])
                            ))
                    except (ValueError, KeyError):
                        continue  

                # Save new records to the database
                if new_records:
                    db.session.add_all(new_records)
                    db.session.commit()
                    updated_any = True
                        
        return updated_any

