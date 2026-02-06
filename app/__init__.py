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

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Optional: database setup or initial data
    # with app.app_context():
    #     database.create_all()

    return app


