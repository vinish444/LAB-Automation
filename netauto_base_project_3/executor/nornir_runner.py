from __future__ import annotations
from typing import Any, Dict

from nornir import InitNornir
from nornir.core.filter import F

from app.core.config import settings
from executor.decision_engine import decide_execution
from executor.napalm_runner import napalm_task
from executor.netmiko_runner import netmiko_task


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

    final_results: Dict[str, Any] = {}

    for command in commands:
        exec_type, exec_value = decide_execution(command)

        if exec_type == "napalm":
            result = nr.run(task=napalm_task, method_name=exec_value, mock=mock)
        else:
            result = nr.run(task=netmiko_task, command=exec_value, parser_name=parser_name, mock=mock)

        for host, multi in result.items():
            host_payload = final_results.setdefault(host, {"failed": multi.failed, "commands": {}})
            for item in multi:
                host_payload["commands"][command] = item.result

    return {
        "status": "completed",
        "device_count": len(nr.inventory.hosts),
        "results": final_results,
    }
