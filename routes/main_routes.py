from flask import Blueprint, jsonify, render_template, redirect, url_for
from flask_login import current_user, login_required
from models.conversation import Conversation
from models.document import Document

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing Page for CodeVocalis AI."""
    return render_template('index.html', current_user=current_user)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Protected Dashboard Page holding the AI Voice Assistant & Developer Workspace."""
    user_conversations = Conversation.query.filter_by(user_id=current_user.id)\
        .order_by(Conversation.updated_at.desc()).all()
    user_documents = Document.query.filter_by(user_id=current_user.id)\
        .order_by(Document.created_at.desc()).limit(10).all()

    return render_template(
        'dashboard.html',
        current_user=current_user,
        conversations=user_conversations,
        documents=user_documents
    )


@main_bp.route('/api/settings/apikey', methods=['GET', 'POST'])
@login_required
def manage_api_key():
    import os
    from flask import request

    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        key = (data.get('api_key') or '').strip()

        if not key:
            return jsonify({'status': 'error', 'message': 'API key cannot be empty.'}), 400

        # Update environment variable in memory
        os.environ['GEMINI_API_KEY'] = key

        # Persist to .env file
        try:
            content = ""
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            import re
            if 'GEMINI_API_KEY=' in content:
                content = re.sub(r'GEMINI_API_KEY=.*', f'GEMINI_API_KEY={key}', content)
            else:
                content += f"\nGEMINI_API_KEY={key}\n"

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            pass

        # Update running AIService in chat_routes
        try:
            from routes.chat_routes import ai_service
            ai_service.gemini_key = key
            try:
                from google import genai
                ai_service.gemini_client = genai.Client(api_key=key)
            except Exception:
                pass
        except Exception:
            pass

        return jsonify({
            'status': 'success',
            'message': 'Google Gemini API Key successfully saved and activated! You now have real-time ChatGPT/Gemini power.'
        })

    # GET request: return status of API key
    current_key = os.getenv('GEMINI_API_KEY', '').strip()
    has_key = bool(current_key and 'your_gemini' not in current_key)
    preview = f"{current_key[:6]}...{current_key[-4:]}" if (has_key and len(current_key) > 12) else ""
    return jsonify({
        'status': 'success',
        'has_key': has_key,
        'key_preview': preview
    })


@main_bp.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'CodeVocalis AI Developer Voice Assistant',
        'version': '2.0.0'
    })
