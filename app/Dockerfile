# 1️⃣ Imagen base oficial de Python
FROM python:3.11-slim

# 2️⃣ Crear un usuario no root por seguridad
RUN useradd -m webadmin

# 3️⃣ Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4️⃣ Copiar el archivo de la aplicación al contenedor
COPY --chown=webadmin:webadmin app.py /app/
COPY --chown=webadmin:webadmin static/ /app/static/

# 5️⃣ Instalar Flask (sin cachear para que la imagen sea más ligera)
RUN pip install --no-cache-dir flask psycopg2-binary
RUN pip install --no-cache-dir flask psycopg2-binary redis

# 6️⃣ Cambiar al usuario normal (no root)
USER webadmin

# 7️⃣ Definir el puerto en el que escucha la app
EXPOSE 8000

# 8️⃣ Comando que se ejecutará al arrancar el contenedor
CMD ["python", "app.py"]
