import re 
from app import database as db
from app.models import UserTradeSummary, User
from datetime import date, timedelta


class UpdateFixedIncomesDatabases:
    def atualize_fixed_income(user_id, trade=None):
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

        # Aplica a operação do trade
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


    def update_fixed_income_daily():
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
        try:
            match = re.search(r"([\d.,]+)%", ticker)
            annual_rate = float(match.group(1).replace(",", ".")) / 100 if match else 0.0
            daily_tax = (1 + annual_rate) ** (1 / 365) - 1 
        except:
            daily_tax = 0
        return daily_tax
    

