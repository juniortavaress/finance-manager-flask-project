from app import database as db
from datetime import date, timedelta
from app.models import UserTradeSummary, CriptoDatas, PersonalTradeStatement, User, CompanyDatas, UserDividents


class UpdateEquityDatabases:
    @staticmethod
    def update_equities_daily(start_date=None):
        today = date.today()
        users = db.session.query(User).all()
        rebuild_start = start_date if start_date else today

        for user in users:
            tickers = (
                db.session.query(UserTradeSummary.company)
                .filter(
                    UserTradeSummary.user_id == user.id,
                    UserTradeSummary.investment_type.notin_(["cripto", "fixed_income"])
                )
                .distinct()
                .all()
            )

            ticker_list = [t.company for t in tickers]

            if start_date and ticker_list:
                db.session.query(UserTradeSummary).filter(
                    UserTradeSummary.user_id == user.id,
                    UserTradeSummary.company.in_(ticker_list),
                    UserTradeSummary.date >= rebuild_start
                ).delete(synchronize_session=False)

            for ticker in ticker_list:
                current_day = rebuild_start

                while current_day <= today:
                    last_summary = (
                        db.session.query(UserTradeSummary)
                        .filter(
                            UserTradeSummary.user_id == user.id,
                            UserTradeSummary.company == ticker,
                            UserTradeSummary.date < current_day
                        )
                        .order_by(UserTradeSummary.date.desc())
                        .first()
                    )

                    if not last_summary or last_summary.quantity == 0:
                        current_day += timedelta(days=1)
                        continue

                    price_entry = (
                        db.session.query(CompanyDatas)
                        .filter_by(company=ticker, date=current_day)
                        .first()
                    )

                    current_price = (
                        price_entry.current_price
                        if price_entry
                        else last_summary.current_price
                    )

                    dividends = (
                        db.session.query(UserDividents)
                        .filter(
                            UserDividents.user_id == user.id,
                            UserDividents.ticker == ticker,
                            UserDividents.date <= current_day
                        )
                        .all()
                    )

                    total_dividends = sum(d.value for d in dividends)

                    existing = (
                        db.session.query(UserTradeSummary)
                        .filter_by(
                            user_id=user.id,
                            company=ticker,
                            date=current_day
                        )
                        .first()
                    )

                    if not existing:
                        db.session.add(
                            UserTradeSummary(
                                user_id=user.id,
                                brokerage=last_summary.brokerage,
                                investment_type=last_summary.investment_type,
                                company=ticker,
                                date=current_day,
                                quantity=last_summary.quantity,
                                avg_price=last_summary.avg_price,
                                current_price=current_price,
                                dividend=total_dividends
                            )
                        )
                    current_day += timedelta(days=1)
        db.session.commit()


    @staticmethod
    def atualize_equities_trades(user_id, trade):
        """
        Updates the stock summary table for a given trade.

        1. Deletes any summary entries from the trade date forward.
        2. Recalculates current quantity and average price.
        3. Updates or inserts the summary for each price date.
        """
        trade_date = trade.date if isinstance(trade.date, date) else trade.date.date()

        db.session.query(UserTradeSummary).filter(
            UserTradeSummary.user_id == user_id,
            UserTradeSummary.company == trade.ticker,
            UserTradeSummary.date >= trade_date
        ).delete(synchronize_session=False)
        db.session.commit()

        trades, prices, dividends, last_quantity = UpdateEquityDatabases._get_info(user_id, trade)
        
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
        db.session.commit()


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
        if trade.investment_type == "cripto":
            prices = db.session.query(CriptoDatas).filter_by(coin=trade.ticker[:3]).order_by(CriptoDatas.date).all()
        else:
            prices = db.session.query(CompanyDatas).filter_by(company=trade.ticker).order_by(CompanyDatas.date).all()
        
        dividends = db.session.query(UserDividents).filter_by(user_id=user_id, ticker=trade.ticker).all()

        last_quantity = last_summary.quantity if last_summary else 0
        return trades, prices, dividends, last_quantity
    
    