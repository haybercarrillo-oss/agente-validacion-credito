"""
SERVER.PY - Servidor FastAPI para manejar llamadas de Twilio
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

app = FastAPI(title="Agente de Validación de Crédito")

resultados_globales = []


def guardar_resultado(resultado: dict):
    carpeta = Path(__file__).parent / "resultados"
    carpeta.mkdir(exist_ok=True)
    nombre = resultado.get("nombre_cliente", "desconocido").replace(" ", "_")
    ruta = carpeta / f"{nombre}_{datetime.now().strftime('%Y%m%%d_%H%M%S')}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    resultados_globales.append(resultado)


# ========================
# ENDPOINTS DE TWILIO
# ========================

@app.get("/twiml-cliente")
async def twiml_cliente(
    nombre: str = "",
    cedula: str = "",
    telefono: str = ""
):
    """
    Genera el TwiML para la llamada al cliente.
    Los datos se pasan como query parameters.
    Ejemplo: /twiml-cliente?nombre=Juan&cedula=123&telefono=+57300
    """
    if not nombre:
        raise HTTPException(status_code=400, detail="Falta nombre del cliente")

    respuesta = VoiceResponse()

    # Saludo
    respuesta.say(
        f"Hola, buen día, ¿hablo con {nombre}?",
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
        f"¿Eres el titular de la cédula número {cedula}? "
        f"¿Confirmas que este es tu número principal {telefono}?",
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

    # Cierre
    respuesta.say(
        "Gracias por tu atención. Un asesor se comunicará contigo pronto. ¡Hasta luego!",
        voice="alice",
        language="es-ES"
    )
    respuesta.hangup()

    return Response(content=str(respuesta), media_type="application/xml")


@app.get("/twiml-referencia")
async def twiml_referencia(
    nombre_ref: str = "",
    nombre_cliente: str = ""
):
    """TwiML para llamada a referencia"""
    if not nombre_ref or not nombre_cliente:
        raise HTTPException(status_code=400, detail="Faltan datos")

    respuesta = VoiceResponse()

    respuesta.say(f"Hola, buen día, ¿con quién tengo el gusto?", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say(f"¿Eres {nombre_ref}?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say(
        "Te llamo del área de validación de crédito. "
        "Esta llamada está siendo grabada por seguridad.",
        voice="alice", language="es-ES"
    )
    respuesta.pause(length=1)
    respuesta.say(f"¿Conoces a {nombre_cliente}?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("¿Qué tipo de relación tienes con esa persona?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("¿Sabes si actualmente está trabajando o generando ingresos?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say(
        "En caso de no lograr contacto, ¿autorizas que te contactemos para dejarle razón?",
        voice="alice", language="es-ES"
    )
    respuesta.say("Muchas gracias por tu tiempo.", voice="alice", language="es-ES")
    respuesta.hangup()

    return Response(content=str(respuesta), media_type="application/xml")


# ========================
# ENDPOINTS DE STATUS
# ========================

@app.get("/")
async def root():
    return {
        "mensaje": "Agente de Validación de Crédito",
        "estado": "Activo",
        "uso": "Usa /twiml-cliente?nombre=XXX&cedula=XXX&telefono=XXX"
    }


@app.get("/resultados")
async def ver_resultados():
    return {"resultados": resultados_globales}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
