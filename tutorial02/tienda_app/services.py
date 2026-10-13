from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Libro


class CompraService:
    """
    SERVICE LAYER (Tutorial 02).
    Orquesta el proceso de compra combinando el patrón Builder (construcción
    del dominio) y el patrón Factory Method (inyección del procesador de pago).
    """

    def __init__(self, procesador_pago):
        self.procesador = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_proceso_compra(self, usuario, lista_productos, direccion):
        # Uso del Builder: Semántica clara y validación interna
        orden = (
            self.builder
            .con_usuario(usuario)
            .con_productos(lista_productos)
            .para_envio(direccion)
            .build()
        )

        # Uso del Factory (inyectado): Cambio de comportamiento sin cambio de código
        if self.procesador.pagar(orden.total):
            return f"Orden {orden.id} procesada exitosamente."

        orden.delete()
        raise Exception("Error en la pasarela de pagos.")
