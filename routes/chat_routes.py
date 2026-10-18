from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import db
from models.conversation import Conversation
from models.message import Message
from models.document import Document
from services.ai_service import AIService

chat_bp = Blueprint('chat', __name__)
ai_service = AIService()


@chat_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get('question') or payload.get('message') or '').strip()
    conversation_id = payload.get('conversation_id')
    document_id = payload.get('document_id')

    if not question:
        return jsonify({'status': 'error', 'message': 'Question cannot be empty.'}), 400

    # Retrieve attached document / codebase text if active
    document_context = None
    if document_id:
        doc = Document.query.filter_by(id=int(document_id), user_id=current_user.id).first()
        if doc and doc.content:
            document_context = doc.content
    else:
        # Auto-detect if user asks about their uploaded file or code
        q_lower = question.lower()
        if any(w in q_lower for w in ['uploaded', 'this file', 'this code', 'my code', 'my file', 'document', 'calculate_tax', 'in the file']):
            recent_doc = Document.query.filter_by(user_id=current_user.id).order_by(Document.id.desc()).first()
            if recent_doc and recent_doc.content:
                document_context = recent_doc.content

    # Find or create conversation
    conv = None
    if conversation_id:
        conv = Conversation.query.filter_by(id=int(conversation_id), user_id=current_user.id).first()

    if conv is None:
        title = question[:45] + ('...' if len(question) > 45 else '')
        conv = Conversation(user_id=current_user.id, title=title)
        db.session.add(conv)
        db.session.commit()

    # Conversation history for context
    past_messages = [{'role': m.role, 'content': m.content} for m in conv.messages[-6:]] if conv.messages else []

    # Save User message
    user_msg = Message(
        conversation_id=conv.id,
        role='user',
        content=question,
        created_at=datetime.utcnow()
    )
    db.session.add(user_msg)
    db.session.commit()

    # Generate specialized programming response
    result = ai_service.answer(
        question=question,
        document_context=document_context,
        conversation_history=past_messages
    )

    # Save Assistant message
    assistant_msg = Message(
        conversation_id=conv.id,
        role='assistant',
        content=result['answer'],
        tool_used=result.get('tool_used', 'CODE_AI'),
        created_at=datetime.utcnow()
    )
    db.session.add(assistant_msg)
    conv.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'status': 'success',
        'answer': result['answer'],
        'tool_used': result.get('tool_used', 'CODE_AI'),
        'conversation_id': conv.id,
        'conversation_title': conv.title,
        'message_id': assistant_msg.id
    })


@chat_bp.route('/api/chat/conversations', methods=['GET'])
@login_required
def get_user_conversations():
    conversations = Conversation.query.filter_by(user_id=current_user.id)\
        .order_by(Conversation.updated_at.desc()).all()
    return jsonify({
        'status': 'success',
        'conversations': [c.to_dict(include_messages=False) for c in conversations]
    })


@chat_bp.route('/api/chat/conversations/<int:conv_id>', methods=['GET'])
@login_required
def get_conversation_detail(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first()
    if not conv:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404

    return jsonify({
        'status': 'success',
        'conversation': conv.to_dict(include_messages=True)
    })


@chat_bp.route('/api/chat/conversations/<int:conv_id>', methods=['DELETE'])
@login_required
def delete_conversation(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first()
    if not conv:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404

    db.session.delete(conv)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Conversation deleted'})


@chat_bp.route('/api/chat/conversations/clear', methods=['POST'])
@login_required
def clear_all_conversations():
    Conversation.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'All conversations cleared'})


@chat_bp.route('/api/chat/feedback', methods=['POST'])
@login_required
def feedback():
    payload = request.get_json(silent=True) or {}
    message_id = payload.get('message_id')
    rating = payload.get('rating')

    if message_id and rating in ['like', 'dislike']:
        msg = Message.query.get(int(message_id))
        if msg:
            msg.rating = rating
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Feedback recorded'})

    return jsonify({'status': 'error', 'message': 'Invalid feedback request'}), 400
