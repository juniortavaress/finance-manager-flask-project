import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a3190c71717b80582c2b580d8bc02528")
    
    instance_path = os.path.join(ROOT_DIR, 'instance', 'database.db')
    
    if os.name == 'nt':  # If Windows (PC)
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + instance_path.replace("\\", "/")
    else: # If Linux (PythonAnywhere)
        SQLALCHEMY_DATABASE_URI = f"sqlite:////{instance_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images")
    
    # Debug enabled only on local PC
    DEBUG = os.name == 'nt'
    ENABLED_CRYPTOS_BRL = ["BTCBRL", "ETHBRL", "SOLBRL", "BNBBRL", "XRPBRL", "ADABRL"]