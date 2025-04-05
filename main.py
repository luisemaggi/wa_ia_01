from flask import Flask, request, jsonify
import os
import requests
import json
import time
from dotenv import load_dotenv

# Cargar variables de entorno con opción de override
load_dotenv(override=True)

# Configurar manualmente las variables de entorno para asegurar que estén disponibles
os.environ.setdefault("WHATSAPP_API_TOKEN", 
"EAARIXNjFcY8BOZCV8R3KDKncSOmYXiHSU0dVmHKw0j8GRQSGtcKc8Cdx8js4CqT6ZAFqkTlUiNLwyagdnjwPRfMlEQ2bwqN9DQlekSteAQbFgF4ZAJuaGD4aZCFYfplzcWeIZAR3fqpbWBZAlt9X8rpPCNuSF3R14YZCHAFtXqLE1mLTY5d0EZBMZBdlOY0x0dHMTGgCXfikQZC5zY9CRWiS7hB7B70RREgP6pOJ3qXCWh")
os.environ.setdefault("WHATSAPP_PHONE_ID", "640597892460269")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "123456")

# Obtener variables de entorno
api_token = os.environ.get("WHATSAPP_API_TOKEN")
phone_id = os.environ.get("WHATSAPP_PHONE_ID")
verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")

print("=== Verificación de variables de entorno ===")
token_status = 'Configurado (longitud: ' + str(len(api_token)) + ')' if api_token else 'NO CONFIGURADO'
print(f"WHATSAPP_API_TOKEN: {token_status}")
print(f"WHATSAPP_PHONE_ID: {phone_id if phone_id else 'NO CONFIGURADO'}")
print(f"WHATSAPP_VERIFY_TOKEN: {verify_token if verify_token else 'NO CONFIGURADO'}")
print("==========================================")

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verificación del webhook
        try:
            verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')

            print(f"Verificación del webhook: mode={mode}, token={token}, challenge={challenge}")

            if mode == "subscribe" and token == verify_token:
                print("Verificación exitosa")
                return challenge, 200
            else:
                print(f"Error de verificación: token recibido '{token}' != token esperado '{verify_token}'")
                return "Error de verificación", 403
        except Exception as e:
            print(f"Error en la verificación del webhook: {e}")
            return "Error interno del servidor", 500

    elif request.method == 'POST':
        # Manejo de mensajes entrantes de WhatsApp
        try:
            data = request.get_json()
            print("Mensaje recibido:", json.dumps(data, indent=2))  # Depuración con formato
            
            # Extraer información del mensaje
            if data and 'entry' in data and len(data['entry']) > 0:
                entry = data['entry'][0]
                if 'changes' in entry and len(entry['changes']) > 0:
                    change = entry['changes'][0]
                    if 'value' in change and 'messages' in change['value'] and len(change['value']['messages']) > 0:
                        message = change['value']['messages'][0]
                        if 'from' in message:  # Número de teléfono del remitente
                            sender = message['from']
                            print(f"Número de remitente detectado: {sender}")
                            
                            # Obtener texto del mensaje (si existe)
                            message_text = "No se pudo obtener el texto del mensaje"
                            if 'text' in message and 'body' in message['text']:
                                message_text = message['text']['body']
                                print(f"Texto del mensaje: {message_text}")
                            
                            # Esperar un poco antes de responder (para evitar límites de frecuencia)
                            time.sleep(1)
                            
                            # Responde al mensaje con hasta 3 intentos
                            response_text = f"¡Hola! He recibido tu mensaje: '{message_text}'"
                            print(f"Enviando respuesta: {response_text}")
                            
                            # Intentar enviar el mensaje hasta 3 veces
                            for attempt in range(3):
                                try:
                                    result = send_whatsapp_message(sender, response_text)
                                    if not result.get('error'):
                                        print(f"Mensaje enviado correctamente en el intento {attempt+1}")
                                        break
                                    else:
                                        print(f"Error en el intento {attempt+1}, reintentando...")
                                        time.sleep(2)  # Esperar antes de reintentar
                                except Exception as e:
                                    print(f"Excepción en el intento {attempt+1}: {e}")
                                    time.sleep(2)  # Esperar antes de reintentar
            
            return jsonify({"status": "Evento recibido"}), 200
        except Exception as e:
            print(f"Error al procesar el mensaje: {e}")
            return "Error interno del servidor", 500

def send_whatsapp_message(recipient, message_text):
    """Envía un mensaje a través de la API de WhatsApp Cloud"""
    try:
        # Obtener variables de entorno
        token = os.environ.get("WHATSAPP_API_TOKEN")
        phone_id = os.environ.get("WHATSAPP_PHONE_ID")
        
        # Verificación simplificada
        if not token:
            print("ERROR: El token de WhatsApp no está configurado")
            return {"error": "Token de WhatsApp no configurado"}
            
        if not phone_id:
            print("ERROR: El ID del teléfono de WhatsApp no está configurado")
            return {"error": "ID de teléfono no configurado"}
        
        print(f"Token (longitud: {len(token)}): {token[:5]}...{token[-5:]}")
        print(f"Phone ID: {phone_id}")
        print(f"Recipient: {recipient}")
        
        # URL de la API de WhatsApp
        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
        
        # Encabezados
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Cuerpo de la solicitud
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_text
            }
        }
        
        print(f"Enviando solicitud a la API de WhatsApp: {json.dumps(data)}")
        
        # Enviar la solicitud
        response = requests.post(url, headers=headers, json=data)
        print(f"Código de respuesta: {response.status_code}")
        print(f"Respuesta completa: {response.text}")
        
        if response.status_code != 200:
            print(f"Error al enviar mensaje. Código: {response.status_code}, Respuesta: {response.text}")
            return {"error": f"Error {response.status_code}", "details": response.text}
        else:
            print("Mensaje enviado correctamente")
            return response.json()
            
    except Exception as e:
        error_message = str(e)
        print(f"Excepción al enviar mensaje de WhatsApp: {error_message}")
        return {"error": "Excepción", "message": error_message}

if __name__ == '__main__':
    print("\n=== Iniciando servidor Flask ===")
    print(f"Webhook verificable en: http://localhost:8000/webhook")
    print(f"Asegúrate de que ngrok esté redirigiendo a este puerto")
    print("===============================\n")
    
    # Cambia el puerto a 8000
    app.run(host='0.0.0.0', port=8000, debug=True)
