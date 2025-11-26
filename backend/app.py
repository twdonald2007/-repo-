from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests
import os
from dotenv import load_dotenv

print("🔄 Starting server...")

load_dotenv()
print("✅ .env loaded")

app = Flask(__name__)
CORS(app)

# ✅ 這裡是你目前最嚴重的錯誤來源（我先照你寫法保留，但先 print 出來）
CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")
USER_ID = os.getenv("CLARIFAI_USER_ID")
APP_ID = os.getenv("CLARIFAI_APP_ID")
MODEL_ID = os.getenv("CLARIFAI_MODEL_ID")
MODEL_VERSION_ID = os.getenv("CLARIFAI_MODEL_VERSION_ID")


print("=== ENV DEBUG ===")
print("CLARIFAI_API_KEY:", CLARIFAI_API_KEY)
print("USER_ID:", USER_ID)
print("APP_ID:", APP_ID)
print("MODEL_ID:", MODEL_ID)
print("MODEL_VERSION_ID:", MODEL_VERSION_ID)
print("=================")


@app.route("/analyze", methods=["POST"])
def analyze():
    print("📥 /analyze endpoint hit")

    if "image" not in request.files:
        print("❌ No image in request.files")
        return jsonify({"error": "No image uploaded"}), 400

    img_file = request.files["image"].read()
    print("✅ Image received, size:", len(img_file))

    img_b64 = base64.b64encode(img_file).decode()
    print("✅ Image base64 encoded")

    url = (
        f"https://api.clarifai.com/v2/users/{USER_ID}/apps/{APP_ID}"
        f"/models/{MODEL_ID}/versions/{MODEL_VERSION_ID}/outputs"
    )

    print("🔗 Clarifai URL:", url)

    headers = {
        "Authorization": f"Key {CLARIFAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": [
            {"data": {"image": {"base64": img_b64}}}
        ]
    }

    print("🚀 Sending request to Clarifai...")

    response = requests.post(url, json=payload, headers=headers)

    print("📡 Clarifai status code:", response.status_code)

    if not response.ok:
        print("❌ Clarifai request failed:", response.text)
        return jsonify({
            "error": "Clarifai request failed",
            "status_code": response.status_code,
            "details": response.text
        }), response.status_code

    result = response.json()
    print("✅ Clarifai raw response received")

    status = result.get("status", {})
    print("📊 Clarifai status:", status)

    if status.get("code") != 10000:
        print("❌ Clarifai returned non-success status")
        return jsonify({
            "error": "Clarifai returned non-success status",
            "status": status,
            "raw": result
        }), 502

    try:
        concepts = result["outputs"][0]["data"]["concepts"]
        print("✅ Concepts parsed, count:", len(concepts))

        ingredients = [
            {"ingredient": c["name"], "confidence": c["value"]}
            for c in concepts
        ]

    except Exception as e:
        print("❌ Failed to parse Clarifai response:", str(e))
        return jsonify({
            "error": "Failed to parse Clarifai response",
            "exception": str(e),
            "raw": result
        }), 502

    print("✅ Returning ingredients")

    return jsonify({"ingredients": ingredients})


# ✅ 測試用首頁 GUI
@app.route("/")
def home():
    print("👀 Home '/' route accessed")
    return "✅ Flask server is running on Render!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
