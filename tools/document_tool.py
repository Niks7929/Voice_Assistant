import os
import re
from pathlib import Path

import requests
from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentTool:
    @staticmethod
    def extract_text(file_path: str):
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.txt':
            return path.read_text(encoding='utf-8', errors='ignore')
        if suffix == '.pdf':
            reader = PdfReader(str(path))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or '')
            return '\n'.join(pages)
        if suffix == '.docx':
            doc = DocxDocument(str(path))
            return '\n'.join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
        return ''

    @staticmethod
    def summarize_text(text: str, max_chars: int = 1200):
        cleaned = re.sub(r'\s+', ' ', text or '').strip()
        return cleaned[:max_chars]

    @staticmethod
    def answer_question(question: str, document_text: str):
        text = (document_text or '').strip()
        if not text:
            return 'No document content is available to answer this question.'

        snippet = DocumentTool.summarize_text(text, max_chars=1200)
        q = (question or '').lower()
        if 'summary' in q or 'summarize' in q:
            return f"Summary: {snippet[:800]}"
        if 'what' in q or 'who' in q or 'when' in q or 'where' in q:
            return f"Based on the uploaded document: {snippet[:600]}"
        return f"Based on the uploaded document, the key information is: {snippet[:700]}"

    @staticmethod
    def load_from_url(url: str):
        try:
            response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response.text[:20000]
        except Exception:
            return ''
