# Tutorial 04 — Dockerización y Despliegue en AWS (Entrega)

**Estudiante:** Daniel Muñeton
**Materia:** Arquitectura de Software (AdS 2026)

---

## 1. Objetivo

Empaquetar la "Tienda API" (Tutorial 03) en contenedores Docker y desplegarla
en una instancia AWS EC2, logrando **infraestructura inmutable** y
configuración por variables de entorno.

## 2. Archivos de infraestructura creados

### `Dockerfile`
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### `docker-compose.yml`
Orquesta dos servicios: `db` (PostgreSQL 15 con healthcheck) y `web` (Django).
El servicio `web` espera a que Postgres esté sano, aplica migraciones, carga
datos de prueba y arranca el servidor.

### `requirements.txt`
Incluye `psycopg2-binary` (driver PostgreSQL) y `djangorestframework`, tal como
exige el PDF.

### `settings.py`
La base de datos se lee de variables de entorno (`DB_NAME`, `DB_USER`,
`DB_PASSWORD`, `DB_HOST`, `DB_PORT`), permitiendo el mismo código en local,
Docker y AWS.

## 3. Verificación realizada

- ✅ La imagen Docker **construye sin errores** (`docker build`).
- ✅ Django carga correctamente dentro del contenedor (`manage.py check` → 0 issues).
- ⏳ La prueba de integración completa (`docker compose up`) y el despliegue en
  AWS se ejecutan en la máquina del estudiante / la nube (requieren Docker
  Desktop y la cuenta de AWS Academy).

## 4. Entregable (sección 6)

📸 **Captura del navegador** accediendo a
`http://<IP-PUBLICA-EC2>:8000/api/v1/comprar/`, mostrando la respuesta JSON de
la API servida desde AWS.

> El paso a paso detallado (local + AWS + cómo tomar la captura) está en
> `README_TUTORIAL04.md`.
