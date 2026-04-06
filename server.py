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
    ruta = carpeta / f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    resultados_globales.append(resultado)


def generar_saludo_formal(nombre: str, cedula: str, telefono: str) -> str:
    """Genera el TwiML completo con mensajes formales en español"""
    respuesta = VoiceResponse()

    # Configuración explícita para español
    respuesta.say(
        f"Hola, muy buenos días. ¿Habla usted con {nombre}?",
        voice="Polly.Marta",  # Voz en español
        language="es-CO",     # Español de Colombia (más claro)
        bargeIn="false"
    )
    respuesta.pause(length=1)

    # Presentación formal
    respuesta.say(
        "Le saluda el Departamento de Validaciones de Crédito. "
        "La presente llamada tiene como propósito verificar la información "
        "proporcionada por usted para el estudio de su solicitud de financiamiento.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    # Aviso legal
    respuesta.say(
        "Por favor tenga en cuenta que esta llamada está siendo grabada "
        "para seguridad y calidad del servicio.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    # Validación de identidad
    respuesta.say(
        f"Para continuar, necesito confirmar sus datos. "
        f"¿Es usted el titular de la cédula número {cedula}? "
        f"¿Este número de teléfono {telefono} es su número principal de contacto?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=2)

    # Información del crédito
    respuesta.say(
        "Nos encontramos validando su solicitud de financiamiento "
        "para la adquisición de un equipo tecnológico.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    # Condiciones
    respuesta.say(
        "Es importante que conozca las condiciones del crédito: "
        "En caso de incumplimiento o atraso en el pago de las cuotas, "
        "el equipo podrá ser bloqueado de forma automática. "
        "Para evitar cualquier inconveniente, usted debe cumplir "
        "con los pagos en las fechas acordadas.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    # Confirmación final
    respuesta.say(
        "Para finalizar, necesito su confirmación: "
        "¿Está usted de acuerdo con las condiciones mencionadas? "
        "¿Se compromete a cumplir con los pagos en las fechas establecidas?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=2)

    # Despedida
    respuesta.say(
        "Gracias por su atención. "
        "Sus respuestas han sido registradas exitosamente. "
        "Un asesor de nuestro equipo se comunicará con usted prontamente. "
        "Que tenga un excelente día. Hasta luego.",
        voice="Polly.Marta",
        language="es-CO"
    )

    respuesta.hangup()
    return str(respuesta)


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
    """
    if not nombre:
        raise HTTPException(status_code=400, detail="Falta nombre del cliente")

    twiml = generar_saludo_formal(nombre, cedula, telefono)
    return Response(content=twiml, media_type="application/xml")


@app.get("/twiml-referencia")
async def twiml_referencia(
    nombre_ref: str = "",
    nombre_cliente: str = ""
):
    """TwiML para llamada a referencia"""
    if not nombre_ref or not nombre_cliente:
        raise HTTPException(status_code=400, detail="Faltan datos")

    respuesta = VoiceResponse()

    respuesta.say(
        f"Muy buenos días. ¿Con quién tengo el gusto de hablar?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    respuesta.say(
        f"¿Es usted {nombre_ref}?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=2)

    respuesta.say(
        "Le saluda el Departamento de Validaciones de Crédito. "
        "Por favor tenga en cuenta que esta llamada está siendo grabada.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    respuesta.say(
        f"Nos encontramos validando la información de {nombre_cliente}, "
        f"quien ha proporcionado sus datos como referencia personal.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    respuesta.say(
        "¿Usted conoce personalmente a esta persona?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=2)

    respuesta.say(
        "¿Qué tipo de relación tiene usted con ella?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=2)

    respuesta.say(
        "¿Sabe si actualmente cuenta con un empleo o alguna fuente de ingresos?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=2)

    respuesta.say(
        "En caso de que esta persona no sea contactada o presente atrasos en sus pagos, "
        "¿nos autoriza a comunicarnos con usted para dejarle un mensaje?",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.pause(length=1)

    respuesta.say(
        "Muchas gracias por su tiempo y colaboración. "
        "Que tenga un excelente día.",
        voice="Polly.Marta",
        language="es-CO"
    )
    respuesta.hangup()

    return Response(content=str(respuesta), media_type="application/xml")


# ========================
# ENDPOINTS DE STATUS
# ========================

@app.get("/")
async def root():
    return {
        "mensaje": "Agente de Validación de Crédito",
        "estado": "Activo"
    }


@app.get("/resultados")
async def ver_resultados():
    return {"resultados": resultados_globales}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
