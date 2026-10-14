# Tutorial 05 — El Escudo Arquitectónico (Nginx + Gunicorn)

**Estudiante:** Daniel Muñeton · **Materia:** Arquitectura de Software (AdS 2026)

Arquitectura de producción de **tres capas**:
**Nginx** (proxy inverso, puerto 80) → **Gunicorn** (servidor WSGI) → **Django**.
Django queda **aislado** (ya no expone el puerto 8000). Base para el futuro
*Strangler Pattern*.

## 📦 Qué cambió respecto al Tutorial 04

| Cambio | Archivo | Detalle |
| :--- | :--- | :--- |
| Añadir Gunicorn | `requirements.txt` | `gunicorn==23.0.0` |
| Config de Nginx | `nginx/nginx.conf` | Proxy inverso puerto 80 → `web:8000` |
| Orquestación | `docker-compose.yml` | `web` sin `ports`, arranca con Gunicorn; nuevo servicio `nginx` en el puerto 80 |

> ⚠️ **Corrección importante respecto al PDF:** el PDF usa
> `gunicorn tienda_project.wsgi:application`, pero en este proyecto la carpeta
> del proyecto se llama **`Tienda`**, no `tienda_project`. El comando correcto
> (ya aplicado en el `docker-compose.yml`) es:
> `gunicorn Tienda.wsgi:application --bind 0.0.0.0:8000`

> ✅ **Verificado localmente:** la imagen construye, Gunicorn carga
> `Tienda.wsgi:application` (`--check-config` OK) y `nginx.conf` pasa `nginx -t`.

---

## ▶️ Prueba local con Docker (opcional)

```powershell
cd tutorial05
docker compose up --build
```

Abre `http://localhost/api/v1/comprar/` (puerto **80**, SIN `:8000`). Debe
responder la API a través de Nginx.

Para detener: `Ctrl + C`; para limpiar: `docker compose down`.

---

## ☁️ Despliegue en AWS EC2

> Reutiliza la instancia del Tutorial 04 (o crea una nueva siguiendo la guía del
> `tutorial04/README_TUTORIAL04.md`, incluyendo la instalación de `docker`,
> `docker compose` y `buildx`).

En la terminal SSH de tu instancia EC2:

```bash
# 1. Entrar al proyecto y traer los últimos cambios
cd arquitectura_software
git pull origin main
cd tutorial05

# 2. Reconstruir y levantar la nueva arquitectura (3 contenedores)
docker compose up -d --build

# 3. Verificar que los TRES contenedores estén corriendo
docker ps
```

### Abrir el puerto 80 en el Security Group
Como ahora Nginx escucha en el puerto **80** (HTTP), hay que abrirlo:
1. Consola AWS → **EC2 → Security Groups** → selecciona el grupo de tu instancia.
2. **Edit inbound rules → Add rule.**
3. **Type:** HTTP · **Port range:** `80` · **Source:** `0.0.0.0/0`.
4. **Save rules.**

> 💡 El puerto 8000 ya no hace falta abrirlo (de hecho, debe quedar cerrado para
> demostrar el aislamiento). Puedes dejar la regla del 8000 o quitarla; lo que
> importa es que la **evidencia 2** demuestre que el 8000 no responde.

---

## 📸 Entregables (sección 6): las 3 capturas

### 1️⃣ Evidencia de Enrutamiento (navegador)
Abre en tu navegador:
```
http://<IP-PUBLICA-EC2>/api/v1/comprar/
```
**SIN el `:8000`.** Debe verse la API (la Browsable API de DRF o el JSON).
Que funcione sin puerto demuestra que **Nginx enruta por el puerto 80**.
📸 Captura asegurándote de que la **barra de URL** (sin `:8000`) sea visible.

### 2️⃣ Evidencia de Aislamiento (debe FALLAR)
En tu navegador o terminal de Windows (PowerShell), intenta:
```
http://<IP-PUBLICA-EC2>:8000
```
Debe quedarse colgado / dar **timeout** (no responde). Esto prueba que Django
está aislado y solo accesible vía Nginx.

Opción navegador: abre esa URL → espera a que diga "no se puede acceder" / "tardó
demasiado en responder" → 📸 captura esa pantalla (con la URL `:8000` visible).

Opción PowerShell (muestra el timeout en texto):
```powershell
curl.exe -m 10 http://<IP-PUBLICA-EC2>:8000
```
Debe terminar con un error de timeout tras ~10s. 📸 captura la terminal.

### 3️⃣ Evidencia de Orquestación (terminal AWS)
En la terminal SSH de EC2:
```bash
docker ps
```
📸 Captura mostrando los **tres** contenedores (`nginx`, `web`, `db`) en estado
**Up**.

---

## 🧯 Problemas comunes

| Síntoma | Causa / Solución |
| :--- | :--- |
| `ModuleNotFoundError: No module named 'tienda_project'` | El PDF trae mal el nombre. Debe ser `Tienda.wsgi` (ya corregido en el compose). |
| `502 Bad Gateway` en Nginx | El servicio `web` aún está arrancando (migrate+seed). Espera unos segundos y recarga; revisa `docker compose logs web`. |
| La API no abre en el puerto 80 | Falta abrir el puerto 80 en el Security Group. |
| El puerto 8000 SÍ responde | Verifica que quitaste la sección `ports` del servicio `web` en `docker-compose.yml`. |
| `compose build requires buildx` en EC2 | Instala buildx (ver guía del Tutorial 04). |
