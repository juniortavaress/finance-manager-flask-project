import re 
from app import database as db
from datetime import date, timedelta
from app.models import UserTradeSummary, User


class UpdateFixedIncomesDatabases:
    """
    Handles persistence and daily valuation of fixed income investments.

    This module is responsible for:
    - Applying fixed income trades (buy/sell) and rebuilding summaries
    - Performing daily accrual updates based on implicit interest rates
    - Ensuring time-series consistency for fixed income assets
    """
        
    @staticmethod
    def atualize_fixed_income(user_id, trade=None):
        """
        Rebuilds fixed income summaries starting from a specific trade date.

        This method:
        - Applies the trade operation (buy or sell)
        - Removes existing summaries from the trade date onward
        - Recreates daily summaries up to today using daily compound interest
        """
        ticker = trade.ticker
        brokerage = trade.brokerage
        investment_type = trade.investment_type
        tax = UpdateFixedIncomesDatabases._get_daily_tax(ticker)

        start_date = trade.date
        today = date.today()
        
        previous = db.session.query(UserTradeSummary).filter(
            UserTradeSummary.user_id == user_id,
            UserTradeSummary.company == ticker,
            UserTradeSummary.date <= start_date
        ).order_by(UserTradeSummary.date.desc()).first()
        
        if not previous:
            quantity = 0
            avg_price = 0
            current_value = 0
        else:
            quantity = previous.quantity
            avg_price = previous.avg_price
            current_value = previous.current_price

        if trade.operation == "B": 
            quantity += trade.quantity
            avg_price += trade.final_value
            current_value += trade.final_value
        else:  
            quantity -= trade.quantity
            
        db.session.query(UserTradeSummary).filter(
            UserTradeSummary.user_id == user_id,
            UserTradeSummary.company == ticker,
            UserTradeSummary.date >= start_date
        ).delete()

        first_day = True
        current_date = start_date
        while current_date <= today:
            if first_day:
                first_day = False
            else:
                current_value *= (1 + tax)
    
            new_entry = UserTradeSummary(
                user_id=user_id,
                brokerage=brokerage,
                investment_type=investment_type,
                date=current_date,
                company=ticker,
                quantity=quantity,
                current_price=round(current_value, 2),
                avg_price=avg_price,
                dividend=0
            )
            db.session.add(new_entry)

            current_date += timedelta(days=1)
        db.session.commit()


    @staticmethod
    def update_fixed_income_daily():
        """
        Performs daily accrual updates for all fixed income assets.

        This method:
        - Iterates through all users
        - Identifies fixed income assets
        - Applies one day of compound interest if today's summary is missing
        """
        today = date.today()
        users = db.session.query(User).all()

        for user in users:
            tickers = db.session.query(UserTradeSummary.company).filter_by(user_id=user.id, investment_type='fixed_income').distinct()

            for ticker_row in tickers:
                ticker = ticker_row.company

                last_summary = db.session.query(UserTradeSummary)\
                    .filter_by(user_id=user.id, company=ticker, investment_type='fixed_income')\
                    .order_by(UserTradeSummary.date.desc())\
                    .first()

                if not last_summary or last_summary.quantity == 0 or last_summary.date == today:
                    continue

                daily_tax = UpdateFixedIncomesDatabases._get_daily_tax(ticker)
                updated_value = last_summary.current_price * (1 + daily_tax)

                new_summary = UserTradeSummary(
                    user_id=user.id,
                    brokerage=last_summary.brokerage,
                    investment_type='fixed_income',
                    company=ticker,
                    date=today,
                    quantity=last_summary.quantity,
                    current_price=round(updated_value, 2),
                    avg_price=last_summary.avg_price,
                    dividend=last_summary.dividend
                )

                db.session.add(new_summary)
        db.session.commit()
        

    @staticmethod
    def _get_daily_tax(ticker):
        """
        Extracts the annual interest rate from the ticker string and
        converts it into a daily compound rate.

        Expected ticker format:
            "... 12.5% ..." → annual rate = 12.5%

        Returns:
            float: Daily compound interest rate
        """
        try:
            match = re.search(r"([\d.,]+)%", ticker)
            annual_rate = float(match.group(1).replace(",", ".")) / 100 if match else 0.0
            daily_tax = (1 + annual_rate) ** (1 / 365) - 1 
        except:
            daily_tax = 0
        return daily_tax
    

