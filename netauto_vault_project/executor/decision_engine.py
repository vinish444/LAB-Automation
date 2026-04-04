from typing import Tuple

NAPALM_SUPPORTED = {
    "get_facts": "get_facts",
    "get_interfaces": "get_interfaces",
    "get_bgp_neighbors": "get_bgp_neighbors",
}


def decide_execution(command: str) -> Tuple[str, str]:
    command = command.strip()
    if command in NAPALM_SUPPORTED:
        return "napalm", NAPALM_SUPPORTED[command]
    return "netmiko", command
