"""
SERVER.PY - Servidor FastAPI para manejar llamadas de Twilio
Recibe las llamadas, ejecuta el flujo del agente y genera resultados
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from pydantic import BaseModel

# Importar agentes
import sys
sys.path.insert(0, str(Path(__file__).parent))
from agente.cliente_flow import clasificar_respuesta_cliente, generar_mensaje_validacion_fallida
from agente.referencia_flow import (
    clasificar_respuesta_referencia,
    generar_mensaje_resultado_referencia,
    clasificar_parentesco
)
from agente.message_generator import generar_resultado_final_cliente

app = FastAPI(title="Agente de Validación de Crédito")

# Almacenamiento en memoria para datos de la llamada
llamadas_pendientes = {}
resultados_globales = []


class DatosCliente(BaseModel):
    nombre_cliente: str
    cedula: str
    telefono_cliente: str
    telefono_ref1: str
    telefono_ref2: str
    nombre_ref1: str
    nombre_ref2: str


class DatosReferencia(BaseModel):
    nombre_ref: str
    telefono_ref: str
    nombre_cliente: str


def guardar_resultado(resultado: dict):
    """Guarda resultado en archivo JSON"""
    carpeta = Path(__file__).parent / "resultados"
    carpeta.mkdir(exist_ok=True)

    nombre = resultado.get("nombre_cliente", "desconocido").replace(" ", "_")
    ruta = carpeta / f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    resultados_globales.append(resultado)


# ========================
# ENDPOINTS DE TWILIO
# ========================

@app.post("/llamada-cliente")
async def iniciar_llamada_cliente(datos: DatosCliente):
    """
    Inicia una llamada al cliente titular
    """
    # Guardar datos para usar en el TwiML
    datos_dict = datos.model_dump()
    llamadas_pendientes["cliente_actual"] = datos_dict

    return {
        "mensaje": "Datos guardados. Ahora necesitas exponer el servidor con ngrok.",
        "numero": datos.telefono_cliente,
        "proximo_paso": "Ejecuta: ngrok http 8000"
    }


@app.get("/twiml-cliente")
async def twiml_cliente(request: Request):
    """
    Genera el TwiML para la llamada al cliente
    Twilio llama a este endpoint para saber qué decir
    """
    datos = llamadas_pendientes.get("cliente_actual", {})

    if not datos:
        raise HTTPException(status_code=404, detail="No hay datos del cliente")

    respuesta = VoiceResponse()

    # Saludo
    respuesta.say(
        f"Hola, buen día, ¿hablo con {datos.get('nombre_cliente', '')}?",
        voice="alice",
        language="es-ES"
    )
    respuesta.pause(length=1)

    # Aviso legal
    respuesta.say(
        "Mi nombre es Agente, te llamo del área de validación de crédito. "
        "Te informo que esta llamada está siendo grabada y monitoreada por seguridad.",
        voice="alice",
        language="es-ES"
    )
    respuesta.pause(length=1)

    # Validación de identidad
    respuesta.say(
        f"¿Eres el titular de la cédula número {datos.get('cedula', '')}? "
        f"¿Confirmas que este es tu número principal?",
        voice="alice",
        language="es-ES"
    )
    respuesta.pause(length=2)

    # Información del crédito
    respuesta.say(
        "Estamos validando tu solicitud de financiamiento para la adquisición de un equipo.",
        voice="alice",
        language="es-ES"
    )
    respuesta.pause(length=1)

    # Condiciones
    respuesta.say(
        "En caso de incumplimiento o atraso en las cuotas, el equipo podrá ser bloqueado automáticamente. "
        "Para evitar inconvenientes, debes cumplir con los pagos en las fechas acordadas.",
        voice="alice",
        language="es-ES"
    )
    respuesta.pause(length=1)

    # Confirmación
    respuesta.say(
        "¿Estás de acuerdo con las condiciones? "
        "¿Te comprometes a cumplir con los pagos?",
        voice="alice",
        language="es-ES"
    )

    # Grabar respuesta del cliente
    respuesta.record(
        action="/grabacion-cliente",
        method="POST",
        max_length="30",
        timeout="10",
        play_beep="true"
    )

    return Response(content=str(respuesta), media_type="application/xml")


@app.post("/grabacion-cliente")
async def grabacion_cliente(
    RecordingUrl: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None),
    From: Optional[str] = Form(None)
):
    """
    Recibe la grabación o dígitos del cliente
    """
    datos = llamadas_pendientes.get("cliente_actual", {})

    # Por simplicidad, asumimos que aceptó (en producción, analizas la grabación)
    resultado_cliente = {
        "identidad_validada": True,
        "acepta_condiciones": True,
        "respuesta": "ACEPTA",
        "grabacion_url": RecordingUrl,
        "call_sid": CallSid
    }

    # Guardar resultado del cliente
    llamadas_pendientes["resultado_cliente"] = resultado_cliente

    # Ahora llamar a la primera referencia
    return await iniciar_llamada_referencia_1(datos)


async def iniciar_llamada_referencia_1(datos_cliente: dict):
    """Llama a la primera referencia"""
    from telefonia.twilio_client import ClienteTwilio

    datos_ref = {
        "nombre_ref": datos_cliente.get("nombre_ref1", ""),
        "telefono_ref": datos_cliente.get("telefono_ref1", ""),
        "nombre_cliente": datos_cliente.get("nombre_cliente", "")
    }

    llamadas_pendientes["referencia_actual"] = datos_ref

    # En producción, aquí harías la llamada real
    # Por ahora, simulamos
    resultado_ref1 = clasificar_respuesta_referencia("SI", "amigo", "SI", "SI")
    llamadas_pendientes["resultado_ref1"] = resultado_ref1

    # Llamar a segunda referencia
    return await iniciar_llamada_referencia_2(datos_cliente)


async def iniciar_llamada_referencia_2(datos_cliente: dict):
    """Llama a la segunda referencia"""
    datos_ref = {
        "nombre_ref": datos_cliente.get("nombre_ref2", ""),
        "telefono_ref": datos_cliente.get("telefono_ref2", ""),
        "nombre_cliente": datos_cliente.get("nombre_cliente", "")
    }

    # Simular resultado
    resultado_ref2 = clasificar_respuesta_referencia("SI", "hermano", "SI", "SI")
    llamadas_pendientes["resultado_ref2"] = resultado_ref2

    # Generar resultado final
    return await generar_resultado_final(datos_cliente)


async def generar_resultado_final(datos_cliente: dict):
    """Genera el resultado final de la validación"""
    resultado_cliente = llamadas_pendientes.get("resultado_cliente", {})
    resultado_ref1 = llamadas_pendientes.get("resultado_ref1", {})
    resultado_ref2 = llamadas_pendientes.get("resultado_ref2", {})

    mensaje = generar_resultado_final_cliente(
        datos_cliente,
        resultado_cliente.get("identidad_validada", False),
        resultado_cliente.get("acepta_condiciones", False),
        resultado_ref1,
        resultado_ref2
    )

    resultado_final = {
        "nombre_cliente": datos_cliente.get("nombre_cliente"),
        "cedula": datos_cliente.get("cedula"),
        "telefono_cliente": datos_cliente.get("telefono_cliente"),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "identidad_validada": resultado_cliente.get("identidad_validada", False),
        "acepta_condiciones": resultado_cliente.get("acepta_condiciones", False),
        "referencias": [
            {"nombre": datos_cliente.get("nombre_ref1"), "resultado": resultado_ref1},
            {"nombre": datos_cliente.get("nombre_ref2"), "resultado": resultado_ref2}
        ],
        "mensaje_whatsapp": mensaje
    }

    guardar_resultado(resultado_final)

    return {
        "resultado": "VALIDACIÓN COMPLETADA",
        "mensaje": mensaje
    }


# ========================
# ENDPOINTS DE STATUS
# ========================

@app.get("/")
async def root():
    return {
        "mensaje": "Agente de Validación de Crédito",
        "estado": "Activo",
        "documentacion": "/docs"
    }


@app.get("/resultados")
async def ver_resultados():
    """Ver todos los resultados guardados"""
    return {"resultados": resultados_globales}


@app.post("/llamada-simple")
async def llamada_simple(
    nombre_cliente: str,
    telefono: str,
    cedula: str
):
    """
    Endpoint simple para hacer una llamada de prueba
    Sirve para probar la conexión con Twilio
    """
    from telefonia.twilio_client import ClienteTwilio

    cliente_twilio = ClienteTwilio()

    # Guardar datos
    datos = {
        "nombre_cliente": nombre_cliente,
        "cedula": cedula,
        "telefono_cliente": telefono
    }
    llamadas_pendientes["cliente_actual"] = datos

    return {
        "mensaje": "Usa ngrok para exponer este servidor y luego llama a /twiml-cliente",
        "datos": datos,
        "nota": "Necesitas un servidor público (ngrok) para que Twilio pueda acceder a este servidor"
    }


# ========================
# EJECUTAR SERVIDOR
# ========================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor...")
    print("📍 Accede a http://localhost:8000/docs para ver la documentación")
    uvicorn.run(app, host="0.0.0.0", port=8000)
