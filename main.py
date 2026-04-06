"""
MAIN.PY - Orquestador del Agente de Validación de Crédito
Recibe datos, ejecuta flujos y genera resultados
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio del proyecto al path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from agente.cliente_flow import (
    obtener_todos_los_pasos as cliente_pasos,
    clasificar_respuesta_cliente,
    generar_mensaje_validacion_fallida
)
from agente.referencia_flow import (
    clasificar_respuesta_referencia,
    generar_mensaje_resultado_referencia,
    generar_mensaje_referencia_no_valida
)
from agente.message_generator import (
    generar_resultado_final_cliente,
    generar_mensaje_seguimiento
)


class AgenteValidacion:
    """Orquestador principal del agente de validación"""

    def __init__(self):
        self.resultados = []
        self.cliente_actual = None

    def cargar_datos_csv(self, ruta_csv: str) -> list:
        """Carga datos desde archivo CSV"""
        datos = []
        try:
            with open(ruta_csv, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                if len(lineas) < 2:
                    return []

                # Leer encabezados
                headers = [h.strip() for h in lineas[0].split(',')]

                # Leer datos
                for linea in lineas[1:]:
                    valores = [v.strip() for v in linea.split(',')]
                    if len(valores) >= len(headers):
                        cliente = dict(zip(headers, valores))
                        datos.append(cliente)

        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {ruta_csv}")
        except Exception as e:
            print(f"❌ Error al leer CSV: {e}")

        return datos

    def simular_llamada_cliente(self, datos_cliente: dict) -> dict:
        """
        Simula una llamada al cliente titular
        En producción, esto se conectaría con Twilio
        """
        print(f"\n📞 SIMULANDO LLAMADA AL CLIENTE: {datos_cliente['nombre_cliente']}")
        print("=" * 50)

        # Mostrar todos los pasos del flujo
        pasos = cliente_pasos(datos_cliente)

        for paso in pasos:
            print(f"\n📌 Paso {paso['paso']}: {paso['accion']}")
            print(f"   {paso['texto']}")
            if paso.get('espera_respuesta'):
                print(f"   Opciones: {paso.get('opciones', ['Respuesta libre'])}")

        # En simulación, retornamos datos de ejemplo
        # En producción, esto vendría de la llamada real
        return {
            "identidad_validada": True,
            "acepta_condiciones": True,
            "respuesta": "ACEPTA"
        }

    def simular_llamada_referencia(self, datos_cliente: dict, datos_ref: dict) -> dict:
        """
        Simula una llamada a una referencia
        En producción, esto se conectaría con Twilio
        """
        print(f"\n📞 SIMULANDO LLAMADA A REFERENCIA: {datos_ref['nombre_ref']}")
        print("=" * 50)

        # En simulación, retornamos resultado de ejemplo
        # En producción, esto vendría de la llamada real
        return {
            "conoce": "SI",
            "relacion": "amigo",
            "trabaja": "SI",
            "autoriza": "SI"
        }

    def validar_cliente(self, datos_cliente: dict, modo: str = "simulacion") -> dict:
        """
        Ejecuta la validación completa de un cliente
        1. Llama al cliente titular
        2. Llama a referencia 1
        3. Llama a referencia 2
        4. Genera resultado final
        """
        print(f"\n{'='*60}")
        print(f"🔄 INICIANDO VALIDACIÓN: {datos_cliente['nombre_cliente']}")
        print(f"{'='*60}")

        resultado = {
            "nombre_cliente": datos_cliente["nombre_cliente"],
            "cedula": datos_cliente["cedula"],
            "telefono_cliente": datos_cliente["telefono_cliente"],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "referencias": []
        }

        # 1. Llamada al cliente titular
        if modo == "simulacion":
            respuesta_cliente = self.simular_llamada_cliente(datos_cliente)
        else:
            # En producción, aquí se conectaría con Twilio
            respuesta_cliente = self.simular_llamada_cliente(datos_cliente)

        resultado["identidad_validada"] = respuesta_cliente.get("identidad_validada", False)
        resultado["acepta_condiciones"] = respuesta_cliente.get("acepta_condiciones", False)

        # Si falla la identidad, terminar
        if not resultado["identidad_validada"]:
            resultado["estado"] = "RECHAZADO"
            resultado["mensaje_whatsapp"] = generar_mensaje_validacion_fallida(datos_cliente)
            return resultado

        # Si no acepta condiciones
        if not resultado["acepta_condiciones"]:
            resultado["estado"] = "RECHAZADO"
            resultado["mensaje_whatsapp"] = generar_mensaje_seguimiento(datos_cliente, "rechazo")
            return resultado

        # 2. Llamada a Referencia 1
        datos_ref1 = {
            "nombre_ref": datos_cliente["nombre_ref1"],
            "telefono_ref": datos_cliente["telefono_ref1"]
        }

        if modo == "simulacion":
            resp_ref1 = self.simular_llamada_referencia(datos_cliente, datos_ref1)
        else:
            resp_ref1 = self.simular_llamada_referencia(datos_cliente, datos_ref1)

        resultado_ref1 = clasificar_respuesta_referencia(
            resp_ref1["conoce"],
            resp_ref1["relacion"],
            resp_ref1["trabaja"],
            resp_ref1["autoriza"]
        )
        resultado["referencias"].append({
            "nombre": datos_ref1["nombre_ref"],
            "telefono": datos_ref1["telefono_ref"],
            "resultado": resultado_ref1
        })

        # 3. Llamada a Referencia 2
        datos_ref2 = {
            "nombre_ref": datos_cliente["nombre_ref2"],
            "telefono_ref": datos_cliente["telefono_ref2"]
        }

        if modo == "simulacion":
            resp_ref2 = self.simular_llamada_referencia(datos_cliente, datos_ref2)
        else:
            resp_ref2 = self.simular_llamada_referencia(datos_cliente, datos_ref2)

        resultado_ref2 = clasificar_respuesta_referencia(
            resp_ref2["conoce"],
            resp_ref2["relacion"],
            resp_ref2["trabaja"],
            resp_ref2["autoriza"]
        )
        resultado["referencias"].append({
            "nombre": datos_ref2["nombre_ref"],
            "telefono": datos_ref2["telefono_ref"],
            "resultado": resultado_ref2
        })

        # 4. Generar resultado final
        resultado_final = generar_resultado_final_cliente(
            datos_cliente,
            resultado["identidad_validada"],
            resultado["acepta_condiciones"],
            resultado_ref1,
            resultado_ref2
        )

        resultado["estado"] = self._determinar_estado(resultado_ref1, resultado_ref2)
        resultado["mensaje_whatsapp"] = resultado_final

        print(f"\n📊 RESULTADO: {resultado['estado']}")

        return resultado

    def _determinar_estado(self, ref1: dict, ref2: dict) -> str:
        """Determina el estado final basado en las referencias"""
        if ref1["resultado"] == "VÁLIDA" and ref2["resultado"] == "VÁLIDA":
            return "APROBADO"
        elif ref1["resultado"] == "NO_VÁLIDA" and ref2["resultado"] == "NO_VÁLIDA":
            return "REQUIERE_NUEVAS_REFERENCIAS"
        elif ref1["resultado"] == "NO_VÁLIDA" or ref2["resultado"] == "NO_VÁLIDA":
            return "REQUIERE_NUEVAS_REFERENCIAS"
        else:
            return "REQUIERE_REVISION"

    def guardar_resultado(self, resultado: dict, carpeta_resultados: str):
        """Guarda el resultado en un archivo JSON y TXT"""
        carpeta = Path(carpeta_resultados)
        carpeta.mkdir(parents=True, exist_ok=True)

        # Nombre del archivo basado en el cliente
        nombre_archivo = resultado["nombre_cliente"].replace(" ", "_")

        # Guardar JSON
        ruta_json = carpeta / f"{nombre_archivo}.json"
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        # Guardar mensaje WhatsApp
        ruta_txt = carpeta / f"{nombre_archivo}_whatsapp.txt"
        with open(ruta_txt, 'w', encoding='utf-8') as f:
            f.write(resultado["mensaje_whatsapp"])

        print(f"💾 Resultado guardado en:")
        print(f"   - {ruta_json}")
        print(f"   - {ruta_txt}")

    def ejecutar_validaciones(self, ruta_csv: str, carpeta_resultados: str, modo: str = "simulacion"):
        """Ejecuta validaciones para todos los clientes del CSV"""
        clientes = self.cargar_datos_csv(ruta_csv)

        if not clientes:
            print("❌ No se encontraron clientes en el archivo")
            return

        print(f"\n📋 Se encontraron {len(clientes)} clientes para validar")

        for i, cliente in enumerate(clientes, 1):
            print(f"\n[{i}/{len(clientes)}] Procesando: {cliente['nombre_cliente']}")

            resultado = self.validar_cliente(cliente, modo)
            self.guardar_resultado(resultado, carpeta_resultados)
            self.resultados.append(resultado)

        print(f"\n{'='*60}")
        print(f"✅ VALIDACIONES COMPLETADAS: {len(self.resultados)} clientes procesados")
        print(f"{'='*60}")

        return self.resultados


def main():
    """Función principal"""
    # Rutas
    base_dir = Path(__file__).parent
    datos_csv = base_dir / "datos" / "clientes_ejemplo.csv"
    resultados_dir = base_dir / "resultados"

    # Crear agente
    agente = AgenteValidacion()

    # Ejecutar en modo simulación
    print("\n🚀 INICIANDO AGENTE DE VALIDACIÓN DE CRÉDITO")
    print("=" * 60)
    print("📌 Modo: SIMULACIÓN (sin llamadas reales)")
    print("=" * 60)

    resultados = agente.ejecutar_validaciones(
        str(datos_csv),
        str(resultados_dir),
        modo="simulacion"
    )

    # Mostrar resumen
    print("\n📊 RESUMEN DE RESULTADOS:")
    for r in resultados:
        print(f"   {r['nombre_cliente']}: {r['estado']}")


if __name__ == "__main__":
    main()
