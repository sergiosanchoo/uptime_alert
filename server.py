'''from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

# Diccionario temporal para guardar el estado de las máquinas
# (Más adelante lo cambiaremos por una base de datos real)
system_status = {}

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    """Ruta que recibe el JSON del agente"""
    data = request.json
    machine_id = data.get("machine_id")
    
    # Actualizamos el estado de esta máquina en nuestra "memoria"
    system_status[machine_id] = data
    
    # --- LÓGICA DE ALERTAS BÁSICA ---
    if data.get("cpu_percent") > 90.0:
        print(f"¡ALERTA ROJA! La máquina {machine_id} tiene la CPU al {data.get('cpu_percent')}%")
        # (En el próximo sprint, aquí meteremos el código de Telegram)
        
    return jsonify({"status": "success", "message": "Métricas recibidas"}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Ruta para ver el estado de todo desde el navegador"""
    return jsonify(system_status), 200

if __name__ == '__main__':
    print("Iniciando Servidor Central Uptime Alert...")
    app.run(host='0.0.0.0', port=5000)'''

''' import platform
import subprocess
import threading
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Memoria del servidor
system_status = {}  # Aquí guardamos los datos de los Agentes (CPU, RAM)
monitored_ips = {}  # Aquí guardamos los equipos configurados por Ping

def ping_ip(ip):
    """Función que lanza un ping real a una IP dependiendo del Sistema Operativo"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = '1000' if platform.system().lower() == 'windows' else '1'

    command = ['ping', param, '1', timeout_flag, timeout_val, ip]
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0  # Si es 0, el ping ha sido exitoso
    except:
        return False

def ping_loop():
    """Bucle infinito que comprueba las IPs en segundo plano cada 10 segundos"""
    while True:
        for ip in list(monitored_ips.keys()):
            is_alive = ping_ip(ip)
            monitored_ips[ip]['status'] = is_alive
            if is_alive:
                monitored_ips[ip]['last_seen'] = time.time()

            # --- LÓGICA DE ALERTA FUTURA ---
            if not is_alive:
                print(f"¡ALERTA ROJA! El equipo {monitored_ips[ip]['name']} ({ip}) ha dejado de responder al ping.")

        time.sleep(10)

# Iniciamos el motor de pings en un hilo paralelo para que no bloquee el servidor web
threading.Thread(target=ping_loop, daemon=True).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    """Ruta para los Agentes con Python instalado"""
    data = request.json
    machine_id = data.get("machine_id")
    system_status[machine_id] = data
    return jsonify({"status": "success", "message": "Métricas recibidas"}), 200

@app.route('/api/add_device', methods=['POST'])
def add_device():
    """Nueva ruta para añadir equipos por IP desde el Dashboard"""
    data = request.json
    ip = data.get("ip")
    name = data.get("name")

    if ip and name:
        # Añadimos el equipo a la lista de monitorización
        monitored_ips[ip] = {"name": name, "ip": ip, "status": False, "last_seen": 0}
        # Hacemos un ping inicial inmediato
        monitored_ips[ip]['status'] = ping_ip(ip)
        if monitored_ips[ip]['status']:
            monitored_ips[ip]['last_seen'] = time.time()

        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Ahora devuelve tanto los agentes como los pings"""
    return jsonify({
        "agents": system_status,
        "pings": monitored_ips
    }), 200

if __name__ == '__main__':
    print("Iniciando Servidor Central Uptime Alert...")
    app.run(host='0.0.0.0', port=5000) '''
'''import platform
import subprocess
import threading
import time
import json
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Archivo donde guardaremos nuestros equipos para que no se borren
DATA_FILE = "equipos_ping.json"

def cargar_datos():
    """Lee el archivo JSON al arrancar el servidor"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def guardar_datos():
    """Guarda el diccionario actual en el archivo JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(monitored_ips, f)

# Memoria del servidor
system_status = {}  # Los Agentes son en tiempo real, no necesitamos guardarlos en archivo
monitored_ips = cargar_datos()  # ¡Cargamos los Pings desde el disco al arrancar!

def ping_ip(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = '1000' if platform.system().lower() == 'windows' else '1'

    command = ['ping', param, '1', timeout_flag, timeout_val, ip]
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except:
        return False

def ping_loop():
    while True:
        # Usamos list() para evitar errores si se borra un equipo mientras iteramos
        for ip in list(monitored_ips.keys()):
            is_alive = ping_ip(ip)
            monitored_ips[ip]['status'] = is_alive
            if is_alive:
                monitored_ips[ip]['last_seen'] = time.time()

            if not is_alive:
                print(f"¡ALERTA ROJA! El equipo {monitored_ips[ip]['name']} ({ip}) ha caído.")

        time.sleep(10)

threading.Thread(target=ping_loop, daemon=True).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    data = request.json
    machine_id = data.get("machine_id")
    system_status[machine_id] = data
    return jsonify({"status": "success"}), 200

@app.route('/api/add_device', methods=['POST'])
def add_device():
    data = request.json
    ip = data.get("ip")
    name = data.get("name")

    if ip and name:
        monitored_ips[ip] = {"name": name, "ip": ip, "status": False, "last_seen": 0}
        # Guardamos en el archivo cada vez que añadimos uno nuevo
        guardar_datos()

        # Ping inicial
        monitored_ips[ip]['status'] = ping_ip(ip)
        if monitored_ips[ip]['status']:
            monitored_ips[ip]['last_seen'] = time.time()

        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/api/remove_device', methods=['POST'])
def remove_device():
    """Nueva ruta para eliminar un equipo"""
    data = request.json
    ip = data.get("ip")

    if ip in monitored_ips:
        del monitored_ips[ip] # Lo borramos de la memoria
        guardar_datos()       # Guardamos el cambio en el archivo
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "agents": system_status,
        "pings": monitored_ips
    }), 200

if __name__ == '__main__':
    print("Iniciando Servidor Central Uptime Alert...")
    app.run(host='0.0.0.0', port=5000)'''
import platform
import subprocess
import threading
import time
import json
import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATA_FILE = "equipos_ping.json"
CONFIG_FILE = "config.json" # NUEVO: Archivo para guardar la configuración del usuario

def cargar_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    return {}

def guardar_datos(archivo, datos):
    with open(archivo, 'w') as f:
        json.dump(datos, f)

# Memoria del servidor
system_status = {}
monitored_ips = cargar_datos(DATA_FILE)
config_app = cargar_datos(CONFIG_FILE) # Cargamos la configuración de Telegram
alertas_cpu = {}

def enviar_telegram(mensaje):
    """Envía un mensaje de texto leyendo los datos de la configuración del usuario"""
    token = config_app.get("telegram_token", "")
    chat_id = config_app.get("telegram_chat_id", "")

    if not token or not chat_id:
        return # Si el usuario no ha configurado Telegram, no hacemos nada

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

def ping_ip(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = '1000' if platform.system().lower() == 'windows' else '1'

    command = ['ping', param, '1', timeout_flag, timeout_val, ip]
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except:
        return False

def ping_loop():
    while True:
        for ip in list(monitored_ips.keys()):
            estado_anterior = monitored_ips[ip].get('status', True)
            is_alive = ping_ip(ip)
            monitored_ips[ip]['status'] = is_alive

            if is_alive:
                monitored_ips[ip]['last_seen'] = time.time()
                if not estado_anterior:
                    msg = f"✅ *RECUPERADO*\nEl equipo `{monitored_ips[ip]['name']}` ({ip}) ha vuelto a conectarse."
                    enviar_telegram(msg)
            else:
                if estado_anterior:
                    msg = f"🚨 *ALERTA CRÍTICA*\nEl equipo `{monitored_ips[ip]['name']}` ({ip}) ha dejado de responder."
                    enviar_telegram(msg)

        time.sleep(10)

threading.Thread(target=ping_loop, daemon=True).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    data = request.json
    machine_id = data.get("machine_id")
    system_status[machine_id] = data

    cpu_actual = float(data.get("cpu_percent", 0))
    if cpu_actual > 90.0:
        ultimo_aviso = alertas_cpu.get(machine_id, 0)
        if (time.time() - ultimo_aviso) > 300:
            msg = f"⚠️ *RENDIMIENTO ALTO*\nEl equipo `{machine_id}` tiene la CPU al *{cpu_actual}%*."
            enviar_telegram(msg)
            alertas_cpu[machine_id] = time.time()

    return jsonify({"status": "success"}), 200

@app.route('/api/add_device', methods=['POST'])
def add_device():
    data = request.json
    ip = data.get("ip")
    name = data.get("name")

    if ip and name:
        monitored_ips[ip] = {"name": name, "ip": ip, "status": False, "last_seen": 0}
        guardar_datos(DATA_FILE, monitored_ips)
        monitored_ips[ip]['status'] = ping_ip(ip)
        if monitored_ips[ip]['status']:
            monitored_ips[ip]['last_seen'] = time.time()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/api/remove_device', methods=['POST'])
def remove_device():
    data = request.json
    ip = data.get("ip")
    if ip in monitored_ips:
        del monitored_ips[ip]
        guardar_datos(DATA_FILE, monitored_ips)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

# --- NUEVAS RUTAS PARA CONFIGURACIÓN DE TELEGRAM ---
@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        data = request.json
        config_app['telegram_token'] = data.get('telegram_token', '')
        config_app['telegram_chat_id'] = data.get('telegram_chat_id', '')
        guardar_datos(CONFIG_FILE, config_app)
        return jsonify({"status": "success"}), 200

    # Si es GET, devolvemos la configuración (ocultando un poco el token por seguridad)
    token = config_app.get('telegram_token', '')
    safe_token = token[:5] + "..." + token[-5:] if len(token) > 10 else token
    return jsonify({
        "telegram_token": safe_token if token else "",
        "telegram_chat_id": config_app.get('telegram_chat_id', ''),
        "is_configured": bool(token and config_app.get('telegram_chat_id'))
    }), 200

@app.route('/api/test_telegram', methods=['POST'])
def test_telegram():
    enviar_telegram("🤖 *¡Hola!* Tu sistema Uptime Alert se ha conectado correctamente.")
    return jsonify({"status": "success"}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "agents": system_status,
        "pings": monitored_ips
    }), 200

if __name__ == '__main__':
    print("Iniciando Servidor Central Uptime Alert...")
    app.run(host='0.0.0.0', port=5000)