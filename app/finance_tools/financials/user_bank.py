import json
import requests
from collections import defaultdict
from sqlalchemy import func, extract
from datetime import date, datetime, date
from app import database as db
from app.models import Transaction

class UserBankFetcher():
    """
    Service class for fetching, aggregating, and formatting 
    user financial data, including transactions and exchange rates.
    """

    @staticmethod
    def _get_sums_by_model(user_id, model, coin_type, procedure=None):
        """
        Calculates financial summaries (balance, expenses, incomes).
        
        Returns a tuple (total_balance, current_month_expense, current_month_income).
        The balance is calculated across all history, while income/expenses 
        refer to the current calendar month.
        """
        today = date.today()

        # Query total expenses and incomes for all time to calculate balance
        all_months = db.session.query(
            func.coalesce(func.sum(model.value).filter(model.type == "Expense"), 0),
            func.coalesce(func.sum(model.value).filter(model.type == "Income"), 0)
        ).filter(model.user_id == user_id, model.coin_type == coin_type).one()

        # Query expenses and incomes specifically for the current month and year
        current_month = db.session.query(
            func.coalesce(func.sum(model.value).filter(model.type == "Expense"), 0),
            func.coalesce(func.sum(model.value).filter(model.type == "Income"), 0)
        ).filter(
            extract("month", model.date) == today.month,
            extract("year", model.date) == today.year,
            model.user_id == user_id,
            model.coin_type == coin_type
        ).one()

        # Balance is the historical difference between all incomes and expenses
        balance = all_months[1] - all_months[0]
        income = current_month[1]
        expense = current_month[0]

        return balance, expense, income


    @staticmethod
    def get_home_page_data(user_id, user_currencies):
        """
        Aggregates financial data for all currencies associated with a user.
        
        Returns a dictionary where each key is a currency code containing 
        formatted values for the home page dashboard.
        """
        results = {}
        for currency_info in user_currencies:
            code = currency_info.code
            # Fetch raw numeric data for the specific currency
            balance, expense, income = UserBankFetcher._get_sums_by_model(
                user_id, Transaction, coin_type=code
            )

            # Map results with formatted strings and currency metadata
            results[code] = {
                "incomes": UserBankFetcher._format_currency(income),
                "expenses": UserBankFetcher._format_currency(expense),
                "balance": UserBankFetcher._format_currency(balance),
                "symbol": currency_info.symbol,
                "name": currency_info.name,
                "icon": currency_info.icon,
            }
        return results


    @staticmethod
    def _format_currency(value):
        """
        Helper method to format floats into Brazilian Real (BRL) currency strings.
        Example: 1500.5 -> "1.500,50"
        """
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


    @staticmethod
    def get_coin_prices(coin="EUR"):
        """
        Fetches historical daily exchange rates for a given coin against BRL.
        
        Uses the AwesomeAPI to retrieve up to 500 daily records starting 
        from June 2024. Returns a JSON string of date/price pairs.
        """
        daily_prices = []
        added_dates = set()

        currency_pair = f"{coin}-BRL"
        quantity = 500
        start_date = "20240601"
        end_date = datetime.today().strftime("%Y%m%d")
        url = (f"https://economia.awesomeapi.com.br/json/daily/"
               f"{currency_pair}/{quantity}?start_date={start_date}&end_date={end_date}")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request error: {response.status_code}")
            return None

        data = response.json()
        for item in data:
            # Convert Unix timestamp to YYYY-MM-DD string
            date_str = datetime.fromtimestamp(int(item["timestamp"])).strftime("%Y-%m-%d")
            price = float(item["bid"])
            if date_str not in added_dates:
                daily_prices.append({"data": date_str, f"valor_{coin.lower()}_brl": price})
                added_dates.add(date_str)

        # Ensure the data is returned in chronological order
        daily_prices.sort(key=lambda x: x["data"])
        return json.dumps(daily_prices)


    @staticmethod
    def get_expenses_by_category(user_id, model, coin_type):
        """
        Groups expenses by category and month for chart visualization.
        
        Returns:
            months_set (list): Sorted chronological list of MM/YY strings.
            json_string (str): JSON object mapped as {month: {category: amount}}.
        """
        query = (
            db.session.query(
                model.category,
                extract("year", model.date).label("year"),
                extract("month", model.date).label("month"),
                func.sum(model.value).label("amount")
            )
            .filter(model.type == "Expense", 
                    model.user_id == user_id, 
                    model.coin_type == coin_type)
            .group_by("year", "month", model.category)
            .order_by("year", "month")
        ).all()

        months_set = set()
        results = defaultdict(dict)
        for category, year, month, amount in query:
            # Skip uncategorized entries if labeled as "Without"
            if category != "Without":
                month_str = f"{int(month):02d}/{str(int(year))[-2:]}"
                results[month_str][category] = float(amount)
                months_set.add(month_str)

        # Sort months chronologically considering year and then month
        months_set = sorted(
            months_set, 
            key=lambda x: (int("20" + x.split("/")[1]), int(x.split("/")[0]))
        )
        return months_set, json.dumps(results)


    @staticmethod
    def get_monthly_incomes_and_expenses(user_id, model, coin_type):
        """
        Calculates monthly cash flow including cumulative balance over time.
        
        Returns:
            years (list): Sorted list of years present in the data.
            json_string (str): Nested data grouped by year and month.
        """
        query = (
            db.session.query(
                extract("year", model.date).label("year"),
                extract("month", model.date).label("month"),
                model.type,
                func.sum(model.value).label("amount")
            )
            .filter(model.user_id == user_id, model.coin_type == coin_type)
            .group_by("year", "month", model.type)
            .order_by("year", "month")
        ).all()

        # Group data in a multi-level dictionary
        results = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        for year, month, type_, amount in query:
            month_str = f"{int(month):02d}/{str(int(year))[-2:]}"
            results[int(year)][month_str][type_] += float(amount)

        clean_results = {}
        cumulative_balance = 0
        years = sorted(list(results.keys()))
        
        for year in years:
            months_data = results[year]
            clean_results[year] = {}
            for month, data in sorted(months_data.items()):
                income = data.get("Income", 0.0)
                expense = data.get("Expense", 0.0)
                monthly_balance = income - expense
                cumulative_balance += monthly_balance
                
                # Format final values rounded to 2 decimal places
                clean_results[year][month] = {
                    "Income": round(income, 2),
                    "Expense": round(expense, 2),
                    "Balance": round(monthly_balance, 2),
                    "Cumulative_Balance": round(cumulative_balance, 2)
                }

        return years, json.dumps(clean_results)
    