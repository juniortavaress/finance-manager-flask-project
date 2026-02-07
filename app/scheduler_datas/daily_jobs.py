from app import create_app
from app.finance_tools.api_prices import CompanyPricesFetcher, CriptoPricesFetcher
from app.finance_tools.market_data.realtime_updates import RealtimeUpdates


def run_daily_updates():
    """
    Entry point for all daily background jobs.

    This script:
    - Fetches crypto prices
    - Fetches equity prices
    - Updates daily summaries

    It must be executed by an external scheduler (cron).
    """
    app = create_app()

    with app.app_context():
        CriptoPricesFetcher.run_api_cripto_history_prices_brl(app.config['ENABLED_CRYPTOS_BRL'])
        CompanyPricesFetcher.run_api_company_history_prices()
        RealtimeUpdates.daily_summary_changes()


if __name__ == "__main__":
    run_daily_updates()
