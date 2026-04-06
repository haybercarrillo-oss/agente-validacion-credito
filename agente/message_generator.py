"""
Generador de mensajes automáticos para WhatsApp
Genera resultados finales listos para enviar
"""

from datetime import datetime


def generar_fecha_actual() -> str:
    """Genera la fecha actual formateada"""
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M")


def generar_resultado_final_cliente(
    datos_cliente: dict,
    identidad_validada: bool,
    acepta_condiciones: bool,
    resultado_ref1: dict,
    resultado_ref2: dict,
    observacion: str = ""
) -> str:
    """
    Genera el resultado final de validación del crédito
    """
    # Determinar estado final
    if not identidad_validada:
        estado_final = "❌ RECHAZADO"
        estado_emoji = "❌"
    elif not acepta_condiciones:
        estado_final = "❌ RECHAZADO"
        estado_emoji = "❌"
    elif resultado_ref1["resultado"] == "NO_VÁLIDA" and resultado_ref2["resultado"] == "NO_VÁLIDA":
        estado_final = "⚠️ REQUIERE NUEVAS REFERENCIAS"
        estado_emoji = "⚠️"
    elif resultado_ref1["resultado"] in ["NO_VÁLIDA", "DUDOSA"] and \
         resultado_ref2["resultado"] in ["NO_VÁLIDA", "DUDOSA"]:
        estado_final = "⚠️ REQUIERE NUEVAS REFERENCIAS"
        estado_emoji = "⚠️"
    else:
        estado_final = "✅ APROBADO"
        estado_emoji = "✅"

    # Construir mensaje
    mensaje = f"""📊 RESULTADO FINAL DEL CRÉDITO

👤 Cliente: {datos_cliente['nombre_cliente']}
📋 Cédula: {datos_cliente['cedula']}
📞 Teléfono: {datos_cliente['telefono_cliente']}
📅 Fecha: {generar_fecha_actual()}

━━━━━━━━━━━━━━━━━━━━━━━
✔ Identidad validada: {"SÍ" if identidad_validada else "NO"}
✔ Acepta condiciones: {"SÍ" if acepta_condiciones else "NO"}
━━━━━━━━━━━━━━━━━━━━━━━

🔹 Referencia 1: {datos_cliente['nombre_ref1']}
   Estado: {resultado_ref1['resultado']}
   {"📝 " + resultado_ref1.get('razon', '') if resultado_ref1.get('razon') else ''}

🔹 Referencia 2: {datos_cliente['nombre_ref2']}
   Estado: {resultado_ref2['resultado']}
   {"📝 " + resultado_ref2.get('razon', '') if resultado_ref2.get('razon') else ''}

━━━━━━━━━━━━━━━━━━━━━━━
📌 Estado final: {estado_emoji} {estado_final}
━━━━━━━━━━━━━━━━━━━━━━━

📝 Observación: {observacion if observacion else 'Sin observaciones adicionales'}
"""

    return mensaje


def generar_mensaje_seguimiento(datos_cliente: dict, tipo: str = "rechazo") -> str:
    """Genera mensajes de seguimiento según el tipo"""
    if tipo == "rechazo":
        return f"""⚠️ INFORMACIÓN IMPORTANTE

Hola {datos_cliente['nombre_cliente']}, lamentamos informarte que tu solicitud de crédito no pudo ser aprobada en esta ocasión.

Te recomendamos:
• Verificar tus datos personales
• Asegurar que las referencias proporcionadas estén actualizadas
• Mantener un buen historial de pagos

Si tienes dudas, comunícate con nuestra área de crédito.
"""
    elif tipo == "aprobado":
        return f"""🎉 ¡FELICIDADES, {datos_cliente['nombre_cliente']}!

Tu solicitud de crédito ha sido aprobada.

Próximos pasos:
1. Recibirás un mensaje con los detalles del financiamiento
2. Un asesor se comunicará contigo para formalizar el proceso
3.Recuerda cumplir con tus pagos en las fechas acordadas

¡Gracias por confiar en nosotros!
"""
    elif tipo == "referencias":
        return f"""📋 SOLICITUD DE NUEVAS REFERENCIAS

{datos_cliente['nombre_cliente']}, debido a que no fue posible validar las referencias proporcionadas, necesitamos que nos envíes nuevas:

Requisitos de las referencias:
• Deben ser personas que te conozcan directamente
• Preferiblemente: familiares o compañeros de trabajo
• Deben tener número de teléfono válido

Por favor responde con los datos de 2 nuevas referencias.
"""
    return ""


def generar_resumen_ejecutivo(resultados: list) -> str:
    """
    Genera un resumen ejecutivo de todos los resultados
    Args:
        resultados: lista de diccionarios con datos de cada cliente validado
    """
    total = len(resultados)
    aprobados = sum(1 for r in resultados if r.get("estado") == "APROBADO")
    rechazados = sum(1 for r in resultados if r.get("estado") == "RECHAZADO")
    pendientes = sum(1 for r in resultados if r.get("estado") == "PENDIENTE")

    mensaje = f"""📈 RESUMEN EJECUTIVO - VALIDACIONES

📊 Total validaciones: {total}
✅ Aprobados: {aprobados}
❌ Rechazados: {rechazados}
⏳ Pendientes: {pendientes}

━━━━━━━━━━━━━━━━━━━━━━━

"""

    for r in resultados:
        estado_emoji = {
            "APROBADO": "✅",
            "RECHAZADO": "❌",
            "PENDIENTE": "⏳"
        }.get(r.get("estado", ""), "❓")

        mensaje += f"{estado_emoji} {r.get('nombre_cliente', 'N/A')} - {r.get('estado', 'N/A')}\n"

    mensaje += f"""
━━━━━━━━━━━━━━━━━━━━━━━
📅 Generado: {generar_fecha_actual()}
"""

    return mensaje
