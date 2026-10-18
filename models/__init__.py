from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .user import User
from .conversation import Conversation
from .message import Message
from .document import Document
