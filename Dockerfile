# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos las dependencias y las instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de los archivos del servidor
COPY server.py .
COPY templates/ templates/

# Exponemos el puerto 5000
EXPOSE 5000

# Comando para ejecutar el servidor
CMD ["python", "server.py"]