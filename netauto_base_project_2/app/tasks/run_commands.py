from app.core.celery_app import celery_app
from executor.nornir_runner import execute_commands


@celery_app.task(name="app.tasks.run_device_commands")
def run_device_commands(payload: dict):
    return execute_commands(payload)
