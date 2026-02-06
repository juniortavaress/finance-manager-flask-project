import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a3190c71717b80582c2b580d8bc02528")
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "static/images"
    ENV = "development"
    DEBUG = True
    ENABLED_CRYPTOS_BRL = ["BTCBRL", "ETHBRL", "SOLBRL", "BNBBRL", "XRPBRL", "ADABRL"]


