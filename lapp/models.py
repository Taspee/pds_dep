# lockers/models.py
from django.db import models

class Usuario(models.Model):
    # Atributos para el modelo Usuario
    name = models.CharField(max_length=100)  # Nombre del usuario
    email = models.EmailField(unique=True)   # Correo electrónico único

    def __str__(self):
        return self.name

class Casillero(models.Model):
    # Atributos para el modelo Casillero
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relación con el modelo Usuario
    password = models.CharField(max_length=100)  # Contraseña del casillero

    def __str__(self):
        return f"Casillero {self.id} de {self.usuario.name}"

class Contoller(models.Model):
    # Atributos para el modelo Casillero
    casillero = models.ForeignKey(Casillero, on_delete=models.CASCADE)  # Relación con el modelo Usuario

    def __str__(self):
        return self.name
