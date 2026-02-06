
from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.finance_tools.api_prices import CompanyPricesFetcher, CriptoPricesFetcher
from app.finance_tools.market_data.realtime_updates import RealtimeUpdates


app = create_app()


def start_scheduler():
    """
    Starts the background scheduler responsible for daily database updates.
    """
    update_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_db, 'cron', hour=2, minute=0)
    scheduler.start()


def update_db():
    """
    Executes all daily background update tasks.

    This function:
    - Fetches and stores crypto historical prices
    - Fetches and stores company historical prices
    - Updates daily summaries in the database

    It must always run inside an application context.
    """
    with app.app_context():
        CriptoPricesFetcher.run_api_cripto_history_prices_brl(app.config['ENABLED_CRYPTOS_BRL'])
        CompanyPricesFetcher.run_api_company_history_prices()
        RealtimeUpdates.daily_summary_changes()
         

if __name__ == "__main__":
    start_scheduler()
    app.run(debug=app.config['DEBUG'])
    # app.run(use_reloader=False, debug=app.config['DEBUG'])
    

# debug=false (mode de produção)
#   -> não recarrega o servidor automaticamente
#   -> erros genericos sem o traceback
#   -> não expoe detalhes internos