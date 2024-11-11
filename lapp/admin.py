# lockers/admin.py
from django.contrib import admin
from .models import Usuario, Casillero

admin.site.register(Usuario)
admin.site.register(Casillero)