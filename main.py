from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Modelos de entrada/salida
class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

# Cliente OpenAI apuntando a OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": request.mensaje}]
                }
            ]
        )
        return {"respuesta": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
