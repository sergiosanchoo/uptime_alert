# 🟢 Uptime Alert

Monitorización inteligente y proactiva de infraestructura.

**Uptime Alert** es una solución ligera para controlar el estado de tus equipos y redes en tiempo real. Combina un agente recolector para métricas profundas (CPU, RAM, Disco) y monitorización pasiva (Ping ICMP) para dispositivos sin agente. Todo ello gestionado desde un panel de control web centralizado y con alertas automáticas a Telegram.

---

## Requisitos Previos

Antes de instalar el proyecto, asegúrate de tener instalado en tu sistema:
* **Python 3.9** o superior.
* **Git** (para clonar el repositorio).

---

## Instalación rápida (Para Testers)

Sigue estos pasos en tu terminal para poner a funcionar el sistema en tu propio ordenador:

1. **Clonar el repositorio:**
   git clone https://github.com/TU_USUARIO/uptime_alert.git
   cd uptime_alert

2. **Crear y activar un entorno virtual (Recomendado):**
    * En Windows:
      python -m venv venv
      .\venv\Scripts\activate
    * En Mac/Linux:
      python3 -m venv venv
      source venv/bin/activate

3. **Instalar las dependencias:**
   pip install -r requirements.txt

---

## Cómo usar Uptime Alert

El sistema se divide en dos partes: el Servidor Central (Dashboard) y el Agente (el que envía los datos).

### 1. Iniciar el Servidor Central
Ejecuta el siguiente comando en la raíz del proyecto:
python server.py

Abre tu navegador web y entra en: **http://localhost:5000**. Verás el panel de control vacío, listo para configurarse.

### 2. Iniciar el Agente Recolector
Abre una nueva pestaña en tu terminal (asegúrate de activar el entorno virtual de nuevo) y ejecuta:
python agent.py

Si vuelves al navegador, verás que tu ordenador acaba de aparecer mágicamente en el panel de control con sus métricas en tiempo real.

### 3. Añadir equipos por Ping (Agentless)
Desde el propio panel web, utiliza el formulario superior para añadir la IP de cualquier equipo de tu red (por ejemplo, el router: `192.168.1.1`). El servidor comprobará su estado cada 10 segundos.

---

## Configurar Alertas de Telegram

Para que el sistema te avise al móvil si un equipo se cae o la CPU se satura (>90%), debes configurar tu propio bot:

1. Abre Telegram y busca a **@BotFather** para crear un bot (`/newbot`) y copia el Token.
2. Busca a **@id_bot** para obtener tu Chat ID numérico.
3. Inicia una conversación con tu nuevo bot en Telegram (botón "Iniciar").
4. En el Dashboard web de Uptime Alert, haz clic en **"⚙️ Ajustes de Alertas"** y pega tu Token y Chat ID.
5. ¡Listo! Puedes hacer clic en "Probar Bot" para verificar que la conexión funciona.

---

## Equipo de Desarrollo
Proyecto desarrollado para la asignatura de Ingeniería de Software.
* Sergio Sancho Azcoitia
* Diego Santodomingo Fernández