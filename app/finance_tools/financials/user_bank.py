import json
import requests

from collections import defaultdict
from sqlalchemy import func, extract
from datetime import date, datetime, date

from app import database as db
from app.models import Transaction


class UserBankFetcher():
    """Class responsible for fetching and calculating user financial data."""
    @staticmethod
    def _get_sums_by_model(user_id, model, coin_type, procedure=None):
        """
        Returns a tuple (balance, expense, income) for all months and the current month.
        
        If procedure is "investment", returns the net investment contribution.
        """
        today = date.today()

        # General case
        all_months = db.session.query(
            func.coalesce(func.sum(model.value).filter(model.type == "Expense"), 0),
            func.coalesce(func.sum(model.value).filter(model.type == "Income"), 0)
        ).filter(model.user_id == user_id, model.coin_type == coin_type).one()

        current_month = db.session.query(
            func.coalesce(func.sum(model.value).filter(model.type == "Expense"), 0),
            func.coalesce(func.sum(model.value).filter(model.type == "Income"), 0)
        ).filter(
            extract("month", model.date) == today.month,
            extract("year", model.date) == today.year,
            model.user_id == user_id,
            model.coin_type == coin_type
        ).one()

        balance = all_months[1] - all_months[0]
        income = current_month[1]
        expense = current_month[0]

        return balance, expense, income


    @staticmethod
    def get_home_page_data(user_id, user_currencies):
        """
        Aggregates data for the home page: balances, incomes, expenses, and investments.
        Returns a dictionary with formatted string values.
        """
        results = {}
        for currency_info in user_currencies:
            code = currency_info.code
            balance, expense, income = UserBankFetcher._get_sums_by_model(user_id, Transaction, coin_type=code)

            results[code] = {
                "incomes": UserBankFetcher._format_currency(income),
                "expenses": UserBankFetcher._format_currency(expense),
                "balance": UserBankFetcher._format_currency(balance),
                "symbol": currency_info.symbol,
                "name": currency_info.name,
                "icon": currency_info.icon,
            }
        # euro_balance, euro_month_expense, euro_month_income = UserBankFetcher._get_sums_by_model(user_id, Transaction, coin_type='EUR')
        # real_balance, real_month_expense, real_month_income = UserBankFetcher._get_sums_by_model(user_id, Transaction, coin_type='BRL')
        
        # # Format values for display
        # values = {
        #     "real_income": real_month_income,
        #     "euro_income": euro_month_income,
        #     "real_expense": real_month_expense,
        #     "euro_expense": euro_month_expense,
        #     "real_balance": real_balance,
        #     "euro_balance": euro_balance,
        # }

        # for key in values:
        #     values[key] = f"{values[key]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return results


    @staticmethod
    def _format_currency(value):
        """Método auxiliar para centralizar a formatação brasileira"""
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def get_euro_prices():
        """
        Fetches daily EUR-BRL exchange rates and returns the latest price and all prices as JSON.

        Returns:
            latest_price (dict): dict with 'data' (DD/MM) and 'valor_eur_brl'
            json_string (str): JSON string with all daily prices sorted ascending
        """
        daily_prices = []
        added_dates = set()

        currency_pair = "EUR-BRL"
        quantity = 500
        start_date = "20240601"
        end_date = datetime.today().strftime("%Y%m%d")
        url = f"https://economia.awesomeapi.com.br/json/daily/{currency_pair}/{quantity}?start_date={start_date}&end_date={end_date}"

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request error: {response.status_code}")
            return None

        data = response.json()
        for item in data:
            date_str = datetime.fromtimestamp(int(item["timestamp"])).strftime("%Y-%m-%d")
            price = float(item["bid"])
            if date_str not in added_dates:
                daily_prices.append({"data": date_str, "valor_eur_brl": price})
                added_dates.add(date_str)

        daily_prices.sort(key=lambda x: x["data"])
        json_string = json.dumps(daily_prices)

        latest = daily_prices[-1].copy()
        latest["data"] = datetime.strptime(latest["data"], "%Y-%m-%d").strftime("%d/%m")
        return latest, json_string


    @staticmethod
    def get_expenses_by_category(user_id, model, coin_type):
        """
        Returns a JSON string with expenses grouped by category and month.

        Returns:
            months_set (list): list of month strings (MM/YY)
            json_string (str): JSON string with category-wise amounts per month
        """
        query = (
            db.session.query(
                model.category,
                extract("year", model.date).label("year"),
                extract("month", model.date).label("month"),
                func.sum(model.value).label("amount")
            )
            .filter(model.type == "Expense", model.user_id == user_id, model.coin_type == coin_type)
            .group_by("year", "month", model.category)
            .order_by("year", "month")
        ).all()

        months_set = set()
        results = defaultdict(dict)
        for category, year, month, amount in query:
            if category != "Without":
                month_str = f"{int(month):02d}/{str(int(year))[-2:]}"
                results[month_str][category] = float(amount)
                months_set.add(month_str)

        months_set = sorted(months_set, key=lambda x: (int("20" + x.split("/")[1]), int(x.split("/")[0])))
        return months_set, json.dumps(results)


    @staticmethod
    def get_monthly_incomes_and_expenses(user_id, model, coin_type):
        """
        Returns monthly income and expenses along with balance and cumulative balance.
        """
        query = (
            db.session.query(
                extract("year", model.date).label("year"),
                extract("month", model.date).label("month"),
                model.type, # Removido Transaction.type para usar o model passado
                func.sum(model.value).label("amount")
            )
            .filter(model.user_id == user_id, model.coin_type == coin_type)
            # REMOVIDO model.category do group_by para somar TUDO do mês
            .group_by("year", "month", model.type) 
            .order_by("year", "month")
        ).all()

        # defaultdict de float para facilitar a soma
        results = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        for year, month, type_, amount in query:
            month_str = f"{int(month):02d}/{str(int(year))[-2:]}"
            # USANDO += em vez de = para garantir que valores sejam somados
            results[int(year)][month_str][type_] += float(amount)

        clean_results = {}
        cumulative_balance = 0
        years = sorted(list(results.keys())) # Lista de anos ordenada
        
        for year in years:
            months_data = results[year]
            clean_results[year] = {}
            for month, data in sorted(months_data.items()):
                income = data.get("Income", 0.0)
                expense = data.get("Expense", 0.0)
                balance = income - expense
                cumulative_balance += balance
                
                clean_results[year][month] = {
                    "Income": round(income, 2),
                    "Expense": round(expense, 2),
                    "Balance": round(balance, 2),
                    "Cumulative_Balance": round(cumulative_balance, 2)
                }

        return years, json.dumps(clean_results)

