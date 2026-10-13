from django.conf import settings
from django.db import models


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.titulo


class Inventario(models.Model):
    libro = models.OneToOneField(Libro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()


class Orden(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # Tutorial 02: la Orden ahora puede agrupar varios productos (lista),
    # por lo que `libro` deja de ser obligatorio. Los productos comprados
    # se registran en la relación M2M `productos`.
    libro = models.ForeignKey(Libro, null=True, blank=True, on_delete=models.SET_NULL)
    productos = models.ManyToManyField(Libro, blank=True, related_name="ordenes")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.CharField(max_length=200, blank=True, default="")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
