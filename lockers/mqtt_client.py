import json
import os
import django
import paho.mqtt.client as mqtt
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
import time

recent_messages = {}
# Configura Django para cargar las aplicaciones
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')  # Cambia 'your_project' al nombre de tu proyecto
django.setup()

from lapp.models import Casillero  # Importa el modelo después de configurar Django

# Callback para manejar la conexión al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker successfully")
        client.subscribe("open_locker_g6")  # Suscribirse al topic "open_locker"
        client.subscribe("close_locker_g6")  # Suscribirse al topic "open_locker"
    else:
        print("Failed to connect. Return code:", rc)

# Callback para manejar los mensajes recibidos
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")
    
    if msg.topic == "open_locker_g6":
        try:
            # Parsear el mensaje JSON
            data = json.loads(msg.payload.decode())
            locker_id = data.get("id")

            # Evitar duplicados: verificar si el mensaje ya fue procesado
            current_time = time.time()
            if locker_id in recent_messages and current_time - recent_messages[locker_id] < 5:
                print(f"Duplicate message ignored for locker ID {locker_id}")
                return

            # Actualizar el historial de mensajes
            recent_messages[locker_id] = current_time

            # Obtener el casillero y su usuario
            casillero = get_object_or_404(Casillero, id=locker_id)
            usuario = casillero.usuario

            # Enviar el correo al usuario notificando la apertura
            asunto = 'Notificación de apertura de casillero'
            mensaje = f"<p>Hola {usuario.name},</p><p>Tu casillero con ID {casillero.id} ha sido abierto.</p>"
            destinatarios = [usuario.email]

            email = EmailMessage(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
            )
            email.content_subtype = "html"
            email.send()

            print(f"Notification sent to {usuario.email} for locker ID {casillero.id}")

        except (json.JSONDecodeError, KeyError):
            print("Error processing message or invalid JSON format")
    elif msg.topic == "close_locker_g6":
        try:
            data = json.loads(msg.payload.decode())
            locker_id = data.get("id")

            current_time = time.time()
            if locker_id in recent_messages and current_time - recent_messages[locker_id] < 5:
                print(f"Duplicate message ignored for locker ID {locker_id}")
                return

            recent_messages[locker_id] = current_time

            casillero = get_object_or_404(Casillero, id=locker_id)
            usuario = casillero.usuario

            asunto = 'Notificación de cerrado de casillero'
            mensaje = f"<p>Hola {usuario.name},</p><p>Tu casillero con ID {casillero.id} ha sido cerrado.</p>"
            destinatarios = [usuario.email]

            email = EmailMessage(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
            )
            email.content_subtype = "html"
            email.send()

            print(f"Notification sent to {usuario.email} for locker ID {casillero.id}")

        except (json.JSONDecodeError, KeyError):
            print("Error processing message or invalid JSON format")


# Función para enviar mensajes al broker MQTT
def send_message(topic, mssage):
    result = client.publish(topic, message)
    status = result[0]
    if status == 0:
        print(f"Message '{message}' sent to topic '{topic}'")
    else:
        print(f"Failed to send message to topic {topic}")

# Configuración del cliente MQTT
client = mqtt.Client()
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker
client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
client.loop_start()
