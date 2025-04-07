import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
import pymongo.errors

app = Flask(__name__)

# 从环境变量中获取 MongoDB 配置
conn_str = os.environ.get("MONGODB_CONNECTIONSTRING")
db_name = os.environ.get("MONGODB_DATABASE")
collection_name = os.environ.get("MONGODB_COLLECTION")

if not (conn_str and db_name and collection_name):
    raise Exception("Missing MongoDB environment variable configuration. Please check MONGODB_CONNECTIONSTRING, MONGODB_DATABASE, and MONGODB_COLLECTION.")

# 创建 MongoClient 对象，注意 Azure Cosmos DB 要求关闭 retryWrites
client = MongoClient(conn_str, serverSelectionTimeoutMS=30000, socketTimeoutMS=30000, retryWrites=False)
db = client[db_name]
collection = db[collection_name]

@app.route("/insert", methods=["POST"])
def insert():
   
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    required_fields = ["game_id", "rank", "contact"]
    missing = [field for field in required_fields if field not in data or not str(data[field]).strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # 检查是否已存在相同的 game_id
    existing = collection.find_one({"game_id": data["game_id"]})
    if existing:
        return jsonify({"message": "game_id already exists, not adding duplicate", "data": data}), 200

    try:
        result = collection.insert_one(data)
        return jsonify({"message": "Insert successful", "inserted_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": "Insert failed: " + str(e)}), 500

@app.route("/query", methods=["GET"])
def query():
    """
    根据查询参数 rank 查询用户数据，
    返回所有匹配记录（不包含 _id 字段）。
    """
    rank = request.args.get("rank")
    if not rank:
        return jsonify({"error": "Missing query parameter: rank"}), 400
    try:
        results = list(collection.find({"rank": rank}, {"_id": 0}))
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": "Query failed: " + str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)