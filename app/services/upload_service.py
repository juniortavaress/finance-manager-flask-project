from app.models import Assets, PersonalTradeStatement
from app.finance_tools import CompanyPricesFetcher, UpdateDatabases, ManagerNotesExtractor

from datetime import datetime
from app import database as db

def process_trade_statements(files, user_id):
    tickers = []
    for file in files:
        extracted = ManagerNotesExtractor.get_info_from_trade_statement(file, file.read(), user_id)
        if extracted is not None:
            tickers.extend(extracted)

    # unique_tickers = list(set(tickers))
    # print(unique_tickers)
    # if not unique_tickers:
    #     return

    # UpdateDatabases.atualize_assets_db(unique_tickers, user_id)
    assets = Assets.query.distinct(Assets.company).all()
    updated = CompanyPricesFetcher.run_api_company_history_prices(assets)
    print(updated)
    # if updated:
    UpdateDatabases.atualize_summary_db(user_id)


def process_manually_input(user_id, data):
    investment_type = data.get('investment_type')
    new_trade = PersonalTradeStatement(
        user_id=user_id,
        brokerage=data.get('brokerage'),
        investment_type=investment_type,
        date=datetime.strptime(data.get('date'), "%Y-%m-%d").date(),
        statement_number=data.get('statement_number'),
        operation=data.get('operation'),
        ticker=data.get('ticker'),
        quantity=float(data.get('quantity', 0)),
        unit_price=float(data.get('unit_price', 0)),
        final_value=float(data.get('final_value', 0))
    )

    db.session.add(new_trade)
    db.session.commit()

    assets = Assets.query.distinct(Assets.company).all()
    if investment_type != "fixed_income":
        CompanyPricesFetcher.run_api_company_history_prices(assets)

    print(new_trade)
    UpdateDatabases.atualize_summary_db(user_id)