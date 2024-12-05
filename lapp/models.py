# lockers/models.py
from django.db import models
from django.utils.timezone import now

class Usuario(models.Model):
    # Atributos para el modelo Usuario
    name = models.CharField(max_length=100)  # Nombre del usuario
    email = models.EmailField(unique=True)   # Correo electrónico único

    def __str__(self):
        return self.name

class Controller(models.Model):
    name = models.CharField(max_length=200)

    def __int__(self):
        return self.id


class Casillero(models.Model):
    # Atributos para el modelo Casillero
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relación con el modelo Usuario
    password = models.CharField(max_length=100)  # Contraseña del casillero
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE, related_name='casilleros')

    def __int__(self):
        return self.id

class MqttInteraction(models.Model):
    timestamp = models.DateTimeField(default=now)  
    action = models.CharField(max_length=50)  
    topic = models.CharField(max_length=255)  
    user = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)  
    
    def __int__(self):
        return self.id
