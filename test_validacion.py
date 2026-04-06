"""
TEST_VALIDACION.PY - Prueba de validación con datos reales
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://agente-validacion.onrender.com"

# Datos del cliente a validar
datos_cliente = {
    "nombre_cliente": "Vega Hernández vldamir",
    "cedula": "1092084218",
    "telefono_cliente": "+573502977483",
    "telefono_ref1": "+573502977483",
    "telefono_ref2": "+573502977483",
    "nombre_ref1": "Rusmira Baron",
    "nombre_ref2": "Yilibeth Vega"
}

def probar_wake_up():
    """Despierta el servicio"""
    print("🔄 Despertando servicio en Render...")
    try:
        r = requests.get(BASE_URL, timeout=60)
        print(f"✅ Servicio activo: {r.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_llamada_cliente():
    """Prueba el flujo de llamada al cliente"""
    print("\n📞 Probando flujo de llamada al cliente...")

    try:
        # Primero verificamos que el TwiML responde
        r = requests.get(f"{BASE_URL}/twiml-cliente", timeout=60)
        if r.status_code == 200:
            print(f"✅ TwiML del cliente responde correctamente")
            print(f"📄 Respuesta (primeros 500 chars):")
            print(r.text[:500])
            return True
        else:
            print(f"❌ TwiML responde con código: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generar_resultado_local():
    """Genera el resultado localmente (sin llamada real)"""
    print("\n🧠 Generando resultado de validación (simulación)...")

    import sys
    sys.path.insert(0, ".")
    from agente.cliente_flow import obtener_todos_los_pasos
    from agente.referencia_flow import clasificar_respuesta_referencia
    from agente.message_generator import generar_resultado_final_cliente

    # Mostrar flujo
    print("\n📞 FLUJO LLAMADA CLIENTE:")
    pasos = obtener_todos_los_pasos(datos_cliente)
    for p in pasos:
        print(f"   Paso {p['paso']}: {p['texto'][:60]}...")

    # Clasificar referencias
    print("\n🔹 CLASIFICANDO REFERENCIA 1:")
    ref1 = clasificar_respuesta_referencia("SI", "amiga", "SI", "SI")
    print(f"   Resultado: {ref1['resultado']}")
    print(f"   Relación: {ref1['tipo_relacion']}")

    print("\n🔹 CLASIFICANDO REFERENCIA 2:")
    ref2 = clasificar_respuesta_referencia("SI", "hermana", "SI", "SI")
    print(f"   Resultado: {ref2['resultado']}")
    print(f"   Relación: {ref2['tipo_relacion']}")

    # Generar resultado final
    print("\n📊 RESULTADO FINAL:")
    resultado = generar_resultado_final_cliente(
        datos_cliente,
        True,  # identidad_validada
        True,  # acepta_condiciones
        ref1,
        ref2
    )
    print(resultado)

    return resultado

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE VALIDACIÓN")
    print("=" * 60)
    print(f"\n📋 Datos: {datos_cliente['nombre_cliente']}")
    print(f"   CC: {datos_cliente['cedula']}")
    print(f"   Tel: {datos_cliente['telefono_cliente']}")
    print("=" * 60)

    # Generar resultado local
    generar_resultado_local()

    print("\n" + "=" * 60)
    print("💡 NOTA: Para validación REAL con llamada telefónica,")
    print("   llama al número Twilio: +16414496942")
    print("=" * 60)
