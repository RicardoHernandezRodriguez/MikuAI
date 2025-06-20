import os
import uuid
import json
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zep_cloud.client import Zep
from zep_cloud.types import Message
import traceback

load_dotenv()

# Aquí pones tu API key fija directamente (cambia esta línea)
OPENROUTER_API_KEY = "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"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

API_KEY_ZEP = os.getenv("ZEP_API_KEY")
USER_ID = os.getenv("USER_ID", "usuario")
SESSION_ID = os.getenv("SESSION_ID")

client = None
if API_KEY_ZEP:
    client = Zep(api_key=API_KEY_ZEP)

if not SESSION_ID:
    SESSION_ID = uuid.uuid4().hex
    print(f"Nuevo SESSION_ID: {SESSION_ID}")

app = FastAPI()

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

async def query_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    json_data = {
        "model": "qwen/qwen-2.5-72b-instruct:free",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=30.0) as client_http:
        response = await client_http.post(OPENROUTER_URL, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

@app.post("/chat", response_model=ChatResponse)
async def chatear(request: ChatRequest):
    try:
        if client:
            try:
                client.user.add(
                    user_id=USER_ID,
                    email="usuario@example.com",
                    first_name="Miku",
                    last_name="User"
                )
            except Exception:
                pass

            try:
                sesiones = client.memory.list_sessions(page_size=100, page_number=1)
                if SESSION_ID not in [s.session_id for s in sesiones.sessions]:
                    client.memory.add_session(session_id=SESSION_ID, user_id=USER_ID)
            except Exception:
                pass

            try:
                mensaje_usuario = Message(
                    role="Miku",
                    content=request.mensaje,
                    role_type="user"
                )
                client.memory.add(SESSION_ID, messages=[mensaje_usuario])
            except Exception:
                pass

        contexto = ""
        if client:
            try:
                memoria = client.memory.get(session_id=SESSION_ID)
                contexto = memoria.context or ""
            except Exception:
                contexto = ""

        openrouter_messages = [
            {"role": "system", "content": "Eres un asistente útil y amigable."}
        ]
        if contexto:
            openrouter_messages.append({"role": "user", "content": contexto})

        openrouter_messages.append({"role": "user", "content": request.mensaje})

        respuesta_llm = await query_openrouter(openrouter_messages)

        if client:
            try:
                mensaje_asistente = Message(
                    role="Asistente Miku",
                    content=respuesta_llm,
                    role_type="assistant"
                )
                client.memory.add(SESSION_ID, messages=[mensaje_asistente])
            except Exception:
                pass

        return {"respuesta": respuesta_llm}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
