import os
import uuid
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zep_cloud.client import Zep
from zep_cloud.types import Message
import traceback

# Cargar claves y configuraciones desde variables de entorno
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ZEP_API_KEY = os.getenv("ZEP_API_KEY")
SESSION_ID = os.getenv("SESSION_ID", uuid.uuid4().hex)
USER_ID = "usuario"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Verificación básica
if not OPENROUTER_API_KEY:
    raise RuntimeError("La variable de entorno OPENROUTER_API_KEY no está definida.")
if not ZEP_API_KEY:
    raise RuntimeError("La variable de entorno ZEP_API_KEY no está definida.")

# Cliente de memoria Zep
zep_client = Zep(api_key=ZEP_API_KEY)

# Instancia de FastAPI
app = FastAPI()

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

async def query_openrouter(messages_texts):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    content_list = [{"type": "text", "text": txt} for txt in messages_texts]
    payload = {
        "model": "qwen/qwen2.5-72b-instruct:free",
        "messages": [{"role": "user", "content": content_list}],
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

@app.post("/chat", response_model=ChatResponse)
async def chatear(request: ChatRequest):
    try:
        # Registro del usuario en Zep (opcional pero útil)
        try:
            zep_client.user.add(
                user_id=USER_ID,
                email="usuario@example.com",
                first_name="Miku",
                last_name="User"
            )
        except Exception:
            pass

        # Crear sesión si no existe
        try:
            sesiones = zep_client.memory.list_sessions(page_size=100, page_number=1)
            if SESSION_ID not in [s.session_id for s in sesiones.sessions]:
                zep_client.memory.add_session(session_id=SESSION_ID, user_id=USER_ID)
        except Exception:
            pass

        # Guardar mensaje del usuario
        try:
            mensaje_usuario = Message(
                role="Miku",
                content=request.mensaje,
                role_type="user"
            )
            zep_client.memory.add(SESSION_ID, messages=[mensaje_usuario])
        except Exception:
            pass

        # Obtener contexto previo si existe
        contexto = ""
        try:
            memoria = zep_client.memory.get(session_id=SESSION_ID)
            contexto = memoria.context or ""
        except Exception:
            pass

        # Preparar mensajes para enviar al modelo
        mensajes_para_llm = []
        if contexto:
            mensajes_para_llm.append(contexto)
        mensajes_para_llm.append(request.mensaje)

        # Consultar al modelo
        respuesta_llm = await query_openrouter(mensajes_para_llm)

        # Guardar respuesta del asistente
        try:
            mensaje_asistente = Message(
                role="Asistente Miku",
                content=respuesta_llm,
                role_type="assistant"
            )
            zep_client.memory.add(SESSION_ID, messages=[mensaje_asistente])
        except Exception:
            pass

        return {"respuesta": respuesta_llm}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
