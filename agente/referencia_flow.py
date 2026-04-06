"""
Flujo de llamada para REFERENCIAS
Valida si conocen al cliente, tipo de relación, actividad laboral
"""

from datetime import datetime


# Mapeo de tipos de relación
PARENTESCOS = {
    "mama": "Madre",
    "mamá": "Madre",
    "madre": "Madre",
    "mama": "Madre",
    "papa": "Padre",
    "papá": "Padre",
    "padre": "Padre",
    "hermano": "Hermano(a)",
    "hermana": "Hermano(a)",
    "hermanos": "Hermano(a)",
    "primo": "Primo(a)",
    "prima": "Primo(a)",
    "abuelo": "Abuelo(a)",
    "abuela": "Abuelo(a)",
    "abuelos": "Abuelo(a)",
    "amigo": "Amigo(a)",
    "amiga": "Amigo(a)",
    "amigos": "Amigo(a)",
    "companero": "Compañero laboral",
    "compañero": "Compañero laboral",
    "colega": "Compañero laboral",
    "vecino": "Vecino",
    "vecina": "Vecino",
    "esposa": "Otro",
    "esposo": "Otro",
    "novio": "Otro",
    "novia": "Otro",
    "hijo": "Otro",
    "hija": "Otro",
    "tio": "Tío(a)",
    "tía": "Tío(a)",
    "suegro": "Tío(a)",
    "suegra": "Tío(a)"
}


def generar_saludo_ref(nombre_ref: str) -> dict:
    """Paso 1: Saludo inicial"""
    hora = datetime.now().hour
    momento_dia = "buen día" if hora < 18 else "buen tarde"

    return {
        "paso": 1,
        "accion": "SALUDO_REFERENCIA",
        "texto": f"Hola, {momento_dia}, ¿con quién tengo el gusto?",
        "espera_respuesta": True
    }


def generar_confirmacion_identidad_ref(nombre_ref: str, nombre_cliente: str) -> dict:
    """Paso 2: Confirmar si es la persona correcta"""
    return {
        "paso": 2,
        "accion": "CONFIRMAR_IDENTIDAD",
        "texto": f"¿Eres {nombre_ref}?",
        "espera_respuesta": True,
        "opciones": ["SI", "NO"]
    }


def generar_no_conoce_cliente(nombre_cliente: str) -> dict:
    """Si no conoce al cliente"""
    return {
        "paso": 3,
        "accion": "NO_CONOCE",
        "texto": f"¿Conoces a {nombre_cliente}?",
        "espera_respuesta": True,
        "opciones": ["SI", "NO"]
    }


def generar_validacion_no_valida(nombre_ref: str, telefono_ref: str, razon: str) -> dict:
    """Genera resultado de referencia NO VÁLIDA"""
    return {
        "valido": False,
        "razon": razon,
        "resultado": "NO_VÁLIDA",
        "mensaje_whatsapp": generar_mensaje_referencia_no_valida(nombre_ref, telefono_ref, razon)
    }


def generar_aviso_grabacion() -> dict:
    """Paso 3: Aviso de grabación"""
    return {
        "paso": 3,
        "accion": "AVISO_GRABACION",
        "texto": "Te llamo del área de validación de crédito. Esta llamada está siendo grabada por seguridad.",
        "espera_respuesta": False,
        "continuar": True
    }


def generar_validacion_conocimiento(nombre_cliente: str) -> dict:
    """Paso 4: Validación - ¿Conoce al cliente?"""
    return {
        "paso": 4,
        "accion": "VALIDAR_CONOCIMIENTO",
        "texto": f"¿Conoces a {nombre_cliente}?",
        "espera_respuesta": True,
        "opciones": ["SI", "NO", "NSNC"]  # No sabe / No contesta
    }


def generar_pregunta_relacion() -> dict:
    """Paso 5: ¿Qué tipo de relación tiene?"""
    return {
        "paso": 5,
        "accion": "PREGUNTAR_RELACION",
        "texto": "¿Qué tipo de relación tienes con esa persona?",
        "espera_respuesta": True
    }


def generar_pregunta_trabajo() -> dict:
    """Paso 6: ¿Sabe si trabaja?"""
    return {
        "paso": 6,
        "accion": "PREGUNTAR_TRABAJO",
        "texto": "¿Sabes si actualmente está trabajando o generando ingresos?",
        "espera_respuesta": True,
        "opciones": ["SI", "NO", "NSNC"]
    }


def generar_pregunta_autorizacion() -> dict:
    """Paso 7: ¿Autoriza contactarlo?"""
    return {
        "paso": 7,
        "accion": "PREGUNTAR_AUTORIZACION",
        "texto": "En caso de no lograr contacto con él/ella o atraso en pagos, ¿autorizas que te contactemos para dejarle razón?",
        "espera_respuesta": True,
        "opciones": ["SI", "NO"]
    }


def generar_cierre() -> dict:
    """Paso 8: Cierre"""
    return {
        "paso": 8,
        "accion": "CIERRE",
        "texto": "Muchas gracias por tu tiempo.",
        "espera_respuesta": False,
        "continuar": False
    }


def clasificar_parentesco(relacion: str) -> str:
    """Clasifica el tipo de relación"""
    relacion_lower = relacion.lower().strip()

    # Buscar en el mapeo
    for key, value in PARENTESCOS.items():
        if key in relacion_lower:
            return value

    # Si no encuentra coincidencia
    return "Relación no definida"


def clasificar_respuesta_referencia(
    conoce: str,
    relacion: str,
    trabaja: str,
    autoriza: str
) -> dict:
    """
    Clasifica la referencia como VÁLIDA, DUDOSA o NO VÁLIDA
    """
    # NO VÁLIDA
    if conoce.upper() in ["NO", "NSNC"]:
        return {
            "conoce_al_cliente": False,
            "tipo_relacion": clasificar_parentesco(relacion),
            "actividad_laboral": "SIN INFORMACIÓN",
            "autoriza_contacto": False,
            "resultado": "NO_VÁLIDA",
            "razon": "No conoce al cliente o no proporcionó información"
        }

    # Análisis de dudas
    dudas = 0

    if not relacion or len(relacion) < 2:
        dudas += 1

    if trabaja.upper() == "NSNC":
        dudas += 1

    if autoriza.upper() in ["NO", "NSNC"]:
        dudas += 1

    # DUDOSA - tiene dudas
    if dudas >= 2:
        return {
            "conoce_al_cliente": True,
            "tipo_relacion": clasificar_parentesco(relacion),
            "actividad_laboral": trabaja.upper(),
            "autoriza_contacto": autoriza.upper() == "SI",
            "resultado": "DUDOSA",
            "razon": f"Respuestas inconsistentes ({dudas} dudas detectadas)"
        }

    # VÁLIDA - todo bien
    return {
        "conoce_al_cliente": True,
        "tipo_relacion": clasificar_parentesco(relacion),
        "actividad_laboral": "SÍ" if trabaja.upper() == "SI" else "NO",
        "autoriza_contacto": autoriza.upper() == "SI",
        "resultado": "VÁLIDA",
        "razon": "Información consistente y positiva"
    }


def generar_mensaje_referencia_no_valida(nombre_ref: str, telefono_ref: str, razon: str) -> str:
    """Genera mensaje de referencia NO VÁLIDA"""
    return f"""⚠️ VALIDACIÓN DE REFERENCIA FALLIDA

La referencia {nombre_ref} con número {telefono_ref} no fue posible contactar.

📌 Razón: {razon}

📝 Acción requerida: Por favor enviar una nueva referencia válida para continuar con el proceso de crédito.
"""


def generar_mensaje_resultado_referencia(
    datos_cliente: dict,
    datos_ref: dict,
    resultado: dict
) -> str:
    """Genera el resultado completo de validación de referencia"""
    estado_emoji = {
        "VÁLIDA": "✅",
        "DUDOSA": "⚠️",
        "NO_VÁLIDA": "❌"
    }.get(resultado["resultado"], "❓")

    return f"""📋 RESULTADO VALIDACIÓN DE REFERENCIA

👤 Cliente: {datos_cliente['nombre_cliente']}
🔹 Referencia: {datos_ref['nombre_ref']} 📞 Número: {datos_ref['telefono_ref']}

✅ Conoce al cliente: {"SÍ" if resultado['conoce_al_cliente'] else "NO"}
👥 Parentesco: {resultado['tipo_relacion']}
💼 Actividad laboral: {resultado['actividad_laboral']}
📢 Autoriza contacto: {"SÍ" if resultado['autoriza_contacto'] else "NO"}

📊 Estado: {estado_emoji} {resultado['resultado']}
📝 Observación: {resultado['razon']}
"""


def obtener_todos_los_pasos(nombre_ref: str, nombre_cliente: str) -> list:
    """Retorna todos los pasos del flujo para referencia"""
    return [
        generar_saludo_ref(nombre_ref),
        generar_confirmacion_identidad_ref(nombre_ref, nombre_cliente),
        generar_aviso_grabacion(),
        generar_validacion_conocimiento(nombre_cliente),
        generar_pregunta_relacion(),
        generar_pregunta_trabajo(),
        generar_pregunta_autorizacion(),
        generar_cierre()
    ]
