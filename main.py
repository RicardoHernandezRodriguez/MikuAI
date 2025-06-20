import os
import uuid
import json
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zep_cloud.client import Zep
from zep_cloud.types import Message

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

API_KEY_ZEP = os.getenv("ZEP_API_KEY")
USER_ID = os.getenv("USER_ID", "usuario_miku")
SESSION_ID = os.getenv("SESSION_ID")

# Inicializamos cliente Zep si API key existe
client = None
if API_KEY_ZEP:
    client = Zep(api_key=API_KEY_ZEP)

# Crear sesión si no existe
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
    # Guardar mensaje del usuario en Zep (si está configurado)
    if client:
        try:
            mensaje_usuario = Message(
                role="user",
                content=request.mensaje,
                role_type="user"
            )
            client.memory.add(SESSION_ID, messages=[mensaje_usuario])
        except Exception:
            pass

    # Obtener el contexto resumido desde Zep (memoria contextual)
    contexto = ""
    if client:
        try:
            memoria = client.memory.get(session_id=SESSION_ID)
            contexto = memoria.context or ""
        except Exception:
            contexto = ""

    # Construir mensajes para el LLM incluyendo el contexto
    openrouter_messages = [
        {"role": "system", "content": "Eres un asistente útil y amigable."}
    ]

    if contexto:
        # Incluir el contexto resumido como mensaje system para contexto general
        openrouter_messages.append({"role": "system", "content": f"Contexto del usuario: {contexto}"})

    # Mensaje actual del usuario
    openrouter_messages.append({"role": "user", "content": request.mensaje})

    # Llamar al LLM con los mensajes completos
    try:
        respuesta_llm = await query_openrouter(openrouter_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error llamando a OpenRouter: {e}")

    # Guardar la respuesta del asistente en Zep
    if client:
        try:
            mensaje_asistente = Message(
                role="assistant",
                content=respuesta_llm,
                role_type="assistant"
            )
            client.memory.add(SESSION_ID, messages=[mensaje_asistente])
        except Exception:
            pass

    return {"respuesta": respuesta_llm}
