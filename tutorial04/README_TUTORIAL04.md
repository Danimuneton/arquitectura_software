# Tutorial 04 — Dockerización y Despliegue en AWS

**Estudiante:** Daniel Muñeton · **Materia:** Arquitectura de Software (AdS 2026)

De *localhost* a la nube: empaquetar la "Tienda API" (Tutorial 03) en
contenedores **Docker** y desplegarla en **AWS EC2**.

## 📦 Qué contiene esta carpeta

| Archivo | Rol |
| :--- | :--- |
| `Dockerfile` | Receta de la imagen (Python 3.11-slim + deps + código) |
| `docker-compose.yml` | Orquesta Django (`web`) + PostgreSQL (`db`) |
| `requirements.txt` | Dependencias (incluye `psycopg2-binary` y `djangorestframework`) |
| `Tienda/settings.py` | DB vía variables de entorno (`DB_HOST`, `DB_NAME`, …) |

> ✅ **Verificado:** la imagen Docker construye correctamente y Django carga sin
> errores dentro del contenedor (`manage.py check` → 0 issues).

## 🔧 Cambios respecto al Tutorial 03

1. `settings.py`: la base de datos ahora se lee de **variables de entorno**
   (PostgreSQL), no está "quemada". `import os` movido al inicio del archivo.
2. `ALLOWED_HOSTS` acepta la IP pública de EC2 (configurable por entorno).
3. `Dockerfile` en la **raíz** del proyecto (junto a `manage.py`).
4. `docker-compose.yml` corre `migrate` + `seed_datos` automáticamente al
   arrancar, para que la API responda desde el primer momento.

---

## ▶️ Parte A — Prueba local con Docker

Requisito: **Docker Desktop** instalado y corriendo.

```bash
cd tutorial04
docker compose up --build
```

Esto levanta dos contenedores (Postgres + Django), aplica migraciones y carga
datos de prueba. Cuando veas `Starting development server at http://0.0.0.0:8000/`,
abre en el navegador:

- API de compra: **http://localhost:8000/api/v1/comprar/**
- Inventario:    **http://localhost:8000/api/v1/inventario/**

Para detener: `Ctrl + C`, y para limpiar: `docker compose down` (o
`docker compose down -v` para borrar también los datos de Postgres).

> 💡 Si tu versión de Docker usa el comando viejo, es `docker-compose up --build`.

---

## ☁️ Parte B — Despliegue en AWS EC2 (paso a paso)

> ⚠️ Esta parte la haces **tú** en tu cuenta de AWS Academy (requiere tu login).
> La guía replica exactamente el PDF del profesor.

### B.1 Lanzar la instancia EC2
1. Entra a **AWS Academy LMS** y lanza el laboratorio → abre la consola de AWS.
2. **EC2 → Launch Instance.**
3. **Name:** `Servidor-Django`
4. **OS Image:** Amazon Linux 2023 AMI (Free tier eligible)
5. **Instance Type:** `t2.micro`
6. **Key Pair:** selecciona `vockey`
7. **Network Settings:** marca **Allow SSH**, **Allow HTTP** y **Allow HTTPS**.
8. **Launch instance.**

### B.2 Conexión SSH
Selecciona la instancia → botón **Connect** → pestaña **EC2 Instance Connect**
→ abre la terminal en el navegador.

### B.3 Instalar Git y Docker
```bash
# Actualizar el sistema
sudo dnf update -y

# Instalar Git y Docker
sudo dnf install git docker -y

# Iniciar Docker
sudo service docker start

# Permitir usar Docker sin sudo
sudo usermod -a -G docker ec2-user

# IMPORTANTE: cierra la terminal y reconéctate para aplicar permisos
exit
```

### B.4 Instalar el plugin de Docker Compose (Amazon Linux no lo trae)
Vuelve a conectarte y ejecuta:
```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version   # debe imprimir una versión
```

### B.5 Clonar y desplegar
```bash
# Clona TU repositorio
git clone https://github.com/Danimuneton/arquitectura_software.git
cd arquitectura_software/tutorial04

# Levantar en segundo plano, construyendo la imagen
docker compose up -d --build

# Verificar que ambos contenedores corren
docker ps
```

### B.6 Abrir el puerto 8000 (Security Group)
1. EC2 → **Instances** → selecciona tu instancia → pestaña **Security**.
2. Clic en el **Security Group** (ej. `launch-wizard-1`).
3. **Edit inbound rules → Add rule.**
4. **Type:** Custom TCP · **Port range:** `8000` · **Source:** `0.0.0.0/0` (Anywhere).
5. **Save rules.**

---

## 📸 Entregable (sección 6): la captura

Con todo corriendo, abre en **tu navegador**:

```
http://<IP-PUBLICA-EC2>:8000/api/v1/comprar/
```

(La IP pública está en el panel de EC2, columna "Public IPv4 address".)

Debe verse la **respuesta JSON de tu API servida desde AWS** (la Browsable API
de DRF o el JSON crudo). **Toma la captura** de esa pantalla, asegurándote de que
se vea:
- La **URL con la IP pública** de EC2 en la barra del navegador.
- La **respuesta de la API** (interfaz DRF o JSON).

Teclas de captura: 🪟 `Win+Shift+S` · 🍎 `Cmd+Shift+4` · 🐧 `PrtScn`.
Guárdala como `evidencia_aws.png` y súbela a la plataforma.

---

## 🧯 Problemas comunes

| Síntoma | Causa / Solución |
| :--- | :--- |
| `no such table` al abrir la API | El `migrate` no corrió. El compose ya lo hace; si cambiaste el `command`, vuelve a incluir `python manage.py migrate`. |
| La página no carga desde la IP pública | Falta abrir el puerto 8000 en el Security Group (paso B.6). |
| `DisallowedHost` | `ALLOWED_HOSTS` ya incluye `*` por entorno; verifica que la variable no lo esté sobreescribiendo. |
| `docker compose: command not found` en EC2 | Instala el plugin (paso B.4) o usa `docker-compose` (v1). |
| `web` arranca antes que `db` | El compose usa `healthcheck` + `depends_on: condition: service_healthy`. |
