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

    database.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'main.login'
    login_manager.init_app(app)   
    
    from app.routes import main
    app.register_blueprint(main)

    # Para criar a db pela primeira vez
    from app.models import User, Assets
    from app.get_datas import GetDatas
    with app.app_context():
        assets = Assets.query.distinct(Assets.company).all()
        GetDatas.run_api_company_history_prices(assets)


    # with app.app_context():
    #     database.create_all()
    #     user = User.query.filter_by(email='test@gmail.com').first()
    #     if not user:
    #         user = User(name='Junior Tavares', email='test@gmail.com')
    #         user.set_password('testflask')
    #         database.session.add(user)
    #         database.session.commit()

    return app

