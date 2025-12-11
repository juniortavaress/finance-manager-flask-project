from app.models import Assets, PersonalTradeStatement
from app.finance_tools import CompanyPricesFetcher, UpdateDatabases, ManagerNotesExtractor

from datetime import datetime
from app import database as db

def process_trade_statements(files, user_id):
    print("process_trade_statements")
    trades = []
    for file in files:
        new_trades = ManagerNotesExtractor.get_info_from_trade_statement(file, file.read(), user_id)
        if new_trades:
            trades.extend(new_trades)

    if not trades:
        return

    unique_tickers = list({trade.ticker for trade in trades});                          print('\n\n', unique_tickers)
    UpdateDatabases.atualize_assets_db(user_id, unique_tickers)
    CompanyPricesFetcher.run_api_company_history_prices(unique_tickers)
    UpdateDatabases.atualize_summary(user_id, trades)


def process_manually_input(user_id, data):
    print("process_manually_input")

    trade = PersonalTradeStatement(
        user_id=user_id,
        brokerage=data.get('brokerage'),
        investment_type=data.get('investment_type'),
        date=datetime.strptime(data.get('date'), "%Y-%m-%d").date(),
        statement_number=data.get('statement_number'),
        operation=data.get('operation'),
        ticker=data.get('ticker'),
        quantity=float(data.get('quantity', 0)),
        unit_price=float(data.get('unit_price', 0)),
        final_value=float(data.get('final_value', 0))
    )

    db.session.add(trade)
    db.session.commit()
    print('process_manually_input')

    if data.get('investment_type') != "fixed_income":
        UpdateDatabases.atualize_assets_db(user_id, [data.get('ticker')])

        if data.get('investment_type') == "cripto":
            CompanyPricesFetcher.run_api_crypto_history_prices_brl([data.get('ticker')])
        else:
            CompanyPricesFetcher.run_api_company_history_prices([data.get('ticker')])

    UpdateDatabases.atualize_summary(user_id, [trade])

