# Imagen del dashboard de Streamlit (app_dashboard.py)
FROM python:3.13-slim

WORKDIR /app

# Primero las dependencias: si no cambia requirements.txt, Docker reutiliza esta capa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sin permisos de administrador dentro del contenedor
RUN useradd --create-home nova
COPY --chown=nova:nova . .
USER nova

EXPOSE 8501
# .streamlit/config.toml escucha solo en localhost; dentro del contenedor tiene
# que ser 0.0.0.0, y compose.yaml publica el puerto solo en 127.0.0.1
CMD ["streamlit", "run", "app_dashboard.py", "--server.address=0.0.0.0", "--server.headless=true"]
