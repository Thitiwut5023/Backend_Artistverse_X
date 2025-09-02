from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

# ---- Elasticsearch Client ----
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "DQEoJCHiY=jvaC0Cnbd8"),  # เปลี่ยนรหัสตามจริง
    ca_certs="~/http_ca.crt"
)

# ทดสอบการเชื่อมต่อ
try:
    print("Connected to ES:", es.info().body)
except Exception as e:
    print("Failed to connect to ES:", e)

# ---- Flask App ----
app = Flask(__name__)

index_name = "spotify"


@app.route("/search", methods=["GET"])
def search():
    """
    Example: /search?q=beatles&field=artists&size=5
    """
    query_text = request.args.get("q")
    field = request.args.get("field", "name")  # default: search in song name
    size = int(request.args.get("size", 10))   # default: return 10 hits

    if not query_text:
        return jsonify({"error": "Missing query parameter `q`"}), 400

    try:
        body = {
            "query": {
                "match": {
                    field: query_text
                }
            }
        }

        response = es.search(index=index_name, body=body, size=size)

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
        return jsonify({"error": str(e)}), 500


# ---- Run App ----
if __name__ == "__main__":
    app.run()