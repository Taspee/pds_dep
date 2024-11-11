from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:usuario_id>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:usuario_id>/eliminar/', views.usuario_delete, name='usuario_delete'),
    path('', views.casilleros_list, name='casilleros_list'),
    path('casilleros/<int:casillero_id>/', views.casillero_detail, name='locker_detail'),  # Detalles del casillero
]
