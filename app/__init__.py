from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

database = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    database.init_app(app)
    bcrypt.init_app(app)

    # from app import routes
    from app.routes import main
    app.register_blueprint(main)
    return app