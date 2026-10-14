# Tutorial 06 — El Primer Estrangulamiento (Strangler Pattern)

**Estudiante:** Daniel Muñeton · **Materia:** Arquitectura de Software (AdS 2026)

Extraemos la función de compra del monolito **Django** hacia un microservicio
**Flask**. Nginx enruta según la versión de la API:

- `/api/v1/...` → **Django** (monolito v1)
- `/api/v2/comprar` → **Flask** (microservicio v2, "el estrangulador")

## 📦 Qué se añadió respecto al Tutorial 05

| Elemento | Archivo | Rol |
| :--- | :--- | :--- |
| Microservicio Flask | `microservicio_pagos/app.py` | Endpoint `POST /api/v2/comprar` |
| Dockerfile de Flask | `microservicio_pagos/Dockerfile` | Imagen del microservicio (gunicorn `app:app`) |
| Endpoint productos (v1) | `tienda_app/api/views.py` → `ProductosAPIView` | `GET /api/v1/productos/` servido por Django |
| Ruteo del estrangulador | `nginx/nginx.conf` | v1→Django, v2→Flask |
| Orquestación | `docker-compose.yml` | servicios `db`, `web_django`, `pagos_flask`, `nginx` |

> ⚠️ **Correcciones respecto al PDF:**
> 1. El comando de Gunicorn del monolito usa **`Tienda.wsgi`** (no `tienda_project.wsgi`).
> 2. El PDF pide una evidencia en `GET /api/v1/productos/`, que el proyecto no
>    tenía: se **creó** ese endpoint (`ProductosAPIView`) para que la prueba
>    funcione tal cual la pide el profesor.

> ✅ **Verificado localmente:** la imagen de Flask construye; el endpoint
> `POST /api/v2/comprar` responde 200 con "procesada exitosamente por el
> Microservicio Flask (v2)" y 400 si falta `producto_id`; el endpoint
> `/api/v1/productos/` resuelve en Django.

---

## ▶️ Prueba local con Docker (opcional)

```powershell
cd tutorial06
docker compose up --build
```

- v1 (Django): `http://localhost/api/v1/productos/`
- v2 (Flask):  POST a `http://localhost/api/v2/comprar`

Detener: `Ctrl + C`; limpiar: `docker compose down`.

---

## ☁️ Despliegue en AWS EC2

En la terminal SSH de tu instancia:

```bash
cd arquitectura_software
git pull origin main
cd tutorial06
docker compose up -d --build
docker ps     # deben verse 4 contenedores: db, web_django, pagos_flask, nginx
```

El puerto **80** ya debería estar abierto en el Security Group (del Tutorial 05).
Si no, ábrelo: Type **HTTP**, Port **80**, Source **0.0.0.0/0**.

---

## 📸 Entregables (sección 7): 3 evidencias

> El profe pide **Postman**. En Windows descárgalo de https://www.postman.com/downloads/
> (o usa la Browsable API de DRF / el navegador para el GET, y Postman para el POST).

### 1️⃣ Prueba de Coexistencia (v1 → Django)
En Postman: **GET** a
```
http://<IP-AWS>/api/v1/productos/
```
Debe responder Django con el catálogo (verás `"servido_por": "Django (Monolito v1)"`).
📸 Captura la petición y la respuesta.

### 2️⃣ Prueba de Estrangulamiento (v2 → Flask)
En Postman: **POST** a
```
http://<IP-AWS>/api/v2/comprar
```
Body → **raw** → **JSON**:
```json
{ "producto_id": 1, "cantidad": 2 }
```
La respuesta debe decir **"Compra procesada exitosamente por el Microservicio Flask (v2)"**.
📸 Captura la petición y la respuesta JSON.

### 3️⃣ Logs de Orquestación (terminal AWS)
```bash
docker compose logs nginx
```
Debe verse el redireccionamiento de peticiones a los dos backends (las líneas de
acceso mostrando `/api/v1/productos/` y `/api/v2/comprar`).
📸 Captura esa salida.

> 💡 Para que los logs muestren ambas rutas, primero haz la petición v1 y la v2
> (pasos 1 y 2), y LUEGO ejecuta `docker compose logs nginx`.

---

## 🧯 Problemas comunes

| Síntoma | Causa / Solución |
| :--- | :--- |
| `host not found in upstream web_django` | Los servicios deben llamarse `web_django` y `pagos_flask` en el compose (ya está así). |
| `502 Bad Gateway` en `/api/v1/` | El monolito aún arranca (migrate+seed). Espera y reintenta. |
| `/api/v2/comprar` da 404 en Django | Verifica que la regla `location /api/v2/comprar` esté ANTES de `location /api/v1/` y `location /` en el nginx.conf. |
| `405` en v2 con GET | El endpoint v2 solo acepta POST. Usa POST en Postman. |
