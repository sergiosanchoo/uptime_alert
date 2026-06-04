import platform
import subprocess
import threading
import time
import json
import os
import requests
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Clave secreta necesaria para que las sesiones de Flask funcionen (puedes cambiarla)
app.secret_key = "super_clave_secreta_uptime_alert_2026"

DATA_FILE = "equipos_ping.json"
CONFIG_FILE = "config.json"
USERS_FILE = "users.json" # NUEVO: Archivo para guardar los usuarios

def cargar_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    return {}

def guardar_datos(archivo, datos):
    with open(archivo, 'w') as f:
        json.dump(datos, f)

system_status = {}
monitored_ips = cargar_datos(DATA_FILE)
config_app = cargar_datos(CONFIG_FILE)
alertas_cpu = {}

def enviar_telegram(mensaje):
    token = config_app.get("telegram_token", "")
    chat_id = config_app.get("telegram_chat_id", "")
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

def ping_ip(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = '1000' if platform.system().lower() == 'windows' else '1'
    command = ['ping', param, '1', timeout_flag, timeout_val, ip]
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except: return False

def ping_loop():
    while True:
        for ip in list(monitored_ips.keys()):
            estado_anterior = monitored_ips[ip].get('status', True)
            is_alive = ping_ip(ip)
            monitored_ips[ip]['status'] = is_alive
            if is_alive:
                monitored_ips[ip]['last_seen'] = time.time()
                if not estado_anterior:
                    enviar_telegram(f"✅ *RECUPERADO*\nEl equipo `{monitored_ips[ip]['name']}` ({ip}) ha vuelto a conectarse.")
            else:
                if estado_anterior:
                    enviar_telegram(f"🚨 *ALERTA CRÍTICA*\nEl equipo `{monitored_ips[ip]['name']}` ({ip}) ha dejado de responder.")
        time.sleep(10)

threading.Thread(target=ping_loop, daemon=True).start()

# --- NUEVAS RUTAS DE AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = cargar_datos(USERS_FILE)
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'register':
            if not users: # Solo permite registrar si el archivo está vacío
                # Guardamos la contraseña encriptada por seguridad
                users[username] = generate_password_hash(password)
                guardar_datos(USERS_FILE, users)
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                error = "El administrador ya existe. Por favor, inicia sesión."

        elif action == 'login':
            # Comprobamos que el usuario existe y que la contraseña coincide con el Hash
            if username in users and check_password_hash(users[username], password):
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                error = "Usuario o contraseña incorrectos."

    return render_template('login.html', has_users=bool(users), error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- RUTAS PROTEGIDAS ---
@app.route('/')
def home():
    # Si el usuario no ha iniciado sesión, lo mandamos al login
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

# Las rutas de la API (/api/metrics, /api/status) no las protegemos con sesión
# porque el agente de Python (agent.py) necesita poder enviar datos sin tener que hacer login en la web.

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    data = request.json
    machine_id = data.get("machine_id")
    system_status[machine_id] = data
    cpu_actual = float(data.get("cpu_percent", 0))
    if cpu_actual > 90.0:
        ultimo_aviso = alertas_cpu.get(machine_id, 0)
        if (time.time() - ultimo_aviso) > 300:
            enviar_telegram(f"⚠️ *RENDIMIENTO ALTO*\nEl equipo `{machine_id}` tiene la CPU al *{cpu_actual}%*.")
            alertas_cpu[machine_id] = time.time()
    return jsonify({"status": "success"}), 200

@app.route('/api/add_device', methods=['POST'])
def add_device():
    if not session.get('logged_in'): return jsonify({"error": "No autorizado"}), 401
    data = request.json
    ip = data.get("ip")
    name = data.get("name")
    if ip and name:
        monitored_ips[ip] = {"name": name, "ip": ip, "status": False, "last_seen": 0}
        guardar_datos(DATA_FILE, monitored_ips)
        monitored_ips[ip]['status'] = ping_ip(ip)
        if monitored_ips[ip]['status']: monitored_ips[ip]['last_seen'] = time.time()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/api/remove_device', methods=['POST'])
def remove_device():
    if not session.get('logged_in'): return jsonify({"error": "No autorizado"}), 401
    data = request.json
    ip = data.get("ip")
    if ip in monitored_ips:
        del monitored_ips[ip]
        guardar_datos(DATA_FILE, monitored_ips)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if not session.get('logged_in'): return jsonify({"error": "No autorizado"}), 401
    if request.method == 'POST':
        data = request.json
        config_app['telegram_token'] = data.get('telegram_token', '')
        config_app['telegram_chat_id'] = data.get('telegram_chat_id', '')
        guardar_datos(CONFIG_FILE, config_app)
        return jsonify({"status": "success"}), 200
    token = config_app.get('telegram_token', '')
    safe_token = token[:5] + "..." + token[-5:] if len(token) > 10 else token
    return jsonify({"telegram_token": safe_token if token else "", "telegram_chat_id": config_app.get('telegram_chat_id', ''), "is_configured": bool(token and config_app.get('telegram_chat_id'))}), 200

@app.route('/api/test_telegram', methods=['POST'])
def test_telegram():
    if not session.get('logged_in'): return jsonify({"error": "No autorizado"}), 401
    enviar_telegram("🤖 *¡Hola!* Tu sistema Uptime Alert se ha conectado correctamente.")
    return jsonify({"status": "success"}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    if not session.get('logged_in'): return jsonify({"error": "No autorizado"}), 401
    return jsonify({"agents": system_status, "pings": monitored_ips}), 200

if __name__ == '__main__':
    print("Iniciando Servidor Central Uptime Alert...")
    app.run(host='0.0.0.0', port=5000)