from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")
USER_ID = os.getenv("CLARIFAI_USER_ID")
APP_ID = os.getenv("CLARIFAI_APP_ID")
MODEL_ID = os.getenv("CLARIFAI_MODEL_ID")
MODEL_VERSION_ID = os.getenv("CLARIFAI_MODEL_VERSION_ID")



@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img_file = request.files["image"].read()
    img_b64 = base64.b64encode(img_file).decode()

    url = (
    f"https://api.clarifai.com/v2/users/{USER_ID}/apps/{APP_ID}"
    f"/models/{MODEL_ID}/versions/{MODEL_VERSION_ID}/outputs"
)
    headers = {
        "Authorization": f"Key {CLARIFAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": [
            {
                "data": {
                    "image": {"base64": img_b64}
                }
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    try:
        concepts = result["outputs"][0]["data"]["concepts"]
        ingredients = [
            {"ingredient": c["name"], "confidence": c["value"]}
            for c in concepts
        ]
    except:
        ingredients = []

    return jsonify({"ingredients": ingredients})


if __name__ == "__main__":
    # For production deploys (e.g., Render), host/port should come from env.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
