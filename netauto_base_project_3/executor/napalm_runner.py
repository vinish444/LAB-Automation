from typing import Any, Dict
from nornir.core.task import Result, Task


def napalm_task(task: Task, method_name: str, mock: bool = True) -> Result:
    if mock:
        result: Dict[str, Any] = {
            "method": method_name,
            "host": task.host.name,
            "platform": str(task.host.platform or "unknown"),
            "mock": True,
        }
        return Result(host=task.host, result=result)

    device = task.host.get_connection("napalm", task.nornir.config)

    if not hasattr(device, method_name):
        raise RuntimeError(f"NAPALM method {method_name} not supported on {task.host.name}")

    result = getattr(device, method_name)()
    return Result(host=task.host, result=result)
