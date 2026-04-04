from nornir.core.task import Result, Task
from parsers.dispatcher import parse_output

try:
    from nornir_netmiko.tasks import netmiko_send_command
except Exception:  # pragma: no cover
    netmiko_send_command = None


def netmiko_task(task: Task, command: str, parser_name: str, mock: bool = True) -> Result:
    if mock:
        raw = f"MOCK CLI OUTPUT from {task.host.name}: {command}"
        return Result(
            host=task.host,
            result={
                "raw": raw,
                "parsed": parse_output(raw, parser_name, str(task.host.platform or "unknown"), command),
            },
        )

    if netmiko_send_command is None:
        raise RuntimeError("nornir_netmiko is not available")

    cmd_result = task.run(task=netmiko_send_command, command_string=command, name=f"run:{command}")
    raw = str(cmd_result.result)
    return Result(
        host=task.host,
        result={
            "raw": raw,
            "parsed": parse_output(raw, parser_name, str(task.host.platform or "unknown"), command),
        },
    )
