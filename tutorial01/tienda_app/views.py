import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .infra.factories import PaymentFactory
from .models import Inventario, Libro, Orden
from .services import CompraService

# =============================================================================
# PASO 1 - PUNTO DE PARTIDA: FBV "SPAGHETTI"
# -----------------------------------------------------------------------------
# Esta función concentra MÚLTIPLES responsabilidades (gestión de inventario,
# cálculo de impuestos y proceso de pago). Se deja documentada como evidencia
# del "antes" y de la deuda técnica que resolveremos con SOLID + Service Layer.
# NO es la vista en uso (ver CompraView más abajo).
# =============================================================================


def compra_rapida_fbv(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        # VIOLACIÓN SRP: Lógica de inventario dentro de la vista
        inventario = Inventario.objects.get(libro=libro)
        if inventario.cantidad > 0:
            # VIOLACIÓN OCP: Cálculo de negocio hardcodeado (IVA fijo)
            total = float(libro.precio) * 1.19

            # VIOLACIÓN DIP: Proceso de pago acoplado al sistema de archivos
            with open("pagos_manuales.log", "a") as f:
                f.write(f"[{datetime.datetime.now()}] Pago FBV: ${total}\n")

            inventario.cantidad -= 1
            inventario.save()
            Orden.objects.create(libro=libro, total=total)

            return HttpResponse(f"Compra exitosa: {libro.titulo}")
        else:
            return HttpResponse("Sin stock", status=400)

    total_estimado = float(libro.precio) * 1.19
    return render(request, 'tienda_app/compra_rapida.html', {
        'libro': libro,
        'total': total_estimado,
    })


# =============================================================================
# PASO 2 - MIGRACIÓN A CLASS-BASED VIEW (CBV)
# -----------------------------------------------------------------------------
# Separamos los verbos HTTP (GET/POST) usando una clase. Eliminamos el
# condicional 'if request.method'. La lógica de negocio AÚN reside aquí, pero
# ya está más ordenada y lista para delegar al servicio (Paso 3).
# Se deja documentada como etapa intermedia de la evolución.
# =============================================================================


class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = float(libro.precio) * 1.19
        return render(request, self.template_name, {
            'libro': libro,
            'total': total,
        })

    def post(self, request, libro_id):
        # La lógica de negocio aún reside aquí, pero separada del GET.
        libro = get_object_or_404(Libro, id=libro_id)
        inv = Inventario.objects.get(libro=libro)
        if inv.cantidad > 0:
            total = float(libro.precio) * 1.19
            # ... proceso de compra ...
            return HttpResponse("Comprado via CBV")
        return HttpResponse("Error", status=400)


# =============================================================================
# PASO 3 - CBV FINAL CON SERVICE LAYER  (VISTA EN PRODUCCIÓN)
# -----------------------------------------------------------------------------
# Resultado final del tutorial: la vista es un simple "portero" (< 10 líneas de
# lógica por método). Toda la complejidad vive en CompraService. Esto hace el
# código testeable, mantenible y escalable (cumple SRP, OCP, DIP).
# =============================================================================


class CompraView(View):
    """CBV que delega toda la lógica de negocio al servicio."""

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(request, self.template_name, {
                'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                'total': total,
            })
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)
