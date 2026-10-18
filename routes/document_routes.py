import os
from pathlib import Path
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from models import db
from models.document import Document
from tools.document_tool import DocumentTool

document_bp = Blueprint('document', __name__)

ALLOWED_EXTENSIONS = {
    'txt', 'md', 'pdf', 'docx', 'doc',
    'py', 'js', 'jsx', 'ts', 'tsx', 'java', 'c', 'cpp', 'h', 'hpp',
    'cs', 'go', 'rs', 'php', 'rb', 'swift', 'kt', 'dart', 'sql', 'sh',
    'json', 'yaml', 'yml', 'html', 'css'
}


def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@document_bp.route('/api/document/upload', methods=['POST'])
@login_required
def upload_document():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file was provided in the request.'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file was selected.'}), 400

    if not is_allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': 'Unsupported file format. Supported: .py, .js, .ts, .java, .cpp, .sql, .pdf, .docx, .txt, etc.'
        }), 400

    upload_dir = Path(os.getcwd()) / 'uploads'
    upload_dir.mkdir(exist_ok=True)

    filename = secure_filename(file.filename)
    safe_name = f"{current_user.id}_{filename}"
    save_path = upload_dir / safe_name
    file.save(save_path)

    # Extract text from code/doc file
    content = DocumentTool.extract_text(str(save_path))
    ext = save_path.suffix.lower().lstrip('.')

    document = Document(
        user_id=current_user.id,
        filename=filename,
        file_type=ext,
        storage_path=str(save_path),
        content=content,
        source_url=None,
    )
    db.session.add(document)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f"File '{filename}' successfully indexed for code Q&A.",
        'document': document.to_dict()
    })


@document_bp.route('/api/document/analyze-url', methods=['POST'])
@login_required
def analyze_url():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()
    if not url:
        return jsonify({'status': 'error', 'message': 'Please provide a valid web URL.'}), 400

    content = DocumentTool.load_from_url(url)
    filename = url.split('/')[-1] or 'webpage_docs.txt'

    document = Document(
        user_id=current_user.id,
        filename=filename,
        file_type='url',
        storage_path='url',
        content=content,
        source_url=url,
    )
    db.session.add(document)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f"Documentation at '{url}' scraped and indexed.",
        'document': document.to_dict()
    })
