from app.models.schemas import RunRequest
from app.tasks.run_commands import run_device_commands


def submit_run_job(request: RunRequest):
    commands = request.commands or [request.command]
    payload = request.model_dump()
    payload["commands"] = commands
    return run_device_commands.delay(payload)
