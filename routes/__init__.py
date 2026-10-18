from .main_routes import main_bp
from .auth_routes import auth_bp
from .chat_routes import chat_bp
from .document_routes import document_bp
from .admin_routes import admin_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(admin_bp)
