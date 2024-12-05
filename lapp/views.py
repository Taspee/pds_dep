from django.shortcuts import render, get_object_or_404, redirect
from .models import Casillero, Usuario, Controller
from .email_operations import EmailOperations  # Importa la clase
from django.conf import settings  # Para obtener las credenciales desde settings.py
from .forms import CasilleroPasswordForm
from .forms import UsuarioForm  # Asegúrate de crear un formulario para Usuario
from django.core.mail import EmailMessage
from lockers.mqtt_client import send_message, on_message, on_connect
from django.http import HttpResponse
import json
from django.http import JsonResponse
import time


def mqtt_message_received(request):
    # Handle received MQTT messages here
    return HttpResponse("Received MQTT message!")

# Vista para mostrar el estado de los casilleros
def casilleros_list(request):
    casilleros = Casillero.objects.select_related('usuario').all()  # Obtiene los casilleros con sus usuarios
    print(casilleros)  # Verifica que los datos están siendo recuperados
    return render(request, 'casilleros_list.html', {'casilleros': casilleros})

def casillero_detail(request, casillero_id):
    casillero = get_object_or_404(Casillero, id=casillero_id)
    usuarios = Usuario.objects.all()  # Obtén todos los usuarios para mostrarlos en el formulario
    form = None  # Inicializa el formulario para evitar errores de referencia

    if request.method == 'POST':
        # Si se presionó el botón para cambiar la contraseña
        if 'cambiar_contraseña' in request.POST:
            new_password = request.POST.get('new_password')
            if new_password and len(new_password) == 4:
                casillero.password = new_password
                casillero.save()
                
                formatted_password = ""
                for char in casillero.password:
                    if char == '1':
                        formatted_password += '✋'
                    elif char == '2':
                        formatted_password += '👆'
                    elif char == '3':
                        formatted_password += '🤜'
                    elif char == '4':
                        formatted_password += '🫵'
                    elif char == '5':
                        formatted_password += '👌'
                    elif char == '6':
                        formatted_password += '🫷'
                    else:
                        formatted_password += char

                # Enviar correo electrónico notificando el cambio de contraseña
                asunto = 'Tu contraseña ha sido cambiada'
                mensaje = f"""
                <p>Hola {casillero.usuario.name}, tu contraseña ha sido cambiada con éxito.</p>
                <p>Tu nueva contraseña es: {formatted_password}</p>
                <p>Recuerda que debes presionar el botón correspondiente al casillero {casillero.id}.</p>
                """
                destinatarios = [casillero.usuario.email]

                email = EmailMessage(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    destinatarios,
                )
                email.content_subtype = "html"
                email.send()

                # Publicar el mensaje MQTT en el tópico 'set_locker_pw'
                mqtt_message = {
                    "id": casillero.id,
                    "password": casillero.password
                }
                send_message("set_locker_g6", json.dumps(mqtt_message))  # Publicar el mensaje con JSON

                return redirect('locker_detail', casillero_id=casillero.id)  # Redirige para ver los cambios

        # Si se presionó el botón para cambiar el usuario
        elif 'cambiar_usuario' in request.POST:
            nuevo_usuario_id = request.POST.get('nuevo_usuario_id')
            if nuevo_usuario_id:
                nuevo_usuario = Usuario.objects.get(id=nuevo_usuario_id)
                casillero.usuario = nuevo_usuario
                casillero.save()

                formatted_password = ""
                for char in casillero.password:
                    if char == '1':
                        formatted_password += '✋'
                    elif char == '2':
                        formatted_password += '👆'
                    elif char == '3':
                        formatted_password += '🤜'
                    elif char == '4':
                        formatted_password += '🫵'
                    elif char == '5':
                        formatted_password += '👌'
                    elif char == '6':
                        formatted_password += '🫷'
                    else:
                        formatted_password += char

                # Enviar correo electrónico al nuevo usuario notificando el ID del casillero y su contraseña
                asunto = 'Nuevo Casillero Asignado'
                mensaje = f"""
                <p>Hola {nuevo_usuario.name},</p>
                <p>Se te ha asignado el Casillero: {casillero.id}.</p>
                <p>Tu contraseña es: {formatted_password}</p>
                """
                destinatarios = [nuevo_usuario.email]

                email = EmailMessage(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    destinatarios,
                )
                email.content_subtype = "html"
                email.send()

                return redirect('locker_detail', casillero_id=casillero.id)

    # Inicializa el formulario si no es un POST o si no hay cambios
    if not form:
        form = CasilleroPasswordForm(instance=casillero)

    return render(request, 'casillero_detail.html', {
        'casillero': casillero,
        'form': form,
        'usuarios': usuarios,  # Pasar la lista de usuarios a la plantilla
    })


# Vista para listar usuarios
def usuarios_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})

# Vista para crear un usuario
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuario_form.html', {'form': form})


# Vista para editar un usuario
def usuario_update(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()

            # Configuración del correo electrónico
            asunto = 'Tu contraseña ha sido cambiada'
            mensaje = f'Hola {usuario.name}, tu contraseña ha sido actualizada con éxito.'
            destinatarios = [usuario.email]  # Usa el email del usuario en la base de datos

            # Instancia de EmailOperations sin pasar username y password
            email_ops = EmailOperations()  # No necesitas pasar username ni password aquí
            
            # Enviar el correo
            email_ops.send_email(
                receivers_email=destinatarios,
                subject=asunto,
                message=mensaje
            )

            return redirect('usuarios_list')
    
    else:
        form = UsuarioForm(instance=usuario)
    
    return render(request, 'usuario_form.html', {'form': form})



# Vista para eliminar un usuario
def usuario_delete(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuarios_list')
    return render(request, 'usuario_confirm_delete.html', {'usuario': usuario})


def user_dashboard(request):
    # Contexto vacío o con datos iniciales para pruebas
    context = {
        "total_openings_monthly": 120,
        "peak_usage_hour": "14:00",
        "average_opening_time_weekly": 7.5,
        "recent_activity": [
            {"date": "2024-12-01", "locker_id": 1, "action": "Opened", "details": "Locker opened by User 1"},
            {"date": "2024-12-01", "locker_id": 2, "action": "Closed", "details": "Locker closed by User 2"},
        ]
    }
    return render(request, 'user_dashboard.html', context)

def show_controllers(request):
    controller = Controller.objects.all()
    return render(request,'controllers.html',{'controller':controller})

def locker_per_controller(request,controller_id):
    controller = get_object_or_404(Controller, id=controller_id)
    casilleros= Casillero.objects.filter(controller_id=controller_id)
    return render(request, 'casilleros_list.html', {'casilleros':casilleros})

def check_status(request, controller_id):
    global conectedc1
    conectedc1 = True
    if controller_id == 1:
        mqtt_message = {
            "id": controller_id,
                    }
        send_message("check_status_c1_g6", json.dumps(mqtt_message))  # Publicar el mensaje con JSON
        for _ in range(5):
            if conectedc1:
                break
            time.sleep(1)
        if conectedc1:
            return JsonResponse({'status': 'conected'})
        else:
            return JsonResponse({'status': 'Not conected'})

    else:
        mqtt_message = {
            "id": controller_id,
                    }
        send_message("check_status_c2_g6", json.dumps(mqtt_message))  # Publicar el mensaje con JSON

    return render(request,'controllers.html')



