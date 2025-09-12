import requests
from datetime import datetime
from app import database as db
from app.models import CompanyDatas

class CompanyPrices():
    def run_api_company_history_prices(assets):
        print('\n\n==================================')
        print('Load Company Current Datas')
        for asset in assets:
            ticker = asset.company
            last_entry = (CompanyDatas.query.filter_by(company=ticker).order_by(CompanyDatas.date.desc()).first())
            
            if last_entry:
                days_diff = (datetime.today().date() - last_entry.date).days
                search = days_diff > 2  # True se último registro tem mais de 2 dias
            else:
                search = True

            print(f'{ticker}: {search}')

            if search:
                data = False
                # Requesting data from Alpha Vantage API
                try:
                    api_key = "XXLAA77N45E5YG4S"
                    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}.SAO&apikey={api_key}'
                    r = requests.get(url)
                    data = r.json()
                except:
                    print("Company doesnt exist")

                if "Weekly Time Series" not in data:
                    print(f"API não retornou dados para {ticker}")
                    continue

                if data:
                    time_series = data["Weekly Time Series"]
                    for date_str, values in time_series.items():
                        close_price = float(values['4. close'])
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                        exists = CompanyDatas.query.filter_by(company=ticker, date=date_obj).first()
                        if not exists:
                            new_record = CompanyDatas(
                                date=date_obj,
                                company=ticker,
                                current_price=close_price
                            )
                            db.session.add(new_record)
                    db.session.commit()
        print('==================================\n\n')
