# Tutorial 01 — Evolución de Arquitectura en Django

**Estudiante:** Daniel Muñeton · **Materia:** Arquitectura de Software (AdS 2026)

De *Spaghetti Code* a *Grado Empresarial* usando **CBVs**, **SOLID** y
**Service Layer**.

## 📦 Qué contiene esta carpeta

Proyecto Django completo basado en el repo del profesor
(`Nram94/TEIS-DjangoSOLID`), con los pasos del tutorial aplicados:

| Paso | Qué se hizo | Dónde |
| :--- | :--- | :--- |
| 1 | FBV "Spaghetti" (viola SRP/OCP/DIP) | `tienda_app/views.py` → `compra_rapida_fbv` |
| 2 | Migración a Class-Based View | `tienda_app/views.py` → `CompraRapidaView` |
| 3 | Capa de Servicio (orquestación) | `tienda_app/services.py` → `CompraService` |
| 4 | Log de auditoría personalizado | `tienda_app/infra/gateways.py` |

## ✅ Entregables (sección 7 del tutorial)

1. **`pagos_locales_DANIEL_MUNETON.log`** — evidencia de ejecución con 3 transacciones.
2. **`ENTREGA_resumen_codigo.md`** — documento con el código de `services.py` y `views.py`.

## ▶️ Cómo ejecutar localmente

```bash
cd tutorial01
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install "django>=5.2,<5.3" djangorestframework
python manage.py migrate

# Crear datos de prueba (3 libros con stock)
python manage.py shell
>>> from tienda_app.models import Libro, Inventario
>>> for t, p in [("Clean Code en Python", 150.0), ("Arquitectura Limpia", 250.0), ("Patrones de Diseño (GoF)", 180.0)]:
...     l = Libro.objects.create(titulo=t, precio=p); Inventario.objects.create(libro=l, cantidad=10)

python manage.py runserver
# Visita /compra/1/ , /compra/2/ , /compra/3/ y confirma el pago en cada uno.
```

Tras realizar 3 compras, se genera `pagos_locales_DANIEL_MUNETON.log` en la raíz
del proyecto con 3 registros de transacciones.

> **Nota de base de datos:** El `settings.py` original del profesor usa
> PostgreSQL (vía Docker). Para ejecución local sencilla se cambió a SQLite
> (como asume el Paso 0 del tutorial). La configuración de PostgreSQL se dejó
> comentada en `Tienda/settings.py`.
