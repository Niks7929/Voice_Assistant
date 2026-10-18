import re

import requests
from bs4 import BeautifulSoup


class WebSearchService:
    @staticmethod
    def search(query: str, limit: int = 3):
        q = (query or '').strip()
        if not q:
            return []

        params = {'q': q, 'format': 'json', 'no_redirect': '1', 'no_html': '1'}
        try:
            response = requests.get('https://api.duckduckgo.com/', params=params, timeout=12)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            payload = {}

        results = []
        for item in payload.get('RelatedTopics', [])[:limit]:
            if isinstance(item, dict):
                text = item.get('Text') or item.get('FirstURL')
                link = item.get('FirstURL')
                if text:
                    results.append({'title': text.split(' - ')[0][:80], 'url': link or '', 'snippet': text})

        if results:
            return results[:limit]

        fallback_url = 'https://duckduckgo.com/html/?q=' + requests.utils.quote(q)
        try:
            html = requests.get(fallback_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=12).text
            soup = BeautifulSoup(html, 'html.parser')
            hits = soup.select('a.result-link')
            for link in hits[:limit]:
                title = link.get_text(' ', strip=True)
                href = link.get('href')
                results.append({'title': title[:80], 'url': href or '', 'snippet': title})
        except Exception:
            pass

        return results[:limit]
