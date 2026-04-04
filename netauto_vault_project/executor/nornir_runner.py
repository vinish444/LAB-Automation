from __future__ import annotations

from typing import Any, Dict

from nornir import InitNornir
from nornir.core.filter import F

from app.core.config import settings
from app.core.vault_client import VaultError, vault_manager
from executor.decision_engine import decide_execution
from executor.napalm_runner import napalm_task
from executor.netmiko_runner import netmiko_task
from parsers.selector import resolve_command


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


def _inject_vault_credentials(nr: Any) -> Dict[str, str]:
    resolved = {}
    for host in nr.inventory.hosts.values():
        platform = str(host.platform or "unknown")
        cred = vault_manager.read_credentials(platform)
        host.username = cred.username
        host.password = cred.password
        resolved[host.name] = cred.source_path
    return resolved


def execute_commands(payload: Dict[str, Any]) -> Dict[str, Any]:
    commands = payload.get("commands") or []
    parser_name = payload.get("parser", "auto")
    mock = payload.get("mock", True)
    use_vault = payload.get("use_vault", True)

    nr = _build_nr()
    nr = _apply_filters(nr, payload)

    if not nr.inventory.hosts:
        return {
            "status": "completed",
            "device_count": 0,
            "results": {},
            "message": "No hosts matched the selection",
        }

    vault_resolution = {}
    if use_vault and not mock:
        try:
            vault_resolution = _inject_vault_credentials(nr)
        except VaultError as exc:
            return {
                "status": "failed",
                "device_count": len(nr.inventory.hosts),
                "results": {},
                "message": f"Vault credential resolution failed: {exc}",
            }

    final_results: Dict[str, Any] = {}

    for command in commands:
        for host_name, host_obj in nr.inventory.hosts.items():
            platform = str(host_obj.platform or "unknown")
            resolved_command = resolve_command(command, platform)
            exec_type, exec_value = decide_execution(resolved_command)

            single_host_nr = nr.filter(name=host_name)
            if exec_type == "napalm":
                result = single_host_nr.run(task=napalm_task, method_name=exec_value, mock=mock)
            else:
                result = single_host_nr.run(task=netmiko_task, command=exec_value, parser_name=parser_name, mock=mock)

            multi = result[host_name]
            host_payload = final_results.setdefault(
                host_name,
                {
                    "failed": multi.failed,
                    "platform": platform,
                    "vault_secret_path": vault_resolution.get(host_name),
                    "commands": {},
                },
            )
            for item in multi:
                host_payload["commands"][command] = {
                    "resolved_command": resolved_command,
                    "result": item.result,
                }

    return {
        "status": "completed",
        "device_count": len(nr.inventory.hosts),
        "results": final_results,
    }
