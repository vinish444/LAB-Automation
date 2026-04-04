from __future__ import annotations

from typing import Any, Dict, List

from nornir import InitNornir
from nornir.core.filter import F
from nornir.core.task import Result, Task

from app.core.config import settings
from parsers.dispatcher import parse_output

try:
    from nornir_netmiko.tasks import netmiko_send_command
except Exception:  # pragma: no cover
    netmiko_send_command = None


def _mock_task(task: Task, commands: List[str], parser_name: str) -> Result:
    per_command = {}
    for command in commands:
        raw_output = f"MOCK OUTPUT from {task.host.name}: {command}"
        per_command[command] = {
            "raw": raw_output,
            "parsed": parse_output(raw_output, parser_name, platform=str(task.host.platform or "unknown"), command=command),
        }
    return Result(host=task.host, result=per_command)


def _netmiko_task(task: Task, commands: List[str], parser_name: str) -> Result:
    if netmiko_send_command is None:
        raise RuntimeError("nornir_netmiko is not available")
    per_command = {}
    for command in commands:
        cmd_result = task.run(task=netmiko_send_command, command_string=command, name=f"run:{command}")
        raw_output = str(cmd_result.result)
        per_command[command] = {
            "raw": raw_output,
            "parsed": parse_output(raw_output, parser_name, platform=str(task.host.platform or "unknown"), command=command),
        }
    return Result(host=task.host, result=per_command)


def _build_nr() -> Any:
    return InitNornir(config_file=settings.nornir_config_file)


def _apply_filters(nr: Any, payload: Dict[str, Any]) -> Any:
    inventory = payload.get("inventory") or {}
    hosts = inventory.get("hosts") or []
    groups = inventory.get("groups") or []

    filtered = nr
    if hosts:
        combined = None
        for host in hosts:
            expr = F(name=host)
            combined = expr if combined is None else combined | expr
        filtered = filtered.filter(combined)

    if groups:
        combined = None
        for group in groups:
            expr = F(groups__contains=group)
            combined = expr if combined is None else combined | expr
        filtered = filtered.filter(combined)

    return filtered


def _normalize_results(result: Any) -> Dict[str, Any]:
    final = {}
    for host, multi in result.items():
        host_payload = {"failed": multi.failed, "commands": {}}
        for item in multi:
            if isinstance(item.result, dict):
                host_payload["commands"].update(item.result)
            elif item.name.startswith("run:"):
                host_payload["commands"][item.name.replace("run:", "", 1)] = {
                    "raw": str(item.result),
                    "parsed": str(item.result),
                }
        final[host] = host_payload
    return final


def execute_commands(payload: Dict[str, Any]) -> Dict[str, Any]:
    commands = payload.get("commands") or []
    parser_name = payload.get("parser", "raw")
    mock = payload.get("mock", True)

    nr = _build_nr()
    nr = _apply_filters(nr, payload)

    if not nr.inventory.hosts:
        return {
            "status": "completed",
            "device_count": 0,
            "results": {},
            "message": "No hosts matched the selection",
        }

    if mock:
        result = nr.run(task=_mock_task, commands=commands, parser_name=parser_name)
    else:
        result = nr.run(task=_netmiko_task, commands=commands, parser_name=parser_name)

    return {
        "status": "completed",
        "device_count": len(nr.inventory.hosts),
        "results": _normalize_results(result),
    }
