# lockers/admin.py
from django.contrib import admin
from .models import Usuario, Casillero, Controller

admin.site.register(Usuario)
admin.site.register(Casillero)
admin.site.register(Controller)