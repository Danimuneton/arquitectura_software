# Tutorial 05 — El Escudo Arquitectónico (Entrega)

**Estudiante:** Daniel Muñeton
**Materia:** Arquitectura de Software (AdS 2026)

---

## 1. Objetivo

Reemplazar el servidor de desarrollo (`runserver`) por una arquitectura de
producción de tres capas: **Nginx** (proxy inverso) + **Gunicorn** (WSGI) +
**Django**, con Django aislado del exterior. Base para el *Strangler Pattern*.

## 2. Archivos clave

### `nginx/nginx.conf`
```nginx
upstream django_backend {
    server web:8000;
}

server {
    listen 80;
    location = /favicon.ico { access_log off; log_not_found off; }
    location / {
        proxy_pass http://django_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

### `docker-compose.yml` (cambios)
- `web`: sin `ports` (Django aislado), arranca con
  `gunicorn Tienda.wsgi:application --bind 0.0.0.0:8000`.
- `nginx`: nuevo servicio `nginx:1.25-alpine` exponiendo el puerto `80`,
  monta `nginx/nginx.conf`.

### `requirements.txt`
Se añadió `gunicorn==23.0.0`.

## 3. Verificación realizada (local)

- ✅ `docker build` exitoso con gunicorn.
- ✅ `gunicorn Tienda.wsgi:application --check-config` → OK (el módulo WSGI carga).
- ✅ `nginx -t` → "syntax is ok / test is successful".

## 4. Entregables (sección 6)

| # | Evidencia | Qué demuestra |
| :--- | :--- | :--- |
| 1 | Navegador en `http://<IP-EC2>/api/v1/comprar/` (sin `:8000`) | Nginx enruta por el puerto 80 |
| 2 | `http://<IP-EC2>:8000` → timeout | Django está aislado del exterior |
| 3 | `docker ps` con `nginx`, `web`, `db` en `Up` | Orquestación de 3 contenedores |

> Guía paso a paso (despliegue + capturas, en Windows) en `README_TUTORIAL05.md`.

## 5. Corrección aplicada respecto al PDF

El PDF indica `gunicorn tienda_project.wsgi:application`, pero la carpeta del
proyecto se llama **`Tienda`**. El comando correcto —ya aplicado— es
`gunicorn Tienda.wsgi:application`. Sin esta corrección, Gunicorn fallaría con
`ModuleNotFoundError: No module named 'tienda_project'`.
