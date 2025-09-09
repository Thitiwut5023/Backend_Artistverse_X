import os
import pandas as pd
import pickle
from elasticsearch import Elasticsearch, helpers
 
# Connect to Elasticsearch
es = Elasticsearch("https://localhost:9200", 
                    basic_auth=("elastic", "DQEoJCHiY=jvaC0Cnbd8"),
                    ca_certs="~/http_ca.crt")
 
print("Ping:", es.ping())
 
# Load CSV
df = pd.read_csv("../test/data/merged_clean.csv")
 
index_name = "spotify"
 
# Delete old index if exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print("Old index deleted.")
 
# Mapping
mapping = {
    "mappings": {
        "properties": {
            "genres": {"type": "text"},  # Changed from keyword to text for better search
            "artists": {"type": "text"},
            "year": {"type": "integer"},
            "name": {"type": "text"}
        }
    }
}
 
# Create index
es.indices.create(index=index_name, body=mapping)
print(f"Created index: {index_name}")
 
# ---------------------------
# Bulk indexing
# ---------------------------
actions = []
for i, row in df.iterrows():
    action = {
        "_index": index_name,
        "_id": i + 1,
        "_source": {
            "genres": row["genres"],
            "artists": row["artists"],
            "year": int(row["year"]),
            "name": row["name"]
        }
    }
    actions.append(action)
 
print(f"Prepared {len(actions)} documents for bulk indexing.")
 
# Execute bulk insert
success, failed = 0, 0
results = []
 
for ok, result in helpers.streaming_bulk(es, actions, chunk_size=500, request_timeout=60):
    if ok:
        success += 1
    else:
        failed += 1
    results.append((ok, result))
 
print(f"Bulk indexing completed: {success} succeeded, {failed} failed.")
 
# ---------------------------
# Save results to pickle
# ---------------------------
log_data = {
    "success_count": success,
    "failed_count": failed,
    "details": results[:100]  # store only first 100 logs to avoid huge pickle size
}
 
with open("bulk_index_log.pkl", "wb") as f:
    pickle.dump(log_data, f)
 
print("Bulk indexing log saved to bulk_index_log.pkl")