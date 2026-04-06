"""
HACER_LLAMADA.PY - Inicia una llamada real a través de Twilio
"""

import sys
sys.path.insert(0, ".")

from telefonia.twilio_client import ClienteTwilio
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

# Datos del cliente
CLIENTE = {
    "nombre_cliente": "María García López",
    "cedula": "9876543210",
    "telefono_cliente": "+573004520500",
}

# URL del servidor en Render con los datos URL-encoded
BASE_URL = "https://agente-validacion.onrender.com"

# URL-encode los parámetros
nombre_encoded = quote(CLIENTE['nombre_cliente'])
cedula_encoded = quote(CLIENTE['cedula'])
telefono_encoded = quote(CLIENTE['telefono_cliente'])

TWIML_URL = f"{BASE_URL}/twiml-cliente?nombre={nombre_encoded}&cedula={cedula_encoded}&telefono={telefono_encoded}"

def hacer_llamada():
    print("=" * 60)
    print("📞 INICIANDO LLAMADA REAL")
    print("=" * 60)
    print(f"📱 Llamando a: {CLIENTE['nombre_cliente']}")
    print(f"📞 Número: {CLIENTE['telefono_cliente']}")
    print(f"🔗 URL: {TWIML_URL}")
    print("=" * 60)

    try:
        cliente = ClienteTwilio()
        resultado = cliente.hacer_llamada(
            numero_destino=CLIENTE["telefono_cliente"],
            url_twiml=TWIML_URL
        )

        print("\n📡 Respuesta de Twilio:")
        print(f"   Success: {resultado.get('success')}")
        print(f"   Call SID: {resultado.get('call_sid')}")
        print(f"   Status: {resultado.get('status')}")

        if resultado.get("success"):
            print("\n✅ LLAMADA INICIADA CORRECTAMENTE")
            print(f"⏳ Contesten el teléfono...")
            return resultado
        else:
            print(f"\n❌ ERROR: {resultado.get('error')}")
            return None

    except Exception as e:
        print(f"\n❌ Error general: {e}")
        return None

if __name__ == "__main__":
    hacer_llamada()
