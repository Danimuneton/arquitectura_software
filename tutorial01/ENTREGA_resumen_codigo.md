# Tutorial 01 — Resumen de Código (Entrega)

**Estudiante:** Daniel Muñeton
**Materia:** Arquitectura de Software (AdS 2026)
**Tutorial:** `tutorial01-DjangoSOLID` — Evolución de Arquitectura en Django

Este documento contiene el código final de `services.py` y `views.py` para
validar que la lógica de negocio fue **extraída correctamente de la capa de
presentación** hacia la capa de servicio.

---

## 1. `tienda_app/services.py` — Capa de Servicio (Service Layer)

La lógica de orquestación (validar stock, construir la orden, procesar el pago
y descontar inventario) vive aquí, **no en la vista**. El servicio depende de
una *abstracción* (`procesador_pago`), cumpliendo el principio DIP.

```python
from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro


class CompraService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio,
    la infraestructura y la base de datos.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        orden = (
            self.builder
            .con_usuario(usuario)
            .con_libro(libro)
            .con_cantidad(cantidad)
            .para_envio(direccion)
            .build()
        )

        pago_exitoso = self.procesador_pago.pagar(orden.total)
        if not pago_exitoso:
            orden.delete()
            raise Exception("La transacción fue rechazada por el banco.")

        inv.cantidad -= cantidad
        inv.save()

        return orden.total
```

---

## 2. `tienda_app/views.py` — Capa de Presentación (CBV)

La vista final `CompraView` actúa como un simple **"portero"**: recibe la
petición, delega al servicio y retorna la respuesta. Cada método tiene menos de
10 líneas de lógica — toda la complejidad vive en `CompraService`.

> El archivo conserva, documentadas, las etapas previas de la evolución
> (`compra_rapida_fbv` = Paso 1 Spaghetti, y `CompraRapidaView` = Paso 2 CBV
> intermedia) como evidencia del "antes y después".

```python
import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .infra.factories import PaymentFactory
from .models import Inventario, Libro, Orden
from .services import CompraService


# -----------------------------------------------------------------------------
# PASO 1 - FBV "SPAGHETTI" (el "antes": viola SRP, OCP y DIP)
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# PASO 2 - CLASS-BASED VIEW intermedia (separa verbos HTTP GET/POST)
# -----------------------------------------------------------------------------
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
        libro = get_object_or_404(Libro, id=libro_id)
        inv = Inventario.objects.get(libro=libro)
        if inv.cantidad > 0:
            total = float(libro.precio) * 1.19
            return HttpResponse("Comprado via CBV")
        return HttpResponse("Error", status=400)


# -----------------------------------------------------------------------------
# PASO 3 - CBV FINAL CON SERVICE LAYER (el "después": vista = portero delgado)
# -----------------------------------------------------------------------------
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
```

---

