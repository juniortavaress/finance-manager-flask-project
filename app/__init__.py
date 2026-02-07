from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
import click

database = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager() 

def register_commands(app):
    @app.cli.command("run-daily-updates")
    @with_appcontext
    def run_daily_updates():
        from app.finance_tools.api_prices import CompanyPricesFetcher, CriptoPricesFetcher
        from app.finance_tools.market_data.realtime_updates import RealtimeUpdates
        
        print("Iniciando atualizações diárias...")
        CriptoPricesFetcher.run_api_cripto_history_prices_brl(app.config['ENABLED_CRYPTOS_BRL'])
        CompanyPricesFetcher.run_api_company_history_prices()
        RealtimeUpdates.daily_summary_changes()
        print("Atualização concluída com sucesso!")


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    database.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    register_commands(app)

    return app


