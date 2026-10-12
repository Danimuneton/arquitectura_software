# Tutorial 02 — Patrones Creacionales en Django (Entrega)

**Estudiante:** Daniel Muñeton
**Materia:** Arquitectura de Software (AdS 2026)
**Tema:** Factory Method y Builder para sistemas escalables

---

## 1. Evidencia de Ejecución (Factory Method con MOCK)

Al ejecutar una compra con la variable de entorno `PAYMENT_PROVIDER=MOCK`, la
Fábrica entrega un `MockPaymentProcessor` en lugar del banco real, y en consola
aparece el mensaje `[DEBUG] Mock Payment...`:

```
========================================================
 EVIDENCIA Tutorial 02 - Factory Method (MOCK)
 Estudiante: Daniel Muneton
 Comando: PAYMENT_PROVIDER=MOCK python manage.py shell
========================================================

>> Procesador seleccionado por la Fabrica: MockPaymentProcessor
>> Productos en la orden: ['Clean Code en Python', 'Arquitectura Limpia']
[DEBUG] Mock Payment: Procesando pago de $476.0 sin cargo real.
>> Orden 1 procesada exitosamente.
```

> La salida cruda también está guardada en `evidencia_consola.txt`.
> **Para la captura de pantalla** sigue las instrucciones del `README_TUTORIAL02.md`.

---

## 2. Código Fuente

### 2.1 `tienda_app/infra/factories.py` — Factory Method

```python
import os
from .gateways import BancoNacionalProcesador


# Implementación ligera para pruebas (Mocking)
class MockPaymentProcessor:
    def pagar(self, monto: float) -> bool:
        print(f"[DEBUG] Mock Payment: Procesando pago de ${monto} sin cargo real.")
        return True


class PaymentFactory:
    @staticmethod
    def get_processor():
        # LECCIÓN ARQUITECTURA: La configuración viene del ambiente, no del código
        provider = os.getenv('PAYMENT_PROVIDER', 'BANCO')

        if provider == 'MOCK':
            return MockPaymentProcessor()

        # Por defecto usamos la infraestructura real
        return BancoNacionalProcesador()
```

### 2.2 `tienda_app/domain/builders.py` — Builder

```python
from ..models import Orden


class OrdenBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._items = []
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self  # Permite Fluent Interface

    def con_productos(self, productos):
        self._items = productos
        return self

    def para_envio(self, direccion):
        self._direccion = direccion
        return self

    def build(self) -> Orden:
        if not self._usuario or not self._items:
            raise ValueError("Datos insuficientes para crear la orden.")

        # Encapsulamos la lógica de cálculo
        subtotal = sum(float(p.precio) for p in self._items)
        total_con_iva = round(subtotal * 1.19, 2)

        orden = Orden.objects.create(
            usuario=self._usuario,
            total=total_con_iva,
            direccion_envio=self._direccion,
        )
        orden.productos.set(self._items)
        self.reset()
        return orden
```

---

## 3. Reflexión: ¿Por qué el `OrdenBuilder` reduce el riesgo de errores?

El patrón **Builder** reduce el riesgo de errores porque **centraliza y
encapsula** en un solo lugar toda la lógica de construcción y validación de la
orden (el cálculo del subtotal, la aplicación del IVA y la verificación de que
existan usuario y productos). Si en cambio creáramos la `Orden` directamente en
la vista, esa lógica quedaría dispersa y habría que repetirla —y recordarla—
en cada punto del código que necesite crear una orden (la vista web, la API, un
comando de administración, un test), con el riesgo constante de olvidar un paso
—por ejemplo, aplicar el IVA o validar el stock— o de calcular el total de forma
inconsistente entre un lugar y otro. El Builder garantiza que **toda orden nace
válida y completa**, sin importar quién la pida: su método `build()` es la única
puerta de entrada y rechaza con un error claro cualquier construcción con datos
insuficientes. Además, su *fluent interface* (`.con_usuario(...).con_productos(...).build()`)
hace el código legible y autoexplicativo, y mantiene la vista delgada y enfocada
únicamente en recibir la petición y delegar, respetando el principio de
responsabilidad única (SRP).

---

## 4. Entregables (sección 6 del tutorial)

| # | Entregable | Archivo |
| :--- | :--- | :--- |
| 1 | Captura de consola `[DEBUG] Mock Payment...` | `evidencia_consola.txt` + tu screenshot |
| 2 | Código `factories.py` y `builders.py` | incluidos arriba y en el repo |
| 3 | Reflexión sobre el Builder | sección 3 de este documento |
