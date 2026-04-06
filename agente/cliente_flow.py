"""
Flujo de llamada para el CLIENTE TITULAR
Valida identidad, informa condiciones y confirma aceptación
"""

from datetime import datetime


def generar_saludo(nombre_cliente: str) -> dict:
    """Paso 1: Saludo + aviso legal"""
    hora = datetime.now().hour
    momento_dia = "buen día" if hora < 18 else "buen tarde"

    return {
        "paso": 1,
        "accion": "SALUDO",
        "texto": f"Hola, {momento_dia}, ¿hablo con {nombre_cliente}?",
        "espera_respuesta": True,
        "opciones": ["SI", "NO"]
    }


def generar_validacion_identidad(cedula: str, telefono_cliente: str) -> dict:
    """Paso 2: Validación de identidad"""
    return {
        "paso": 2,
        "accion": "VALIDACION_IDENTIDAD",
        "texto": f"Mi nombre es Agente, te llamo del área de validación de crédito. "
                  f"Te informo que esta llamada está siendo grabada y monitoreada por seguridad.\n\n"
                  f"¿Eres el titular de la cédula número {cedula}?\n"
                  f"¿Confirmas que este es tu número principal ({telefono_cliente})?",
        "espera_respuesta": True,
        "opciones": ["SI_COINCIDE", "NO_COINCIDE"]
    }


def generar_informacion_credito() -> dict:
    """Paso 3: Información del crédito"""
    return {
        "paso": 3,
        "accion": "INFORMACION_CREDITO",
        "texto": "Estamos validando tu solicitud de financiamiento para la adquisición de un equipo.",
        "espera_respuesta": False,
        "continuar": True
    }


def generar_condiciones() -> dict:
    """Paso 4: Condiciones importantes"""
    return {
        "paso": 4,
        "accion": "CONDICIONES",
        "texto": "En caso de incumplimiento o atraso en las cuotas, el equipo podrá ser bloqueado automáticamente. "
                 "Para evitar inconvenientes, debes cumplir con los pagos en las fechas acordadas.",
        "espera_respuesta": False,
        "continuar": True
    }


def generar_confirmacion() -> dict:
    """Paso 5: Confirmación final"""
    return {
        "paso": 5,
        "accion": "CONFIRMACION",
        "texto": "¿Estás de acuerdo con las condiciones?\n¿Te comprometes a cumplir con los pagos?",
        "espera_respuesta": True,
        "opciones": ["ACEPTA", "NO_ACEPTA", "DUDA"]
    }


def clasificar_respuesta_cliente(respuesta: str, datos: dict) -> dict:
    """
    Clasifica la respuesta del cliente y genera resultado
    """
    respuesta = respuesta.upper().strip()

    # Validación fallida
    if respuesta == "NO_COINCIDE":
        return {
            "valido": False,
            "razon": "Identidad no validada - datos no coinciden",
            "resultado": "VALIDACION_FALLIDA",
            "mensaje_whatsapp": generar_mensaje_validacion_fallida(datos)
        }

    # Aceptación
    if respuesta == "ACEPTA":
        return {
            "valido": True,
            "razon": "Cliente acepta condiciones y se compromete",
            "resultado": "APROBADO",
            "mensaje_whatsapp": None  # Se genera al final
        }

    # No aceptación
    if respuesta == "NO_ACEPTA":
        return {
            "valido": False,
            "razon": "Cliente no acepta las condiciones",
            "resultado": "RECHAZADO",
            "mensaje_whatsapp": generar_mensaje_rechazado(datos, "No acepta condiciones")
        }

    # Duda
    if respuesta == "DUDA":
        return {
            "valido": None,
            "razon": "Cliente muestra dudas",
            "resultado": "DUDOSO",
            "mensaje_whatsapp": None
        }

    return {
        "valido": None,
        "razon": "Respuesta no reconocida",
        "resultado": "SIN_RESPUESTA",
        "mensaje_whatsapp": None
    }


def generar_mensaje_validacion_fallida(datos: dict) -> str:
    """Genera mensaje cuando la validación de identidad falla"""
    return f"""⚠️ VALIDACIÓN DE IDENTIDAD FALLIDA

👤 Cliente: {datos['nombre_cliente']}
📋 Cédula: {datos['cedula']}
📞 Número: {datos['telefono_cliente']}

❌ La identidad del cliente no pudo ser validada.
Los datos proporcionados no coinciden con la información proporcionada.

📝 Acción requerida: Verificar datos del cliente e intentar nuevamente.
"""


def generar_mensaje_rechazado(datos: dict, razon: str) -> str:
    """Genera mensaje de rechazo"""
    return f"""❌ CRÉDITO RECHAZADO

👤 Cliente: {datos['nombre_cliente']}
📋 Cédula: {datos['cedula']}

📌 Razón: {razon}

📝 Observación: El cliente no cumple con los requisitos de validación.
"""


def obtener_todos_los_pasos(datos: dict) -> list:
    """Retorna todos los pasos del flujo para el cliente"""
    return [
        generar_saludo(datos["nombre_cliente"]),
        generar_validacion_identidad(datos["cedula"], datos["telefono_cliente"]),
        generar_informacion_credito(),
        generar_condiciones(),
        generar_confirmacion()
    ]
