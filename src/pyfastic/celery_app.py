import os
from celery import Celery

# We maken de Celery instance aan
# 'pyfastic' is hier de naam van de 'main' module voor Celery
celery_app = Celery(
    "pyfastic",
    broker=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/0",
    backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/0",
    include=["pyfastic.tasks"]  # HEEL BELANGRIJK: Vertel Celery waar de taken staan
)

# Optionele configuratie
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()