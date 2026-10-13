# Tutorial 03 — Introducción a APIs con DRF (Entrega)

**Estudiante:** Daniel Muñeton
**Materia:** Arquitectura de Software (AdS 2026)
**Tema:** De Monolito HTML a Backend Headless — Django Rest Framework

---

## 1. Objetivo cumplido

Se implementó una capa de **API REST con DRF** que **reutiliza la misma Capa de
Servicio** (`CompraService`) usada por la vista HTML. Esto demuestra que ambas
"puertas" (HTML y API) conducen a la misma "habitación" (la lógica de negocio).

---

## 2. Evidencia de Ejecución (ambas puertas, misma lógica)

```
--- Stock inicial libro 1: 10 ---

[PUERTA 1 - API] POST /api/v1/comprar/  payload libro_id=1
  status: 201 | json: {"estado": "exito", "mensaje": "Orden creada. Total: 178.5"}
  stock libro 1 ahora: 9

[PUERTA 2 - HTML] POST /compra/1/
  status: 200
  stock libro 1 ahora: 8

--> Ambas puertas descontaron el MISMO inventario usando el MISMO CompraService.
```

### Log de pagos generado (`pagos_locales_DANIEL_MUNETON.log`)

```
[2026-10-13 ...] Transaccion exitosa por: $178.50   <- compra vía API
[2026-10-13 ...] Transaccion exitosa por: $178.50   <- compra vía HTML
```

> La salida completa está en `evidencia_api.txt`. El log confirma que la compra
> por API **descuenta inventario y genera el log de pagos**, usando la Factory
> configurada en el Tutorial 02.

---

## 3. Código Fuente

### 3.1 `tienda_app/api/serializers.py` — El Adaptador (patrón Adapter)

```python
from rest_framework import serializers
from tienda_app.models import Libro


class LibroSerializer(serializers.ModelSerializer):
    stock_actual = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = ['id', 'titulo', 'precio', 'stock_actual']

    def get_stock_actual(self, obj):
        inventario = getattr(obj, 'inventario', None)
        return inventario.cantidad if inventario else 0


class OrdenInputSerializer(serializers.Serializer):
    """DTO: valida la entrada de datos, no está ligado a un modelo."""
    libro_id = serializers.IntegerField()
    direccion_envio = serializers.CharField(max_length=200)
    cantidad = serializers.IntegerField(min_value=1, default=1)
```

### 3.2 `tienda_app/api/views.py` — La API View (el Controlador)

```python
class CompraAPIView(APIView):
    """POST /api/v1/comprar/ — procesa compras vía JSON reutilizando el Service."""

    def post(self, request):
        serializer = OrdenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data
        try:
            gateway = PaymentFactory.get_processor()           # Factory
            servicio = CompraService(procesador_pago=gateway)  # Service reutilizado
            usuario = request.user if request.user.is_authenticated else None
            resultado = servicio.ejecutar_compra(
                libro_id=datos['libro_id'],
                cantidad=datos.get('cantidad', 1),
                direccion=datos['direccion_envio'],
                usuario=usuario,
            )
            return Response(
                {'estado': 'exito', 'mensaje': f'Orden creada. Total: {resultado}'},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception:
            return Response({'error': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

> **La clave arquitectónica:** la API View NO reescribe la lógica de compra.
> Solo valida la entrada (Serializer), pide el procesador (Factory) y delega al
> `CompraService`. El servicio no cambia; solo cambia **quién lo llama**.

### 3.3 `tienda_app/urls.py` — Enrutamiento

```python
urlpatterns = [
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),   # HTML
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),             # API
    path('api/v1/inventario/', InventarioAPIView.as_view(), name='api_inventario'),   # API GET
]
```

---

## 4. Entregables (sección 6 del tutorial)

| # | Entregable | Archivo / Acción |
| :--- | :--- | :--- |
| 1 | Log de pagos + inventario descontado por API | `pagos_locales_DANIEL_MUNETON.log` + `evidencia_api.txt` |
| 2 | Captura del POST a `/api/v1/comprar/` (Postman o DRF web) | tu screenshot — ver `README_TUTORIAL03.md` |
