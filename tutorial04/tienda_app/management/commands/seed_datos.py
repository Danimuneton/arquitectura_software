"""
Comando de datos de prueba para el Tutorial 03.

Uso:
    python manage.py seed_datos

Crea (de forma idempotente) un superusuario de prueba y tres libros con
inventario. El superusuario permite autenticarse en la Browsable API de DRF
y en el /admin/.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tienda_app.models import Inventario, Libro


class Command(BaseCommand):
    help = "Crea datos de prueba (superusuario + libros con inventario) para el Tutorial 03."

    LIBROS = [
        ("Clean Code en Python", 150.0),
        ("Arquitectura Limpia", 250.0),
        ("Patrones de Diseño (GoF)", 180.0),
    ]

    def handle(self, *args, **options):
        User = get_user_model()

        usuario, creado = User.objects.get_or_create(
            username="daniel",
            defaults={"email": "daniel@test.com"},
        )
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.set_password("test1234")
        usuario.save()
        estado_u = "creado" if creado else "actualizado"
        self.stdout.write(self.style.SUCCESS(
            f"Usuario 'daniel' {estado_u} como SUPERUSUARIO (password: test1234)."
        ))

        for titulo, precio in self.LIBROS:
            libro, creado = Libro.objects.get_or_create(
                titulo=titulo, defaults={"precio": precio}
            )
            Inventario.objects.get_or_create(libro=libro, defaults={"cantidad": 10})
            estado = "creado" if creado else "ya existía"
            self.stdout.write(f"  - Libro id={libro.id} '{libro.titulo}' ({estado})")

        self.stdout.write(self.style.SUCCESS("\n✅ Datos de prueba listos."))
