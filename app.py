import os
from dotenv import load_dotenv

load_dotenv(override=True)

from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from models import db
from routes import register_blueprints


login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-voice-assistant-secret-key-2026')
    app_root = os.path.dirname(os.path.abspath(__file__))
    database_dir = os.path.join(app_root, 'database')
    os.makedirs(database_dir, exist_ok=True)
    db_file = os.path.join(database_dir, "voice_assistant.db").replace('\\', '/')
    env_db = os.getenv('DATABASE_URL')
    if env_db and not env_db.startswith('sqlite:///database') and not env_db.startswith('sqlite:///instance'):
        app.config['SQLALCHEMY_DATABASE_URI'] = env_db
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app_root, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['WTF_CSRF_ENABLED'] = False

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    with app.app_context():
        from models import User, Conversation, Message, Document
        db.create_all()

    register_blueprints(app)
    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
