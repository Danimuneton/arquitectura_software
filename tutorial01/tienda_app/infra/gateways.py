import datetime
from ..domain.interfaces import ProcesadorPago


class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.
    Simula un banco local escribiendo en un log de auditoría.
    """
    def pagar(self, monto: float) -> bool:
        # Nombre del archivo personalizado con la identidad del estudiante
        # (Paso 4: Evidencia de Ejecución - Log de Auditoría).
        archivo_log = "pagos_locales_DANIEL_MUNETON.log"

        with open(archivo_log, "a") as f:
            f.write(f"[{datetime.datetime.now()}] Transaccion exitosa por: ${float(monto):.2f}\n")
        return True
