# Tutorial 06 — El Primer Estrangulamiento (Entrega)

**Estudiante:** Daniel Muñeton
**Materia:** Arquitectura de Software (AdS 2026)

---

## 1. Objetivo

Aplicar el **Strangler Pattern**: extraer la función de compra del monolito
Django hacia un microservicio Flask, con Nginx enrutando por versión de API
(v1 → Django, v2 → Flask) de forma transparente para el usuario.

## 2. Archivos clave

### `microservicio_pagos/app.py` (Flask v2)
```python
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/api/v2/comprar', methods=['POST'])
def realizar_compra():
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)
    if not producto_id:
        return jsonify({"error": "Falta el ID del producto"}), 400
    return jsonify({
        "mensaje": "Compra procesada exitosamente por el Microservicio Flask (v2)",
        "producto_id": producto_id,
        "cantidad": cantidad,
        "status": "Aprobado"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### `nginx/nginx.conf` (el cerebro del ruteo)
```nginx
upstream django_v1 { server web_django:8000; }
upstream flask_v2  { server pagos_flask:5000; }

server {
    listen 80;
    location /api/v2/comprar { proxy_pass http://flask_v2;  proxy_set_header Host $host; }
    location /api/v1/        { proxy_pass http://django_v1; proxy_set_header Host $host; }
    location /               { proxy_pass http://django_v1; proxy_set_header Host $host; }
}
```

### `docker-compose.yml`
Servicios: `db`, `web_django` (monolito, Gunicorn `Tienda.wsgi`), `pagos_flask`
(microservicio), `nginx` (proxy inverso en el puerto 80).

### Endpoint v1 nuevo
`tienda_app/api/views.py → ProductosAPIView` expone `GET /api/v1/productos/`
servido por Django (para la prueba de coexistencia).

## 3. Verificación realizada (local)

- ✅ `docker build` del microservicio Flask → OK.
- ✅ `POST /api/v2/comprar` {producto_id:1} → 200, "procesada exitosamente por el Microservicio Flask (v2)".
- ✅ `POST /api/v2/comprar` sin producto_id → 400, "Falta el ID del producto".
- ✅ `GET /api/v1/productos/` resuelve en Django (`ProductosAPIView`).
- ✅ `nginx.conf` sintácticamente válido (los upstreams resuelven dentro de la red de compose).

## 4. Entregables (sección 7)

| # | Evidencia | Resultado esperado |
| :--- | :--- | :--- |
| 1 | Postman GET `http://<IP-AWS>/api/v1/productos/` | Responde Django (coexistencia v1) |
| 2 | Postman POST `http://<IP-AWS>/api/v2/comprar` | "procesada exitosamente por el Microservicio Flask" (v2) |
| 3 | `docker compose logs nginx` | Ruteo a los dos backends (v1 y v2) |

> Guía paso a paso (despliegue + Postman + capturas, en Windows) en
> `README_TUTORIAL06.md`.

## 5. Correcciones aplicadas respecto al PDF

1. Gunicorn del monolito: **`Tienda.wsgi`** (no `tienda_project.wsgi`).
2. Se creó el endpoint `GET /api/v1/productos/` que el PDF pide como evidencia 1
   pero que el proyecto no incluía.
