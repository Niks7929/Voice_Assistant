from services.web_search_service import WebSearchService


class WebSearchTool:
    @staticmethod
    def search(query: str, limit: int = 3):
        return WebSearchService.search(query, limit=limit)
