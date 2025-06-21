from fastapi import FastAPI, HTTPException  # Importamos FastAPI y HTTPException para manejo de errores HTTP
from pydantic import BaseModel  # Usamos BaseModel para definir los modelos de datos
from openai import OpenAI  # Importamos el cliente oficial de OpenAI

app = FastAPI()  # Creamos la instancia de la aplicación FastAPI

# Modelo para recibir la petición JSON con el mensaje del usuario
class ChatRequest(BaseModel):
    mensaje: str  # Campo obligatorio 'mensaje' tipo string

# Modelo para enviar la respuesta JSON con la respuesta del asistente
class ChatResponse(BaseModel):
    respuesta: str  # Campo obligatorio 'respuesta' tipo string

# Instanciamos el cliente OpenAI con la API key y la URL base de OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # Aquí va tu API key hardcodeada
)

# Definimos la ruta POST /chat que recibe un ChatRequest y responde un ChatResponse
@app.post("/chat", response_model=ChatResponse)
def query(request: ChatRequest):
    try:
        # Creamos la conversación con el modelo, enviando el mensaje del usuario
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",  # Modelo que usaremos
            messages=[
                {
                    "role": "user",  # Rol del mensaje
                    "content": [
                        {
                            "type": "text",  # Tipo de contenido texto
                            "text": request.mensaje  # Texto que recibe desde la petición
                        }
                    ]
                }
            ],
            extra_body={}  # Parámetros extra si necesitas
        )
        # Retornamos la respuesta con el contenido del asistente
        return {"respuesta": completion.choices[0].message.content}

    except Exception as e:
        # Si hay algún error lanzamos una excepción HTTP 500 con el detalle del error
        raise HTTPException(status_code=500, detail=str(e))


# Para poder arrancar el servidor local con: python main.py
if __name__ == "__main__":
    import uvicorn  # Importamos uvicorn para correr el servidor ASGI
    uvicorn.run("main:app", host="0.0.0.0", port=10000)  # Ejecutamos en puerto 10000 y cualquier IP
