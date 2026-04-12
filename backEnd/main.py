import json
from typing import Literal
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
import requests
import os
from groq import Groq
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

try:
    HF_KEY = os.getenv("HF_KEY")
except Exception:
    print(f"**main.py** - ERROR - Failed to load Hugging Face API key env.")
    raise

try:
    GROQ_KEY = os.getenv("GROQ_KEY")
    client = Groq(api_key=GROQ_KEY)
except Exception:
    print(f"**main.py** - ERROR - Failed to load Groq API key env.")
    raise

WHITELISTED_ORIGINS = ["http://127.0.0.1:5500", "http://localhost:5500"] # Remove localhost urls in production !!
IMAGE_API_URL = "https://router.huggingface.co/hf-inference/models/Organika/sdxl-detector"


class TextDetectionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    label: Literal['human', 'ai'] = Field(..., description="The classification of the text")
    confidence: float = Field(..., description="The detection certainty as a percentage")

app = Flask(__name__)

CORS(app, origins=WHITELISTED_ORIGINS)

def requestImageModel(img):
    headers = {
        "Authorization": f"Bearer {HF_KEY}",
        "Content-Type": img.content_type or "image/png"
    }

    imgBytes = img.read()
    response = requests.post(IMAGE_API_URL, headers=headers, data=imgBytes)
    
    data = response.json()
    label = data[0]['label']
    score = data[0]['score']

    print(f"**main.py** - INFO - {data}")
    
    return label, score

def requestTextModel(text):
    systemPrompt = (
        'You are a forensic linguist. Analyze the provided text for AI signatures (like perfect grammar and robotic transitions) versus human markers (like typos or unique phrasing).\n' 
        'Return ONLY a JSON object:\n'
        '{\n'
        '  "label": "human" or "ai",\n'
        '  "confidence": [float 0-100]\n'
        '}'
    )

    userPrompt = (
        f"Analyze the following text: \n'{text}'"
    )
    
    chatCompletion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ],
        
        model="meta-llama/llama-4-scout-17b-16e-instruct", 
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "TextDetectionResponse",
                "strict": True,
                "schema": TextDetectionResponse.model_json_schema()
            }
        }
    )

    response = json.loads(chatCompletion.choices[0].message.content)

    print(response)

@app.route("/text-detect", methods=["POST"])
def textDetect():
    promptData = request.get_json()
    text = promptData.get("text") # !!! Remember, make client not able to input empty textbox

    result, confidence = requestTextModel(text)

    return {
        "label": result,
        "confidence": confidence
    }

@app.route("/image-detect", methods=["POST"])
def imageDetect():
    file = request.files["file"]

    result, confidence = requestImageModel(file)

    return {
        "label": result,
        "confidence": confidence
    }

if __name__ == "__main__":
    app.run(port="2497")