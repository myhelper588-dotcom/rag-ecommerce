# Image Python officielle légère
FROM python:3.11-slim

# Dossier de travail dans le container
WORKDIR /app

# Copie les dépendances en premier (optimisation cache Docker)
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code
COPY . .

# Variable d'environnement pour Python
ENV PYTHONUNBUFFERED=1

# Commande de démarrage
CMD ["python", "app/main.py"]