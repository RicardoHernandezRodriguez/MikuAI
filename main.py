from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

API_KEY = "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"

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        # Opcional, puedes poner tu dominio o app aquí o dejarlos vacíos:
        "HTTP-Referer": "https://tu-sitio.com",
        "X-Title": "TuAppNombre",
    }
    data = {
        "model": "qwen/qwen-2.5-72b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": request.mensaje
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        resp_json = response.json()
        respuesta = resp_json["choices"][0]["message"]["content"]
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
