"""
Cliente Twilio para realizar llamadas
Conecta el agente con la red telefónica
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Cargar variables de entorno
load_dotenv()

# Credenciales de Twilio (desde .env)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


class ClienteTwilio:
    """Cliente para realizar llamadas salientes"""

    def __init__(self):
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            raise ValueError("Faltan credenciales de Twilio. Verifica el archivo .env")
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.numero_origen = TWILIO_PHONE_NUMBER

    def hacer_llamada(self, numero_destino: str, url_twiml: str) -> dict:
        """
        Realiza una llamada saliente
        """
        try:
            llamada = self.client.calls.create(
                to=numero_destino,
                from_=self.numero_origen,
                url=url_twiml,
                method="POST",
                status_callback_event=["completed", "failed"],
                status_callback_method="POST"
            )
            return {
                "success": True,
                "call_sid": llamada.sid,
                "status": llamada.status,
                "numero": numero_destino
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "numero": numero_destino
            }

    def obtener_estado_llamada(self, call_sid: str) -> dict:
        """Obtiene el estado de una llamada"""
        try:
            llamada = self.client.calls(call_sid).fetch()
            return {
                "sid": llamada.sid,
                "status": llamada.status,
                "duration": llamada.duration,
                "numero": llamada.to
            }
        except Exception as e:
            return {"error": str(e)}

    def colgar_llamada(self, call_sid: str) -> bool:
        """Cuelga una llamada activa"""
        try:
            self.client.calls(call_sid).update(status="completed")
            return True
        except Exception:
            return False


def generar_twiml_cliente(datos: dict) -> str:
    """Genera TwiML para el flujo del cliente titular"""
    respuesta = VoiceResponse()
    respuesta.say(f"Hola, buen día, ¿hablo con {datos['nombre_cliente']}?", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say("Mi nombre es Agente, te llamo del área de validación de crédito. Te informo que esta llamada está siendo grabada.", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say(f"¿Eres el titular de la cédula número {datos['cedula']}? ¿Confirmas que este es tu número principal?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("Estamos validando tu solicitud de financiamiento para la adquisición de un equipo.", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say("En caso de incumplimiento, el equipo podrá ser bloqueado automáticamente. Para evitar inconvenientes, debes cumplir con los pagos.", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say("¿Estás de acuerdo con las condiciones? ¿Te comprometes a cumplir con los pagos?", voice="alice", language="es-ES")
    respuesta.record(action="/grabacion-cliente", method="POST", max_length="30", timeout="10")
    return str(respuesta)


def generar_twiml_referencia(datos_cliente: dict, datos_ref: dict) -> str:
    """Genera TwiML para el flujo de referencia"""
    respuesta = VoiceResponse()
    respuesta.say(f"Hola, buen día, ¿con quién tengo el gusto?", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say(f"¿Eres {datos_ref['nombre_ref']}?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("Te llamo del área de validación de crédito. Esta llamada está siendo grabada.", voice="alice", language="es-ES")
    respuesta.pause(length=1)
    respuesta.say(f"¿Conoces a {datos_cliente['nombre_cliente']}?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("¿Qué tipo de relación tienes con esa persona?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("¿Sabes si actualmente está trabajando o generando ingresos?", voice="alice", language="es-ES")
    respuesta.pause(length=2)
    respuesta.say("En caso de no lograr contacto, ¿autorizas que te contactemos para dejarle razón?", voice="alice", language="es-ES")
    respuesta.say("Muchas gracias por tu tiempo.", voice="alice", language="es-ES")
    respuesta.record(action="/grabacion-referencia", method="POST", max_length="60", timeout="15")
    return str(respuesta)


def generar_twiml_numero_invalido() -> str:
    """TwiML para cuando el número está apagado"""
    respuesta = VoiceResponse()
    respuesta.say("El número no está disponible.", voice="alice", language="es-ES")
    respuesta.hangup()
    return str(respuesta)
