# Tutorial 03 — Introducción a APIs con DRF

**Estudiante:** Daniel Muñeton · **Materia:** Arquitectura de Software (AdS 2026)

API REST con **Django Rest Framework** que reutiliza la Capa de Servicio
(`CompraService`). Dos puertas (HTML y API), una sola lógica de negocio.

## 📦 Qué se implementó

| Paso | Qué | Archivo |
| :--- | :--- | :--- |
| 1 | DRF instalado y en `INSTALLED_APPS` | `Tienda/settings.py` |
| 2 | Serializers (Adapter + DTO) | `tienda_app/api/serializers.py` |
| 3 | `CompraAPIView` reutiliza el Service | `tienda_app/api/views.py` |
| 4 | Rutas `/api/v1/comprar/` y `/api/v1/inventario/` | `tienda_app/urls.py` |

## ✅ Entregables (sección 6)

1. **Log de pagos** + inventario descontado por API → `pagos_locales_DANIEL_MUNETON.log` y `evidencia_api.txt`.
2. **Captura** de un POST a `/api/v1/comprar/` (Postman o la Browsable API de DRF).

---

## ▶️ Cómo ejecutar

```bash
cd tutorial03
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install "django>=5.2,<5.3" djangorestframework markdown django-filter
python manage.py migrate
python manage.py seed_datos         # crea superusuario 'daniel' (test1234) + libros
python manage.py runserver
```

---

## 📸 Cómo hacer el POST y la captura (dos opciones)

### 🅰️ Opción fácil: Browsable API de DRF (en el navegador, sin instalar nada)

DRF trae una interfaz web automática. Con el servidor corriendo:

1. **Inicia sesión** primero en `http://127.0.0.1:8000/admin/` con `daniel` / `test1234`
   (así la API usa tu usuario autenticado para la compra).
2. Abre en el navegador: **`http://127.0.0.1:8000/api/v1/comprar/`**
3. Verás un formulario al final de la página ("HTML form" / "Raw data").
   En la pestaña **Raw data** escribe el JSON:
   ```json
   {
       "libro_id": 1,
       "direccion_envio": "Calle 123, Medellin",
       "cantidad": 1
   }
   ```
4. Pulsa **POST**. Deberías ver la respuesta `201 Created`:
   ```json
   { "estado": "exito", "mensaje": "Orden creada. Total: 178.5" }
   ```
5. **Toma la captura** de esa pantalla (que se vea la URL `/api/v1/comprar/`,
   el JSON enviado y la respuesta `201`).
6. Verifica el descuento abriendo `http://127.0.0.1:8000/api/v1/inventario/`:
   el `stock_actual` del libro 1 habrá bajado en 1.

### 🅱️ Opción Postman

1. Descarga Postman (https://www.postman.com/downloads/).
2. Nueva request → método **POST** → URL `http://127.0.0.1:8000/api/v1/comprar/`.
3. Pestaña **Body** → **raw** → tipo **JSON** → pega el mismo JSON de arriba.
4. (Autenticación) Como la vista usa el usuario de sesión, lo más simple es
   loguearte antes en `/admin/` en el navegador y usar la Browsable API; si usas
   Postman sin sesión, la compra se registra con usuario anónimo (igual descuenta
   stock y genera log, porque `usuario` puede ser `None`).
5. **Send** → verás el `201 Created`. Toma la captura con la respuesta visible.

### Cómo capturar la pantalla
- 🪟 **Windows:** `Win + Shift + S` (recorte) o `Impr Pant`.
- 🍎 **macOS:** `Cmd + Shift + 4` (seleccionar área).
- 🐧 **Linux:** `PrtScn`, o `Shift + PrtScn` para un área.

Guarda la imagen como `evidencia_post_api.png` y súbela junto con el log a la
asignación **"tutorial0-3 DRF&API"**.

---

## 🔎 Verificar que ambas puertas descuentan el mismo inventario

```bash
# Compra por API (descuenta stock + escribe log):
curl -X POST http://127.0.0.1:8000/api/v1/comprar/ \
     -H "Content-Type: application/json" \
     -d '{"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1}'

# Ver inventario (el stock del libro 1 baja):
curl http://127.0.0.1:8000/api/v1/inventario/
```

> **Nota de base de datos:** se usa SQLite para ejecución local (la config de
> PostgreSQL original del profesor queda comentada en `Tienda/settings.py`).
