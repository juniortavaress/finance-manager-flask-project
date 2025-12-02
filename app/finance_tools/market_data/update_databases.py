from datetime import date, timedelta
from app import database as db
from app.models import PersonalTradeStatement, Assets, BrokerStatus, User, UserTradeSummary, Contribution
from app.finance_tools.market_data.update_fixed_income_investments import UpdateFixedIncomesDatabases
from app.finance_tools.market_data.update_equity_investiments import UpdateEquityDatabases
from sqlalchemy import func


class UpdateDatabases:
    def atualize_assets_db(user_id, list_tickers):
        """Updates the user's asset records based on current trade quantities."""
        for ticker in list_tickers:
            trades = PersonalTradeStatement.query.filter_by(user_id=user_id, ticker=ticker).all()
            current_qty = sum(t.quantity if t.operation == 'B' else -t.quantity for t in trades)
            asset = Assets.query.filter_by(user_id=user_id, company=ticker).first()
            
            if current_qty > 0:
                first_trade = min(trades, key=lambda t: t.date)
                if not asset:
                    asset = Assets(
                        user_id=user_id,
                        company=ticker,
                        start_date=first_trade.date,
                        current_quantity=current_qty
                    )
                    db.session.add(asset)
                else:
                    if first_trade.date < asset.start_date:
                        asset.start_date = first_trade.date
                    asset.current_quantity = current_qty
                    db.session.add(asset)
            elif current_qty == 0:
                if asset:
                    db.session.delete(asset)
        db.session.commit()


    def atualize_summary(user_id, trades):
        """
        Updates the user trade summary table based on a list of trades.

        For each trade:
        1. Updates the user's cash balance.
        2. Updates the stock summary if the investment is not a fixed income.
        """
        print("atualize_summary")
        print("trades", trades)
        oldest_date = min(trades, key=lambda t: t.date).date
        brokerages = list({t.brokerage for t in trades})

        for trade in trades:    
            print(trade.investment_type)
            # UpdateDatabases._atualize_cash(user_id, trade)
            if trade.investment_type == "fixed_income":
                UpdateFixedIncomesDatabases.atualize_fixed_income(user_id, trade)
            elif trade.investment_type == "stockes" or trade.investment_type == "fixed_income":
                UpdateEquityDatabases.atualize_stockes_trades(user_id, trade)
        UpdateDatabases.update_broker_status(user_id, oldest_date, brokerages)


    def atualize_daily_summary():
        UpdateFixedIncomesDatabases.update_fixed_income_daily()
        UpdateEquityDatabases.update_equities_daily()
        from datetime import datetime
        UpdateDatabases.update_broker_status(target_date=datetime.strptime("2020-11-01", "%Y-%m-%d").date())


    @staticmethod
    def update_broker_status(user_id=None, target_date=None, brokerage=None):

        start_date = target_date if target_date else date.today() - timedelta(days=1)
        users = db.session.query(User).all() if not user_id else [db.session.query(User).get(user_id)]
            
        print(users)

        for user in users:
            if target_date:
                db.session.query(BrokerStatus).filter(
                    BrokerStatus.user_id == user.id,
                    BrokerStatus.date >= target_date
                ).delete()
                db.session.commit()

            brokerages = [br_row.brokerage for br_row in db.session.query(Contribution.brokerage).filter_by(user_id=user.id).distinct()] if not brokerage else brokerage
            
            # print(brokerages)
            for brokerage in brokerages:
                current_date = start_date
                while current_date <= date.today():
                    # print(current_date)
                    summaries = (db.session.query(UserTradeSummary).filter_by(user_id=user.id, brokerage=brokerage, date=current_date).all())
                    total_contributions = (db.session.query(func.sum(Contribution.amount)).filter(Contribution.user_id==user.id, Contribution.brokerage==brokerage, Contribution.date<=current_date).scalar()) or 0
                    buy_operations = (db.session.query(func.sum(PersonalTradeStatement.final_value)).filter(PersonalTradeStatement.user_id==user.id, PersonalTradeStatement.brokerage==brokerage, PersonalTradeStatement.date<=current_date, PersonalTradeStatement.operation=="B").scalar()) or 0
                    sell_operations = (db.session.query(func.sum(PersonalTradeStatement.final_value)).filter(PersonalTradeStatement.user_id==user.id, PersonalTradeStatement.brokerage==brokerage, PersonalTradeStatement.date<=current_date, PersonalTradeStatement.operation=="S").scalar()) or 0
                    cash = total_contributions + sell_operations - buy_operations
                    
                    invested_value = 0.0
                    # print("summaries", summaries)
                    for s in summaries:
                        if s.investment_type != "fixed_income":
                            invested_value += s.quantity * s.current_price
                        else:
                            invested_value += s.current_price

                    # print(invested_value)
                    broker_status = (db.session.query(BrokerStatus).filter_by(user_id=user.id, brokerage=brokerage, date=current_date).first())
                    
                    if not broker_status:
                        # print("aqui")
                        broker_status = BrokerStatus(user_id=user.id, brokerage=brokerage, date=current_date)

                    broker_status.invested_value = round(invested_value, 2)
                    broker_status.total_contributions = round(total_contributions, 2)
                    broker_status.cash = round(cash, 2)
                    db.session.add(broker_status)
                    current_date += timedelta(days=1)
        db.session.commit()    

