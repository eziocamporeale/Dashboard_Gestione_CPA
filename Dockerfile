# Dockerfile per Dashboard Gestione CPA
FROM python:3.9-slim

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di dipendenze
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea directory necessarie
RUN mkdir -p exports .streamlit

# Espone la porta
EXPOSE 8501

# Comando di avvio
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
