import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

if not API_KEY:
    raise RuntimeError("La variable de entorno OPENROUTER_API_KEY no está definida.")

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "qwen/qwen2.5-vl-72b-instruct:free",
        "messages": [
            {"role": "user", "content": request.mensaje}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        respuesta = data["choices"][0]["message"]["content"]
        return {"respuesta": respuesta}
    except requests.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=f"Error HTTP: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
