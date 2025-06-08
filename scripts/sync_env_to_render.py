#!/usr/bin/env python3
"""
Script para sincronizar variables de entorno desde GitHub Secrets a Render
Requiere: pip install requests
"""

import os
import requests
import json
import sys


def sync_env_to_render():
    """
    Sincroniza las variables de entorno desde los secretos de GitHub a Render
    Utiliza la API de Render para actualizar las variables de entorno
    """
    # Obtener credenciales de Render desde las variables de entorno
    api_key = os.environ.get("RENDER_API_KEY")
    service_id = os.environ.get("RENDER_SERVICE_ID")

    if not api_key or not service_id:
        print(
            "Error: Se requieren las variables de entorno RENDER_API_KEY y RENDER_SERVICE_ID"
        )
        sys.exit(1)

    # URL de la API de Render
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"

    # Headers para la API de Render
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Recopilar variables de entorno desde GitHub Secrets
    # Esta es una demostración - en un entorno real, deberías obtener estos valores
    # de manera más segura (por ejemplo, desde los secretos de GitHub Actions)
    env_vars = []

    # Variables que quieres sincronizar desde GitHub Secrets a Render
    # Estos nombres deben coincidir con los secretos en GitHub
    github_secrets = [
        "ENVIRONMENT",
        # Agrega aquí otros secretos que quieras sincronizar
    ]

    # Recopilar los valores de los secretos
    for secret_name in github_secrets:
        secret_value = os.environ.get(secret_name)
        if secret_value:
            env_vars.append({"key": secret_name, "value": secret_value})

    # Agregar variables con valores fijos
    env_vars.append({"key": "HOST", "value": "0.0.0.0"})

    # Payload para la API de Render
    payload = {"envVars": env_vars}

    # Enviar solicitud a la API de Render
    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(
            f"Variables de entorno actualizadas exitosamente en Render: {response.status_code}"
        )
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar variables de entorno en Render: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_env_to_render()
