import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a3190c71717b80582c2b580d8bc02528")
    SQLALCHEMY_DATABASE_URI = "sqlite:///website_infos.db"
    UPLOAD_FOLDER = "static/images"
    ENV = "development"
    DEBUG = True