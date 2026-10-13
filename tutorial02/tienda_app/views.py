from django.shortcuts import get_object_or_404, render
from django.views import View

from .infra.factories import PaymentFactory
from .models import Libro
from .services import CompraService


class CompraView(View):
    """
    CBV agnóstica a la infraestructura.
    No sabe qué banco se usa: la Fábrica (PaymentFactory) le entrega el
    procesador adecuado según la variable de entorno PAYMENT_PROVIDER.
    """

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        # ANTES: gateway = BancoNacionalProcesador()
        # AHORA: Delegación total a la Fábrica (Factory Method)
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        libro = get_object_or_404(Libro, id=libro_id)
        usuario = request.user if request.user.is_authenticated else None
        try:
            # El Builder recibe una lista de productos (aquí, el libro seleccionado)
            mensaje = servicio.ejecutar_proceso_compra(
                usuario=usuario,
                lista_productos=[libro],
                direccion=request.POST.get('direccion', 'Dirección de prueba'),
            )
            return render(request, self.template_name, {
                'mensaje_exito': mensaje,
            })
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)
