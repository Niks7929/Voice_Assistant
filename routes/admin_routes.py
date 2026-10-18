from flask import Blueprint, render_template
from flask_login import login_required

from models.user import User
from models.conversation import Conversation
from models.message import Message

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@login_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(status='active').count(),
        'blocked_users': User.query.filter_by(status='blocked').count(),
        'total_conversations': Conversation.query.count(),
        'total_messages': Message.query.count(),
    }
    return render_template('admin_dashboard.html', users=users, stats=stats, current_user=None)
