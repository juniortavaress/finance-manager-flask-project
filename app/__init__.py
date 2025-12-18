import logging
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


database = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager() 

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    database.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  
    # login_manager.login_view = 'auth.new_user'  


    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    
    # Optional: database setup or initial data
    with app.app_context():
        database.create_all()
        seed_initial_data()

    return app


# # Optional: initial data seeding
# def seed_initial_data():
#     from app.models import User, Assets
#     from app.finance_tools import CompanyPricesFetcher

#     # CompanyPricesFetcher.run_api_company_history_prices(Assets.query.all())

#     user = User.query.filter_by(email='test@gmail.com').first()
#     if not user:
#         new_user = User(name='Junior Tavares', email='test@gmail.com')
#         new_user.set_password('testflask')
#         database.session.add(new_user)
#         database.session.commit()


def seed_initial_data():
    from app.models import Currency
    from app import database

    currencies = [
        {"code": "BRL", "name": "Real", "symbol": "R$", "icon": "payments"},
        {"code": "USD", "name": "Dólar Americano", "symbol": "$", "icon": "attach_money"},
        {"code": "CAD", "name": "Dólar Canadense", "symbol": "C$", "icon": "monetization_on"},
        {"code": "EUR", "name": "Euro", "symbol": "€", "icon": "euro"},
        {"code": "GBP", "name": "Libra Esterlina", "symbol": "£", "icon": "currency_pound"},
        {"code": "CHF", "name": "Franco Suíço", "symbol": "CHF", "icon": "toll"},
        {"code": "JPY", "name": "Iene Japonês", "symbol": "¥", "icon": "currency_yen"},
        {"code": "CNY", "name": "Yuan Chinês", "symbol": "¥", "icon": "currency_yuan"},
    ]

    for cur in currencies:
        exists = Currency.query.filter_by(code=cur["code"]).first()
        if not exists:
            database.session.add(
                Currency(
                    code=cur["code"],
                    name=cur["name"],
                    icon=cur["icon"],
                    symbol=cur["symbol"]
                )
            )

    database.session.commit()