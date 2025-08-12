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
    from app.models import User
    app.register_blueprint(main)

    # Para criar a db pela primeira vez
    with app.app_context():
        database.create_all()

        
        user = User.query.filter_by(email='test@gmail.com').first()
        if not user:
            user = User(name='Junior Tavares', email='test@gmail.com')
            user.set_password('testflask')
            database.session.add(user)
            database.session.commit()

    return app

