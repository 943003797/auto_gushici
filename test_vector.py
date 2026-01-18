from src.vector.vectordb import VectorDB


vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video")

where = {
        "$and": [
            {"duration": {"$gte": 3 }},
            {"duration": {"$lte": 10 }},
        ]}
res = vector_db.search("书房", n_results=30, where=where)
print(res)
