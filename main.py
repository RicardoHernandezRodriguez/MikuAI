import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

@app.post("/chat", response_model=ChatResponse)
def query(request: ChatRequest):
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
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))  # Lee variable PORT o usa 10000
    uvicorn.run("main:app", host="0.0.0.0", port=port)
