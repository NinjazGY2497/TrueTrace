import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

HF_KEY = os.getenv("HF_KEY")
if not HF_KEY:
    raise ValueError("HF_KEY is not set in backEnd/.env")

CHAT_API_URL = "https://router.huggingface.co/v1/chat/completions"
IMAGE_API_URL = "https://router.huggingface.co/hf-inference/models/Organika/sdxl-detector"

app = Flask(__name__)
CORS(app)


def callHFAPI(url, *, data=None, json_payload=None, headers=None, timeout=30):
    requestHeaders = {"Authorization": f"Bearer {HF_KEY}"}
    if headers:
        requestHeaders.update(headers)

    response = requests.post(
        url,
        headers=requestHeaders,
        data=data,
        json=json_payload,
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(payload["error"])
    return payload


def normalize_label(value):
    text = str(value or "").lower()
    if any(token in text for token in ("ai", "artificial", "generated", "synthetic")):
        return "ai"
    return "human"


def parse_json_output(text):
    text = str(text or "").strip()
    if not text.startswith("{") or not text.endswith("}"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]
    return json.loads(text)


def normalize_response(label, confidence, reasons):
    label = normalize_label(label)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(confidence, 1.0))

    if not isinstance(reasons, list):
        reasons = [str(reasons)]
    if not reasons:
        reasons = ["No explanation was provided by the model."]

    return label, confidence, reasons


def request_image_model(image_file):
    if image_file is None:
        raise ValueError("Image file is required.")

    headers = {"Content-Type": image_file.content_type or "image/png"}
    image_bytes = image_file.read()
    payload = callHFAPI(IMAGE_API_URL, data=image_bytes, headers=headers)

    entry = None
    if isinstance(payload, list) and payload:
        entry = payload[0]
    elif isinstance(payload, dict):
        entry = payload

    label = normalize_label(entry.get("label") if isinstance(entry, dict) else None)
    confidence = (entry.get("score") or entry.get("confidence") or 0.0) if isinstance(entry, dict) else 0.0
    reasons = [
        "The image appears to contain natural detail and texture consistent with a real photo."
    ]
    if label == "ai":
        reasons = [
            "The image shows patterns more consistent with AI-generated characteristics.",
            "The classifier is more confident about synthetic image features than natural photography."
        ]

    return normalize_response(label, confidence, reasons)


def request_text_model(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text content is required for analysis.")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a forensic linguist. Analyze the provided text and determine whether it is AI-generated or human-written. "
                "Return only a JSON object with exactly these fields: label, confidence, and reasons. "
                "label must be \"human\" or \"ai\". confidence must be a number between 0 and 1. "
                "reasons must be a list of short explanation strings."
            )
        },
        {
            "role": "user",
            "content": f"Text:\n{text}\n\nRespond with a JSON object only. Do not add any extra text."
        }
    ]

    payload = callHFAPI(
        CHAT_API_URL,
        json_payload={
            "model": "openai/gpt-oss-120b:fastest",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 300,
        },
    )

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("Text API returned unexpected response data.")

    assistant_text = choices[0].get("message", {}).get("content", "")
    try:
        parsed = parse_json_output(assistant_text)
    except Exception:
        return normalize_response(
            assistant_text,
            0.5,
            [
                "The model response could not be parsed as JSON, so this result is a fallback interpretation.",
                assistant_text.strip()[:200],
            ],
        )

    return normalize_response(
        parsed.get("label"),
        parsed.get("confidence", 0.0),
        parsed.get("reasons", []),
    )


@app.route("/text-detect", methods=["POST"])
def text_detect():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload.get("text"):
        return jsonify({"error": "Request body must be JSON with a non-empty text field."}), 400

    try:
        label, confidence, reasons = request_text_model(payload["text"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"label": label, "confidence": confidence, "reasons": reasons})


@app.route("/image-detect", methods=["POST"])
def image_detect():
    image_file = request.files.get("file")
    if image_file is None:
        return jsonify({"error": "Image file field 'file' is required."}), 400

    try:
        label, confidence, reasons = request_image_model(image_file)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"label": label, "confidence": confidence, "reasons": reasons})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2497)
