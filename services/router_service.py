import re


class RouterService:
    @staticmethod
    def classify(question: str) -> str:
        q = (question or '').strip().lower()
        if not q:
            return 'GENERAL'

        if re.search(r'\b(calculat|compute|math|plus|minus|multiply|divide|sqrt|sum|average|percent|\d+\s*[+\-*/%]\s*\d+)\b', q):
            return 'CALCULATOR'
        if any(k in q for k in ['weather', 'news', 'latest', 'today', 'tomorrow', 'current', 'search', 'find', 'what happened']):
            return 'WEB_SEARCH'
        if any(k in q for k in ['pdf', 'document', 'file', 'summary', 'read', 'extract', 'upload', 'analyze']):
            return 'DOCUMENT'
        if (
            ('write' in q or 'show' in q or 'example' in q or 'snippet' in q or 'function' in q or 'class' in q or 'programming' in q or 'debug' in q)
            and ('python' in q or 'flask' in q or 'javascript' in q or 'code' in q or 'function' in q or 'class' in q)
        ):
            return 'CODE'
        if any(k in q for k in ['time', 'date', 'today', 'tomorrow', 'day', 'month', 'year']):
            return 'DATETIME'
        if 'url' in q or 'website' in q or 'webpage' in q:
            return 'URL'
        if 'who' in q or 'what' in q or 'why' in q or 'how' in q:
            return 'GENERAL'
        return 'GENERAL'
