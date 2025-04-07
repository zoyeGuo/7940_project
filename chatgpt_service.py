from flask import Flask, request, jsonify
from ChatGPT_HKBU import HKBU_ChatGPT
import os

app = Flask(__name__)

# 从环境变量中获取 ChatGPT 配置
basic_url = os.environ.get("CHATGPT_BASICURL")
model_name = os.environ.get("CHATGPT_MODELNAME")
api_version = os.environ.get("CHATGPT_APIVERSION")
access_token = os.environ.get("CHATGPT_ACCESSTOKEN")

# 创建 ChatGPT 实例
chatgpt = HKBU_ChatGPT(
    basic_url=basic_url,
    model_name=model_name,
    api_version=api_version,
    access_token=access_token
)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' parameter"}), 400
    prompt = data["prompt"]
    response_text = chatgpt.submit(prompt)
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)