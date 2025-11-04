# from flask import Blueprint

def register_blueprints(app):
    from .auth_routes import auth_bp
    from .transaction_routes import transaction_bp
    from .finance_routes import finance_bp
    from .upload_routes import upload_bp
    from .user_routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(user_bp)
