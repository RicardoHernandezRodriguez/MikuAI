from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class chatRequest(BaseModel):
    mensaje: str

class chatResponse(BaseModel):
    respuesta: str

@app.post("/chat", response_model=chatResponse)
def query(request: chatRequest):
    try:
        response = requests.post(
            url = "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
            },
            data = json.dumps({
                "model": "qwen/qwen2.5-vl-72b-instruct:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": request.mensaje
                            }
                        ]
                    }
                ]
            })
        )
        response.raise_for_status()
        data = response.json()
        contenido = data["choices"][0]["message"]["content"]
        return {"respuesta": contenido}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))