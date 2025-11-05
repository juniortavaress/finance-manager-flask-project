from app import database as db
from app.models import PersonalTradeStatement, CompanyDatas, UserTradeSummary, Assets, UserDividents
from datetime import date
import re 
from dateutil.relativedelta import relativedelta

class UpdateDatabases:
    def atualize_assets_db(list_tickers, user_id):
        """Updates the user's asset records based on current trade quantities."""
        print('Updating assets database...')
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


    def atualize_summary_db(user_id):
        """Updates the user trade summary table based on price and trade history."""
        print("Updating summary database...")
        trades = db.session.query(PersonalTradeStatement).filter_by(user_id=user_id).order_by(PersonalTradeStatement.date).all()
        
        fixed_income_trades_by_ticker = {}
        other_trades_by_ticker = {}
        for trade in trades:
            if trade.investment_type == "fixed_income":
                fixed_income_trades_by_ticker.setdefault(trade.ticker, []).append(trade)
            else:
                other_trades_by_ticker.setdefault(trade.ticker, []).append(trade)

        UpdateDatabases._atualize_fixed_income_trades_by_ticker(user_id, fixed_income_trades_by_ticker)
        UpdateDatabases._atualize_other_trades_by_ticker(user_id, other_trades_by_ticker)


    def _atualize_fixed_income_trades_by_ticker(user_id, trades_by_ticker):
        """Atualiza os resumos de renda fixa (CDB, Tesouro etc.) no banco."""
        print("Updating fixed income summaries...")

        # Cache existentes para evitar duplicatas
        existing_summaries = (db.session.query(UserTradeSummary) .filter_by(user_id=user_id) .all())
        existing_keys = {(s.company, s.date) for s in existing_summaries}
        today = date.today()

        for ticker, trades in trades_by_ticker.items():
            # Ignora se não há negociações
            if not trades:
                continue

            trades.sort(key=lambda t: t.date)
            current_quantity = sum(t.quantity if t.operation == "B" else -t.quantity for t in trades)
            if current_quantity <= 0:
                continue

            # Dados da última negociação (pra pegar corretora e tipo)
            last_trade = max(trades, key=lambda t: t.date)
            brokerage = last_trade.brokerage
            investment_type = last_trade.investment_type

            # Calcula preço médio de compra
            buy_trades = [t for t in trades if t.operation == "B"]
            total_buy_value = sum(t.final_value for t in buy_trades)
            total_buy_quantity = sum(t.quantity for t in buy_trades)
            avg_price = (round(total_buy_value / total_buy_quantity, 2) if total_buy_quantity > 0 else 0)

            # Extrai taxa nominal do nome (ex: "15.43%")
            match = re.search(r"([\d.,]+)%", ticker)
            rate = float(match.group(1).replace(",", ".")) if match else 0.0
            print(rate)

            # Data da primeira compra — base para o cálculo do rendimento
            start_date = min(t.date for t in buy_trades)
            start_month = date(start_date.year, start_date.month, 1)
            end_month = date(today.year, today.month, 1)

         # Gera lista de meses (primeiro dia de cada mês até o mês atual)
        months = []
        current_month = start_month
        while current_month <= end_month:
            months.append(current_month)
            current_month += relativedelta(months=1)

        invested_value = total_buy_value

        # Loop mês a mês
        for month_date in months:
            if (ticker, month_date) in existing_keys:
                continue  # já existe no banco, pula

            # Quantos dias passaram desde a data da compra
            days_passed = (month_date - start_date).days
            if days_passed < 0:
                continue  # antes da compra

            # Calcula valor atualizado com juros compostos
            current_value = invested_value * ((1 + rate / 100) ** (days_passed / 365))
            current_price = round(current_value / current_quantity, 2)

            summary = UserTradeSummary(
                user_id=user_id,
                brokerage=brokerage,
                investment_type=investment_type,
                date=month_date,
                company=ticker,
                quantity=current_quantity,
                current_price=current_price,
                avg_price=avg_price,
                dividend=0,
            )
            db.session.add(summary)
            existing_keys.add((ticker, month_date))  # marca como salvo

        db.session.commit()




    def _atualize_other_trades_by_ticker(user_id, trades_by_ticker):
        # Load all prices
        prices = db.session.query(CompanyDatas).order_by(CompanyDatas.date).all()

        # Load all dividends and group by ticker
        dividends = db.session.query(UserDividents).filter_by(user_id=user_id).all()
        dividends_by_ticker = {}
        for d in dividends:
            dividends_by_ticker.setdefault(d.ticker, []).append(d)

        # Cache existing summaries to avoid duplicate inserts
        existing_summaries = db.session.query(UserTradeSummary).filter_by(user_id=user_id).all()
        existing_keys = {(s.company, s.date) for s in existing_summaries}

        for price in prices:
            ticker = price.company
            price_date = price.date

            if (ticker, price_date) in existing_keys:
                continue

            ticker_trades = trades_by_ticker.get(ticker, [])
            trades_until_date = [t for t in ticker_trades if t.date <= price_date]

            if not trades_until_date:
                continue

            current_quantity = sum(t.quantity if t.operation == 'B' else -t.quantity for t in trades_until_date)
            if current_quantity <= 0:
                continue

            buy_trades = [t for t in trades_until_date if t.operation == 'B']
            total_buy_value = sum(t.final_value for t in buy_trades)
            total_buy_quantity = sum(t.quantity for t in buy_trades)
            avg_price = round(total_buy_value / total_buy_quantity, 2) if total_buy_quantity > 0 else 0

            # Sum dividends up to price_date
            ticker_dividends = dividends_by_ticker.get(ticker, [])
            total_dividends = sum(d.value for d in ticker_dividends if d.date <= price_date)

            last_trade = max(trades_until_date, key=lambda t: t.date)
            brokerage = last_trade.brokerage if hasattr(last_trade, 'brokerage') else None
            investment_type = last_trade.investment_type if hasattr(last_trade, 'investment_type') else None

            summary = UserTradeSummary(
                user_id=user_id,
                brokerage=brokerage,
                investment_type=investment_type,
                date=price_date,
                company=ticker,
                quantity=current_quantity,
                current_price=price.current_price,
                avg_price=avg_price,
                dividend=total_dividends
            )
            db.session.add(summary)

        db.session.commit()



    # def atualize_summary_db(user_id):
    #     """Updates the user trade summary table based on price and trade history."""
    #     print("Updating summary database...")
    #     # Preload all trades and prices
    #     trades = db.session.query(PersonalTradeStatement).filter_by(user_id=user_id).order_by(PersonalTradeStatement.date).all()
    #     prices = db.session.query(CompanyDatas).order_by(CompanyDatas.date).all()

    #     # Organize trades by ticker for faster access
    #     trades_by_ticker = {}
    #     for trade in trades:
    #         trades_by_ticker.setdefault(trade.ticker, []).append(trade)

    #     for price in prices:
    #         ticker = price.company
    #         price_date = price.date

    #         last_summary = (db.session.query(UserTradeSummary)
    #             .filter_by(user_id=user_id, company=ticker)
    #             .order_by(UserTradeSummary.date.desc())
    #             .first())

    #         # Already updated to this date or earlier
    #         if last_summary and price_date <= last_summary.date:
    #             # print(f"{ticker} already updated until {last_summary.date}")
    #             continue

    #         # Filter trades up to the current price date
    #         ticker_trades = trades_by_ticker.get(ticker, [])
    #         trades_until_date = [t for t in ticker_trades if t.date <= price_date]

    #         if trades_until_date:
    #             current_quantity = sum(t.quantity if t.operation == 'B' else -t.quantity for t in trades_until_date)
    #             buy_trades = [t for t in trades_until_date if t.operation == 'B']
    #             total_buy_value = sum(t.final_value for t in buy_trades)
    #             total_buy_quantity = sum(t.quantity for t in buy_trades)
    #             avg_price = round(total_buy_value / total_buy_quantity, 2) if total_buy_quantity > 0 else 0
    #         else:
    #             current_quantity = 0
    #             avg_price = 0

    #         # Calculate total dividends
    #         total_dividends = (db.session.query(UserDividents)
    #             .filter(UserDividents.user_id == user_id,
    #                        UserDividents.ticker == ticker,
    #                        UserDividents.date <= price_date)
    #             .with_entities(db.func.sum(UserDividents.value))
    #             .scalar()) or 0

    #         # Save summary record
    #         if current_quantity > 0:
    #             summary = UserTradeSummary(
    #                 user_id=user_id,
    #                 date=price_date,
    #                 company=ticker,
    #                 quantity=current_quantity,
    #                 current_price=price.current_price,
    #                 avg_price=avg_price,
    #                 dividend=total_dividends
    #             )
    #             db.session.add(summary)
    #     db.session.commit()