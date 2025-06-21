from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import traceback

app = FastAPI()

class chatRequest(BaseModel):
    mensaje: str

class chatResponse(BaseModel):
    respuesta: str

@app.post("/chat", response_model=chatResponse)
def query(request: chatRequest):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
            },
            data=json.dumps({
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
        traceback.print_exc()  # Aquí imprime el traceback completo en los logs
        raise HTTPException(status_code=500, detail=str(e))
