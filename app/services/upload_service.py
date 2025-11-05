from app.models import Assets
from app.finance_tools import CompanyPricesFetcher, UpdateDatabases, ManagerNotesExtractor

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
