"""
Comando de datos de prueba para el Tutorial 02.

Uso:
    python manage.py seed_datos

Crea (de forma idempotente, sin duplicar) un usuario de prueba y tres libros
con inventario. Evita el error de indentación del shell interactivo porque todo
corre dentro de este comando.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tienda_app.models import Inventario, Libro


class Command(BaseCommand):
    help = "Crea datos de prueba (usuario + libros con inventario) para el Tutorial 02."

    LIBROS = [
        ("Clean Code en Python", 150.0),
        ("Arquitectura Limpia", 250.0),
        ("Patrones de Diseño (GoF)", 180.0),
    ]

    def handle(self, *args, **options):
        User = get_user_model()

        # Usuario de prueba (get_or_create evita el error de username duplicado).
        # Se marca como staff + superuser para que pueda entrar al /admin/.
        usuario, creado = User.objects.get_or_create(
            username="daniel",
            defaults={"email": "daniel@test.com"},
        )
        # Garantizamos permisos de admin y password en cada ejecución
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.set_password("test1234")
        usuario.save()
        if creado:
            self.stdout.write(self.style.SUCCESS(
                "Usuario 'daniel' creado como SUPERUSUARIO (password: test1234)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "Usuario 'daniel' actualizado a SUPERUSUARIO (password: test1234)."
            ))

        # Libros + inventario
        for titulo, precio in self.LIBROS:
            libro, creado = Libro.objects.get_or_create(
                titulo=titulo, defaults={"precio": precio}
            )
            Inventario.objects.get_or_create(libro=libro, defaults={"cantidad": 10})
            estado = "creado" if creado else "ya existía"
            self.stdout.write(f"  - Libro id={libro.id} '{libro.titulo}' ({estado})")

        self.stdout.write(self.style.SUCCESS("\n✅ Datos de prueba listos."))
