from ..models import Orden


class OrdenBuilder:
    """
    Patrón Builder (Tutorial 02).
    Ensambla el objeto de dominio `Orden` paso a paso, encapsulando la lógica
    de cálculo y la validación. Expone una Fluent Interface (cada método
    retorna `self`).
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._items = []
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self  # Permite Fluent Interface

    def con_productos(self, productos):
        self._items = productos
        return self

    def para_envio(self, direccion):
        self._direccion = direccion
        return self

    def build(self) -> Orden:
        if not self._usuario or not self._items:
            raise ValueError("Datos insuficientes para crear la orden.")

        # Encapsulamos la lógica de cálculo
        # (float() evita el conflicto Decimal * float que lanza el ORM)
        subtotal = sum(float(p.precio) for p in self._items)
        total_con_iva = round(subtotal * 1.19, 2)

        orden = Orden.objects.create(
            usuario=self._usuario,
            total=total_con_iva,
            direccion_envio=self._direccion,
        )
        # Registramos los productos comprados (relación M2M)
        orden.productos.set(self._items)
        self.reset()
        return orden
