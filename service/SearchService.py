from flask import jsonify
from elasticsearch import Elasticsearch

class SearchService:
    def __init__(self):
        # ---- Elasticsearch Client ----
        self.es = Elasticsearch(
            "https://localhost:9200",
            basic_auth=("elastic", "DQEoJCHiY=jvaC0Cnbd8"),  # เปลี่ยนรหัสตามจริง
            ca_certs="~/http_ca.crt"
        )
        
        self.index_name = "spotify"
        
        # ทดสอบการเชื่อมต่อ
        try:
            print("Connected to ES:", self.es.info().body)
        except Exception as e:
            print("Failed to connect to ES:", e)

    def search(self, query_text, field="name", size=10):
        """
        Search for songs in Elasticsearch
        Args:
            query_text: The search query
            field: The field to search in (default: "name")
            size: Number of results to return (default: 10)
        """
        try:
            body = {
                "query": {
                    "match": {
                        field: query_text
                    }
                }
            }

            response = self.es.search(index=self.index_name, body=body, size=size)

            results = [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"]
                }
                for hit in response["hits"]["hits"]
            ]

            return jsonify({
                "query": query_text,
                "field": field,
                "hits": results
            })

        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")
