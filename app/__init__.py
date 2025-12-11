import logging
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
# from app.services.sidebar_context import sidebar_context


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

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # app.context_processor(sidebar_context)
    
    # Optional: database setup or initial data
    with app.app_context():
        database.create_all()
        seed_initial_data()

    return app


# Optional: initial data seeding
def seed_initial_data():
    from app.models import User, Assets
    from app.finance_tools import CompanyPricesFetcher

    # CompanyPricesFetcher.run_api_company_history_prices(Assets.query.all())

    user = User.query.filter_by(email='test@gmail.com').first()
    if not user:
        new_user = User(name='Junior Tavares', email='test@gmail.com')
        new_user.set_password('testflask')
        database.session.add(new_user)
        database.session.commit()