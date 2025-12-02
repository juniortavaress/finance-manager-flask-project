import re 
from datetime import date
from app import database as db
from app.models import UserTradeSummary, PersonalTradeStatement, User, CompanyDatas, UserDividents


class UpdateEquityDatabases:
    @staticmethod
    def update_equities_daily():
        today = date.today()
        users = db.session.query(User).all()

        for user in users:
            tickers_query = db.session.query(UserTradeSummary.company).filter_by(user_id=user.id, investment_type='stock').distinct()
            
            for ticker_row in tickers_query:
                ticker = ticker_row.company

                last_summary = db.session.query(UserTradeSummary)\
                    .filter_by(user_id=user.id, company=ticker, investment_type='stock')\
                    .order_by(UserTradeSummary.date.desc())\
                    .first()

                if not last_summary or last_summary.date == today or last_summary.quantity == 0:
                    continue  

                price_entry = db.session.query(CompanyDatas)\
                    .filter_by(company=ticker, date=today)\
                    .first()
                
                current_price = price_entry.current_price if price_entry else last_summary.current_price

                dividends = db.session.query(UserDividents).filter(UserDividents.user_id == user.id, UserDividents.ticker == ticker).all()
                total_dividends = sum(d.value for d in dividends)

                new_summary = UserTradeSummary(
                    user_id=user.id,
                    brokerage=last_summary.brokerage,
                    investment_type=last_summary.investment_type,
                    company=ticker,
                    date=today,
                    quantity=last_summary.quantity,
                    avg_price=last_summary.avg_price,
                    current_price=current_price,
                    dividend=total_dividends
                )

                db.session.add(new_summary)
        db.session.commit()


    @staticmethod
    def atualize_stockes_trades(user_id, trade):
        """
        Updates the stock summary table for a given trade.

        1. Deletes any summary entries from the trade date forward.
        2. Recalculates current quantity and average price.
        3. Updates or inserts the summary for each price date.
        """
        trade_date = trade.date if isinstance(trade.date, date) else trade.date.date()
        print(f"\n=== Atualizando {trade.ticker} para user {user_id} a partir de {trade_date} ===")

        db.session.query(UserTradeSummary).filter(
            UserTradeSummary.user_id == user_id,
            UserTradeSummary.company == trade.ticker,
            UserTradeSummary.date >= trade_date
        ).delete(synchronize_session=False)
        db.session.commit()

        trades, prices, dividends, last_quantity = UpdateEquityDatabases._get_info(user_id, trade)
        
        print("last_quantity", last_quantity)

        for price in prices:
            price_date = price.date if isinstance(price.date, date) else price.date.date()

            trades_until_date = [t for t in trades if t.date <= price_date]
            if not trades_until_date:
                continue

            avg_price = UpdateEquityDatabases._calculate_avg_price(user_id, price_date, trade.ticker) 
            total_dividends = sum(d.value for d in dividends if d.date <= price_date)

            current_quantity = sum(
                (t.quantity if t.operation == 'B' else -t.quantity)
                for t in trades_until_date
            )

            summary = db.session.query(UserTradeSummary).filter_by(user_id=user_id, company=trade.ticker, date=price_date).first()
            if summary:
                summary.quantity = last_quantity + current_quantity
                summary.dividend = total_dividends
                summary.avg_price = avg_price
                summary.current_price = price.current_price
            else:
                summary = UserTradeSummary(
                    user_id=user_id,
                    brokerage=trade.brokerage,
                    investment_type=trade.investment_type,
                    date=price_date,
                    company=trade.ticker,
                    quantity= last_quantity + current_quantity,
                    current_price=price.current_price,
                    avg_price=avg_price,
                    dividend=total_dividends
                )
                db.session.add(summary)
            # UpdateEquityDatabases._atualize(user_id, trade, price_date)
        db.session.commit()


        
    @staticmethod
    def _calculate_broker_invested_value(user_id, brokerage, target_date, trade=None):
        summaries = (
            db.session.query(UserTradeSummary)
            .filter(
                UserTradeSummary.user_id == user_id,
                UserTradeSummary.brokerage == brokerage,
                UserTradeSummary.date <= target_date
            )
            .order_by(UserTradeSummary.company, UserTradeSummary.date.desc())
            .all()
        )

        last_by_company = {}
        for s in summaries:
            if s.company not in last_by_company:
                last_by_company[s.company] = s

        total_invested_value = sum(s.quantity * s.current_price for s in last_by_company.values())

        # Se trade é do mesmo dia e não tem summary ainda, adiciona ele
        if trade and (trade.date == target_date):
            total_invested_value += trade.quantity * trade.unit_price

        return total_invested_value

    @staticmethod
    def _calculate_avg_price(user_id, price, ticker):
        """
        Calculates the average buy price for a given ticker up to a certain date.

        Only 'B' (buy) operations are considered.
        """
        buy_trades_for_avg = db.session.query(PersonalTradeStatement).filter(
            PersonalTradeStatement.user_id == user_id,
            PersonalTradeStatement.ticker == ticker,
            PersonalTradeStatement.operation == 'B',
            PersonalTradeStatement.date <= price
        ).all()

        total_buy_value = sum(t.final_value for t in buy_trades_for_avg)
        total_buy_quantity = sum(t.quantity for t in buy_trades_for_avg)
        avg_price = round(total_buy_value / total_buy_quantity, 2) if total_buy_quantity > 0 else 0.0
        return avg_price
                
   
    @staticmethod
    def _get_info(user_id, trade):
        """
        Returns all information required to update stock summaries:
        - Trades from the trade date onwards
        - All prices for the ticker
        - All dividends for the ticker
        - Current quantity and average price from the last summary
        """
        trade_date = trade.date if isinstance(trade.date, date) else trade.date.date()

        last_summary = db.session.query(UserTradeSummary).filter(
            UserTradeSummary.user_id == user_id,
            UserTradeSummary.company == trade.ticker,
            UserTradeSummary.date < trade_date
        ).order_by(UserTradeSummary.date.desc()).first()

        trades = db.session.query(PersonalTradeStatement).filter(
            PersonalTradeStatement.user_id == user_id,
            PersonalTradeStatement.ticker == trade.ticker,
            PersonalTradeStatement.date >= trade_date  
        ).order_by(PersonalTradeStatement.date).all()

        # Load all prices
        prices = db.session.query(CompanyDatas).filter_by(company=trade.ticker).order_by(CompanyDatas.date).all()
        
        dividends = db.session.query(UserDividents).filter_by(user_id=user_id, ticker=trade.ticker).all()

        last_quantity = last_summary.quantity if last_summary else 0
        return trades, prices, dividends, last_quantity
    
    