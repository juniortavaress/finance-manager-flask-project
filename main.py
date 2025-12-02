# import os 
# os.chdir(r'finance-manager-flask-project')
from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.finance_tools.market_data.get_companies_prices import CompanyPricesFetcher
from app.finance_tools.market_data.update_databases import UpdateDatabases



app = create_app()

def start_scheduler():
    atualize_db()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(atualize_db, 'cron', hour=2, minute=0)
    scheduler.start()

def atualize_db():
    with app.app_context():
        CompanyPricesFetcher.run_api_crypto_history_prices_brl()
        CompanyPricesFetcher.run_api_company_history_prices()
        UpdateDatabases.atualize_daily_summary()
        
if __name__ == "__main__":
    start_scheduler()
    app.run(debug=app.config['DEBUG'])
    

# debug=false (mode de produção)
#   -> não recarrega o servidor automaticamente
#   -> erros genericos sem o traceback
#   -> não expoe detalhes internos