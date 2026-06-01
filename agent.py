import psutil
import requests
import time
import socket

# Aquí pondréis la IP de vuestro servidor central
SERVER_URL = "http://localhost:5000/api/metrics"
MACHINE_ID = socket.gethostname() # Coge el nombre del ordenador automáticamente

def get_metrics():
    """Lee las métricas vitales del sistema"""
    return {
        "machine_id": MACHINE_ID,
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "timestamp": time.time()
    }

def send_metrics():
    """Bucle infinito que envía los datos cada 60 segundos"""
    print(f"Iniciando agente en: {MACHINE_ID}")
    while True:
        try:
            data = get_metrics()
            # Enviamos los datos en formato JSON mediante POST
            response = requests.post(SERVER_URL, json=data)
            print(f"Enviado OK. CPU: {data['cpu_percent']}% | RAM: {data['ram_percent']}%")
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
        
        time.sleep(60) # Pausa de 60 segundos hasta el próximo envío

if __name__ == "__main__":
    send_metrics()