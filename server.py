"""
SERVER.PY - Agente Interactivo de Validación de Crédito
Hace preguntas una por una y detecta respuestas (sí/no)
"""

import os
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from pydantic import BaseModel

app = FastAPI(title="Agente Interactivo de Validación")

resultados_globales = []


# ========================
# PREGUNTAS DEL AGENTE
# ========================

def paso_1_saludo(nombre: str) -> str:
    """Paso 1: Saludo inicial"""
    twiml = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        action="/respuesta?paso=1",
        method="POST",
        timeout="10",
        speechTimeout="7",
        language="es-CO"
    )
    gather.say(
        f"Hola, muy buenos días. ¿Habla usted con {nombre}?",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.append(gather)
    # Si no responde, repetir
    twiml.say("Le pido que por favor confirme si está presente.", voice="Polly.Marta", language="es-CO")
    twiml.redirect("/respuesta?paso=1")
    return str(twiml)


def paso_2_identidad(cedula: str, telefono: str) -> str:
    """Paso 2: Validar identidad"""
    twiml = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        action="/respuesta?paso=2",
        method="POST",
        timeout="5",
        speechTimeout="5",
        language="es-CO"
    )
    gather.say(
        f"Por favor confirme: ¿Es usted el titular de la cédula número {cedula}? "
        f"¿Este número {telefono} es su número principal de contacto?",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.append(gather)
    twiml.say("No se detectaron respuestas. Por favor responda sí o no.", voice="Polly.Marta", language="es-CO")
    twiml.redirect("/respuesta?paso=2")
    return str(twiml)


def paso_3_informacion() -> str:
    """Paso 3: Informar sobre el crédito"""
    twiml = VoiceResponse()
    twiml.say(
        "Nos encontramos validando su solicitud de financiamiento "
        "para la adquisición de un equipo tecnológico.",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.pause(length=1)
    twiml.redirect("/respuesta?paso=3")
    return str(twiml)


def paso_4_condiciones() -> str:
    """Paso 4: Explicar condiciones"""
    twiml = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        action="/respuesta?paso=4",
        method="POST",
        timeout="5",
        speechTimeout="5",
        language="es-CO"
    )
    gather.say(
        "Es importante que conozca las condiciones: "
        "En caso de incumplimiento o atraso en el pago, el equipo será bloqueado automáticamente. "
        "¿Está usted de acuerdo con estas condiciones?",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.append(gather)
    twiml.say("Por favor confirme si acepta las condiciones.", voice="Polly.Marta", language="es-CO")
    twiml.redirect("/respuesta?paso=4")
    return str(twiml)


def paso_5_compromiso() -> str:
    """Paso 5: Confirmar compromiso"""
    twiml = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        action="/respuesta?paso=5",
        method="POST",
        timeout="5",
        speechTimeout="5",
        language="es-CO"
    )
    gather.say(
        "¿Se compromete a cumplir con los pagos en las fechas establecidas?",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.append(gather)
    twiml.say("Por favor responda sí o no.", voice="Polly.Marta", language="es-CO")
    twiml.redirect("/respuesta?paso=5")
    return str(twiml)


def paso_final() -> str:
    """Paso final: Despedida"""
    twiml = VoiceResponse()
    twiml.say(
        "Gracias por su atención. Sus respuestas han sido registradas exitosamente. "
        "Un asesor se comunicará con usted prontamente. "
        "Que tenga un excelente día. Hasta luego.",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.hangup()
    return str(twiml)


def paso_no_respondio() -> str:
    """Cuando no hay respuesta"""
    twiml = VoiceResponse()
    twiml.say(
        "No se detectaron respuestas. La llamada será finalizada. "
        "Gracias por su tiempo.",
        voice="Polly.Marta",
        language="es-CO"
    )
    twiml.hangup()
    return str(twiml)


def clasificar_respuesta(texto: str) -> str:
    """Clasifica la respuesta como sí, no, o inválido"""
    if not texto:
        return "NSNC"  # No sabe / No contesta

    texto = texto.lower().strip()

    # Positivos
    if any(p in texto for p in ["sí", "si", "si!", "sip", "correcto", "si señor", "si señora", "exacto", "afirmativo", "así es", "asies", "yes"]):
        return "SI"

    # Negativos
    if any(p in texto for p in ["no", "nop", "no!", "negativo", "incorrecto", "nop", "nah"]):
        return "NO"

    return "NSNC"


# ========================
# ALMACENAMIENTO DE RESPUESTAS
# ========================

respuestas_cliente = {}


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
    Inicia el flujo de llamada al cliente
    """
    if not nombre:
        raise HTTPException(status_code=400, detail="Falta nombre del cliente")

    # Guardar datos
    respuestas_cliente["nombre"] = nombre
    respuestas_cliente["cedula"] = cedula
    respuestas_cliente["telefono"] = telefono
    respuestas_cliente["respuestas"] = {}

    twiml = paso_1_saludo(nombre)
    return Response(content=twiml, media_type="application/xml")


@app.post("/respuesta")
async def manejar_respuesta(
    Digits: str = Form(None),
    SpeechResult: str = Form(None),
    CallSid: str = Form(None),
    paso: str = Form("1")
):
    """
    Maneja las respuestas del cliente
    """
    # Obtener respuesta (DTMF o voz)
    respuesta_texto = SpeechResult or Digits or ""
    respuesta = clasificar_respuesta(respuesta_texto)

    paso_int = int(paso)
    respuestas_cliente["respuestas"][f"paso_{paso_int}"] = {
        "texto_original": respuesta_texto,
        "clasificado": respuesta
    }

    # Decidir siguiente paso
    if paso_int == 1:
        if respuesta == "SI":
            return Response(content=paso_2_identidad(
                respuestas_cliente["cedula"],
                respuestas_cliente["telefono"]
            ), media_type="application/xml")
        else:
            return Response(content=paso_no_respondio(), media_type="application/xml")

    elif paso_int == 2:
        if respuesta == "SI":
            return Response(content=paso_3_informacion(), media_type="application/xml")
        else:
            return Response(content=paso_no_respondio(), media_type="application/xml")

    elif paso_int == 3:
        return Response(content=paso_4_condiciones(), media_type="application/xml")

    elif paso_int == 4:
        if respuesta == "SI":
            return Response(content=paso_5_compromiso(), media_type="application/xml")
        else:
            return Response(content=paso_no_respondio(), media_type="application/xml")

    elif paso_int == 5:
        if respuesta == "SI":
            # Guardar resultado exitoso
            guardar_validacion_exitosa()
            return Response(content=paso_final(), media_type="application/xml")
        else:
            return Response(content=paso_no_respondio(), media_type="application/xml")

    return Response(content=paso_final(), media_type="application/xml")


def guardar_validacion_exitosa():
    """Guarda el resultado de la validación"""
    datos = respuestas_cliente
    resultado = {
        "nombre_cliente": datos.get("nombre"),
        "cedula": datos.get("cedula"),
        "telefono": datos.get("telefono"),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "identidad_validada": True,
        "acepta_condiciones": True,
        "compromete_pagos": True,
        "respuestas": datos.get("respuestas", {}),
        "estado": "APROBADO"
    }

    carpeta = Path("resultados")
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / f"validacion_{datos.get('nombre', 'desconocido').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    resultados_globales.append(resultado)


# ========================
# ENDPOINTS DE STATUS
# ========================

@app.get("/")
async def root():
    return {
        "mensaje": "Agente Interactivo de Validación",
        "estado": "Activo",
        "endpoints": {
            "cliente": "/twiml-cliente?nombre=XXX&cedula=XXX&telefono=XXX",
            "resultados": "/resultados"
        }
    }


@app.get("/resultados")
async def ver_resultados():
    return {"resultados": resultados_globales}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
