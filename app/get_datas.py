from datetime import date, timedelta, datetime, date
import pandas as pd
import json
import requests
from collections import defaultdict
from app import database as db
from sqlalchemy import func, extract
from app.models import Transaction, Contribution, EuroIncomesAndExpenses, RealIncomesAndExpenses, CompanyDatas

class GetDatas():
# Home User Page
    def get_sums(model, user_id, procedure=None):
        """Retorna tupla (expense_sum, income_sum) de todos os meses e do mês atual"""
        today = date.today()

        if procedure == "investment":
            investments_contribuition = db.session.query(
                func.coalesce(func.sum(Contribution.amount).filter(Contribution.type == "Expense"), 0),
                func.coalesce(func.sum(Contribution.amount).filter(Contribution.type == "Income").filter(Contribution.description != "Rendimentos "), 0)
            ).filter(Contribution.user_id == user_id).one()
            investments_contribuition_value = investments_contribuition[0] - investments_contribuition[1]
            return investments_contribuition_value
            
        else: 
            all_months = db.session.query(
                func.coalesce(func.sum(model.amount).filter(model.type == "Expense"), 0),
                func.coalesce(func.sum(model.amount).filter(model.type == "Income"), 0)
            ).filter(model.user_id == user_id).one()

            current_month = db.session.query(
                func.coalesce(func.sum(model.amount).filter(model.type == "Expense"), 0),
                func.coalesce(func.sum(model.amount).filter(model.type == "Income"), 0)
            ).filter(
                extract("month", model.date) == today.month,
                extract("year", model.date) == today.year
            ).filter(model.user_id == user_id).one()

            balance = all_months[1] - all_months[0]
            income = current_month[1]
            expense = current_month[0]
            return balance, expense, income


    def get_datas_home_page(user_id):
        # Euro data
        euro_balance, euro_month_expense, euro_month_income = GetDatas.get_sums(EuroIncomesAndExpenses, user_id)
        # Real data
        real_balance, real_month_expense, real_month_income = GetDatas.get_sums(RealIncomesAndExpenses, user_id)
        # Investment data
        investments_contribuition_value = GetDatas.get_sums(Contribution, user_id, "investment")

        # Formated Values
        values = {
            "real_income": real_month_income,
            "euro_income": euro_month_income,
            "real_expense": real_month_expense,
            "euro_expense": euro_month_expense,
            "real_balance": real_balance,
            "euro_balance": euro_balance,
            "investment_contribuition": investments_contribuition_value
        }

        for key in values:
            values[key] = f"{values[key]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return values


# Euro Page
    def get_euro_prices():
        """
        Fetches the daily EUR-BRL exchange rates and returns the latest price along with a JSON string
        of all daily prices. Only the first price of each day is included. The list is sorted in 
        ascending order by date.

        Returns:
            tuple: (current_price: dict, json_string: str)
                current_price: dict containing 'data' (formatted as DD/MM) and 'valor_eur_brl' (float)
                json_string: JSON string of all daily prices in ascending date order
        """
        daily_prices = []
        added_dates = set()  # Track dates already added

        currency_pair = 'EUR-BRL'
        quantity = 500
        start_date = '20240601'
        end_date = datetime.today().strftime('%Y%m%d')
        url = f'https://economia.awesomeapi.com.br/json/daily/{currency_pair}/{quantity}?start_date={start_date}&end_date={end_date}'

        response = requests.get(url)

        if response.status_code != 200:
            print(f"Request error: {response.status_code}")
            return None

        data = response.json()
        for item in data:
            timestamp = int(item['timestamp'])
            date_obj = datetime.fromtimestamp(timestamp)
            date_str = date_obj.strftime('%Y-%m-%d')
            price = float(item['bid'])

            # Add only the first price of each day
            if date_str not in added_dates:
                daily_prices.append({"data": date_str, "valor_eur_brl": price})
                added_dates.add(date_str)

        # Sort by date ascending
        daily_prices.sort(key=lambda x: x['data'])
        json_string = json.dumps(daily_prices)

        # Get the latest price and format date as DD/MM
        latest = daily_prices[-1].copy()
        latest["data"] = datetime.strptime(latest["data"], "%Y-%m-%d").strftime("%d/%m")

        return latest, json_string


    def load_datas_by_category(user_id):
        query = (
            db.session.query(
                EuroIncomesAndExpenses.category,
                extract('year', EuroIncomesAndExpenses.date).label('year'),
                extract('month', EuroIncomesAndExpenses.date).label('month'),
                func.sum(EuroIncomesAndExpenses.amount).label('amount')
            )
            .filter(EuroIncomesAndExpenses.type == "Expense")
            .group_by('year', 'month', EuroIncomesAndExpenses.category)
            .order_by('year', 'month')
        ).filter(EuroIncomesAndExpenses.user_id == user_id).all()

        months_set = set()
        results = defaultdict(dict)

        for category, year, month, amount in query:
            if category != "Without":
                month_str = f"{int(month):02d}/{str(int(year))[-2:]}"
                results[month_str][category] = float(amount)
                months_set.add(month_str)
            
        months_set = sorted(months_set, key=lambda x: (int('20'+x.split('/')[1]), int(x.split('/')[0])))
        
        return months_set, json.dumps(results)
    

    def load_datas_incomes_and_expenses(model, user_id):
        year_expr = extract('year', model.date)
        month_expr = extract('month', model.date)

        query = (
            db.session.query(
                model.type,
                year_expr.label('year'),
                month_expr.label('month'),
                func.sum(model.amount).label('amount')
            )
            .group_by(year_expr, month_expr, model.type)
            .order_by(year_expr, month_expr)
        ).filter(model.user_id == user_id).all()

        results = defaultdict(lambda: defaultdict(dict))
        for type, year, month, amount in query:
            month_str = f"{int(month):02d}/{str(int(year))[-2:]}"
            results[int(year)][month_str][type] = float(amount)

        clean_results = {}
        cumulative_balance = 0
        years = set()
        for year, months in results.items():
            clean_results[year] = {}
            years.add(year)
            for month, data in sorted(months.items()):  # garante ordem dos meses
                income = data.get("Income", 0.0)
                expense = data.get("Expense", 0.0)
                balance = income - expense
                cumulative_balance += balance

                clean_results[year][month] = {
                    "Income": income,
                    "Expense": expense,
                    "Balance": balance,
                    "Cumulative_Balance": cumulative_balance}
                
        return years, json.dumps(clean_results)

        


    def load_datas_page_real2():




        # Carregando o primeiro DataFrame
        df = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Entrada_Saida_Real')
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df['data'] = pd.to_datetime(df['data'])
        df['ano'] = df['data'].dt.year.astype(str)
        df['mes'] = df['data'].dt.strftime('%b')

        # Carregando o segundo DataFrame
        df2 = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Investido')
        df2.columns = [col.strip().lower().replace(' ', '_') for col in df2.columns]
        df2['data'] = pd.to_datetime(df2['data'])
        df2['ano'] = df2['data'].dt.year.astype(str)
        df2['mes'] = df2['data'].dt.strftime('%b')

        # Dicionário final
        dados_por_ano = defaultdict(dict)

        # Acumuladores globais
        acumulado = 0

        # Processando df (Entrada_Saida_Real)
        for _, row in df.iterrows():
            ano = row['ano']
            mes = row['mes']
            if mes not in dados_por_ano[ano]:
                dados_por_ano[ano][mes] = {}

            dados_por_ano[ano][mes]['entrada'] = round(row['entrada'], 2)       
            dados_por_ano[ano][mes]['saida'] = round(row['saida'], 2)           
            dados_por_ano[ano][mes]['saldo'] = round(row['saldo'], 2)           
            acumulado += row['saldo']                                           
            dados_por_ano[ano][mes]['saldo_acumulado'] = round(acumulado, 2)    
            # dados_por_ano[ano][mes]['entrada'] = round(row['entrada'], 2)       /10
            # dados_por_ano[ano][mes]['saida'] = round(row['saida'], 2)           /10
            # dados_por_ano[ano][mes]['saldo'] = round(row['saldo'], 2)           /10
            # acumulado += row['saldo']                                           /10
            # dados_por_ano[ano][mes]['saldo_acumulado'] = round(acumulado, 2)    /10

        # Processando df2 (Investido)
        for _, row in df2.iterrows():
            ano = row['ano']
            mes = row['mes']
            if mes not in dados_por_ano[ano]:
                dados_por_ano[ano][mes] = {}

            dados_por_ano[ano][mes]['aportes investimentos'] = round(row['aportes'], 2) 
            dados_por_ano[ano][mes]['total investido'] = round(row['investido'], 2)     
            dados_por_ano[ano][mes]['lucro investimentos'] = round(row['lucro'], 2)     
            # dados_por_ano[ano][mes]['aportes investimentos'] = round(row['aportes'], 2) /10
            # dados_por_ano[ano][mes]['total investido'] = round(row['investido'], 2)     /10
            # dados_por_ano[ano][mes]['lucro investimentos'] = round(row['lucro'], 2)     /10

        # Garantir que todos os campos existam em todos os meses
        campos_esperados = [
            'entrada',
            'saida',
            'saldo',
            'saldo_acumulado',
            'aportes investimentos',
            'total investido',
            'lucro investimentos'
        ]

        for ano in dados_por_ano:
            for mes in dados_por_ano[ano]:
                for campo in campos_esperados:
                    if campo not in dados_por_ano[ano][mes]:
                        dados_por_ano[ano][mes][campo] = 0.0  # ou None, se preferir

        # Ordenar meses corretamente
        meses_ordem = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        dados_ordenados = {}
        for ano, meses in dados_por_ano.items():
            dados_ordenados[ano] = {mes: meses[mes] for mes in meses_ordem if mes in meses}
        dados_ordenados = dict(dados_ordenados)


        return dados_ordenados



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
