import logging
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mikuapi")

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen2.5-vl-72b-instruct:free"

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

@app.get("/")
async def root():
    return {"message": "Hellow"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.debug(f"Recibido mensaje: {request.mensaje}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": request.mensaje}]
            }
        ]
    }

    logger.debug(f"Payload para OpenRouter: {payload}")

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        logger.debug(f"Respuesta HTTP: {response.status_code}")
        response.raise_for_status()  # Lanza error si status no es 200 OK
        data = response.json()
        logger.debug(f"Respuesta JSON: {data}")

        # Extraemos la respuesta del modelo
        respuesta = data["choices"][0]["message"]["content"]
        logger.debug(f"Respuesta procesada: {respuesta}")

        return ChatResponse(respuesta=respuesta)

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err} - Respuesta: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
