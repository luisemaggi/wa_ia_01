# WhatsApp Webhook Project

Este proyecto implementa un webhook para manejar mensajes entrantes y salientes a través de la API de WhatsApp Cloud. Utiliza Flask como framework para crear un servidor web que interactúa con la API de WhatsApp.

## Características

- **Verificación del Webhook**: Valida las solicitudes entrantes desde la API de WhatsApp.
- **Recepción de Mensajes**: Procesa mensajes entrantes y extrae información relevante como el remitente y el contenido del mensaje.
- **Envío de Respuestas**: Responde automáticamente a los mensajes recibidos con un texto personalizado.
- **Manejo de Errores**: Incluye manejo de excepciones para garantizar la estabilidad del servidor.

## Requisitos

- Python 3.8 o superior
- Flask
- requests
- python-dotenv

## Configuración

1. Clona este repositorio:
   ```bash
   git clone https://github.com/luisemaggi/wa_ia_01.git
   cd wa_ia_01