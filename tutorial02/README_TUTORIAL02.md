# Tutorial 02 — Patrones Creacionales en Django

**Estudiante:** Daniel Muñeton · **Materia:** Arquitectura de Software (AdS 2026)

Implementación de **Factory Method** (desacople de infraestructura por variable
de entorno) y **Builder** (construcción de objetos de dominio complejos).

## 📦 Pasos aplicados

| Paso | Qué se hizo | Archivo |
| :--- | :--- | :--- |
| 1 | Factory Method (`PaymentFactory` + `MockPaymentProcessor`) | `tienda_app/infra/factories.py` |
| 2 | Builder con fluent interface (`OrdenBuilder`) | `tienda_app/domain/builders.py` |
| 3 | Integración en el Service Layer (`ejecutar_proceso_compra`) | `tienda_app/services.py` |
| 4 | Despliegue configurable por `PAYMENT_PROVIDER` | — |

## ✅ Entregables

1. **Captura de consola** mostrando `[DEBUG] Mock Payment...` (ver abajo cómo tomarla).
2. **Código**: `infra/factories.py` y `domain/builders.py`.
3. **Reflexión** sobre el Builder → en `ENTREGA_tutorial02.md`.

La evidencia de texto ya ejecutada está en `evidencia_consola.txt`.

---

## ▶️ Cómo ejecutar y reproducir la evidencia

```bash
cd tutorial02
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install "django>=5.2,<5.3" djangorestframework
python manage.py migrate

# Crear datos de prueba (usuario + libros con stock)
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from tienda_app.models import Libro, Inventario
>>> U = get_user_model(); u = U.objects.create_user("daniel", password="test1234")
>>> for t, p in [("Clean Code en Python",150.0),("Arquitectura Limpia",250.0)]:
...     l = Libro.objects.create(titulo=t, precio=p); Inventario.objects.create(libro=l, cantidad=10)
>>> exit()
```

### Ejecutar en modo MOCK (el que genera el `[DEBUG]`)

```bash
# Linux / Mac / GitBash:
PAYMENT_PROVIDER=MOCK python manage.py runserver

# Windows PowerShell:
$env:PAYMENT_PROVIDER="MOCK"; python manage.py runserver
```

Luego inicia sesión en `/admin/` (crea un superusuario si quieres) o usa el
usuario `daniel`, y entra a `http://127.0.0.1:8000/compra/1/` → pulsa el botón
de confirmar compra. En la **terminal donde corre el servidor** aparecerá:

```
[DEBUG] Mock Payment: Procesando pago de $178.5 sin cargo real.
```

---

## 📸 Cómo tomar el screenshot de la consola de Django

El profesor pide una **captura de pantalla de la consola** mostrando el mensaje
`[DEBUG] Mock Payment...`. Aquí va el paso a paso según tu sistema operativo:

### 1. Deja la terminal visible
Arranca el servidor en modo MOCK (comando de arriba) y realiza una compra desde
el navegador. El mensaje `[DEBUG] Mock Payment...` se imprime en **la terminal**,
no en el navegador. Asegúrate de que esa línea sea visible en pantalla.

### 2. Captura la pantalla

**🪟 Windows:**
- `Win + Shift + S` → abre la herramienta de recorte; selecciona el área de la
  terminal. La imagen queda en el portapapeles (pégala en Paint/Word con `Ctrl+V`).
- O pulsa `Impr Pant` (PrtScn) para capturar toda la pantalla.
- O busca **"Recortes"** / "Snipping Tool" en el menú inicio.

**🍎 macOS:**
- `Cmd + Shift + 4` → el cursor se vuelve una cruz; arrastra para seleccionar la
  terminal. La imagen se guarda en el Escritorio.
- `Cmd + Shift + 3` captura la pantalla completa.

**🐧 Linux:**
- Tecla `Impr Pant` (PrtScn) para pantalla completa.
- `Shift + PrtScn` para seleccionar un área (GNOME).
- O usa la app **"Capturas de pantalla" / "Screenshot"**, o `flameshot gui` si lo tienes.

### 3. Qué debe verse en la captura
- El **prompt o comando** con `PAYMENT_PROVIDER=MOCK` (idealmente visible arriba).
- La línea `[DEBUG] Mock Payment: Procesando pago de $... sin cargo real.`
- Opcional pero recomendado: que se note que es tu entorno (ruta del proyecto).

### 4. Guarda el archivo
Guarda la imagen como `evidencia_mock_payment.png` y súbela a la asignación
`tutorial02` junto con los dos archivos de código y la reflexión.

> 💡 Tip: si prefieres no usar el navegador, puedes reproducir la salida
> directamente ejecutando el bloque del shell que está en `evidencia_consola.txt`
> con `PAYMENT_PROVIDER=MOCK python manage.py shell` y capturar esa terminal.

---

> **Nota de base de datos:** se usa SQLite para ejecución local (el `settings.py`
> conserva comentada la configuración PostgreSQL original del profesor).
