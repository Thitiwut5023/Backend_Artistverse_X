from flask import request, jsonify
from service.SearchService import SearchService

class SearchController:
    def __init__(self):
        self.search_service = SearchService()

    def search_handler(self):
        """
        Handle search requests
        Example: /search?q=beatles&field=artists&size=5
        """
        try:
            query_text = request.args.get("q")
            field = request.args.get("field", "name")  # default: search in song name
            size = int(request.args.get("size", 10))   # default: return 10 hits

            if not query_text:
                return jsonify({"error": "Missing query parameter `q`"}), 400

            result = self.search_service.search(query_text, field, size)
            return result

        except Exception as e:
            return jsonify({"error": str(e)}), 500
