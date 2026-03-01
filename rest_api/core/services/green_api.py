import requests
import traceback
from django.conf import settings

def send_whatsapp_message(chat_id: str, text: str):
    """
    Envía un mensaje a través de Green API utilizando la configuración de Django settings.
    """
    url = f"{settings.GREEN_API_HOST}/waInstance{settings.GREEN_API_INSTANCE_ID}/sendMessage/{settings.GREEN_API_TOKEN}"
    
    # Ensure chat_id has the correct format for WhatsApp (e.g., 56912345678@c.us)
    if "@" not in chat_id:
        chat_id = f"{chat_id}@c.us"

    payload = {
        "chatId": chat_id,
        "message": text
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Mensaje enviado con éxito: {response.text}")
        return response.json()
    except Exception as e:
        traceback.print_exc()
        print(f"Error al enviar mensaje vía Green API: {e}")
        return None
