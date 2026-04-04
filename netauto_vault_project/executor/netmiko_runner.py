from nornir.core.task import Result, Task

from parsers.dispatcher import parse_output
from parsers.selector import template_hint

try:
    from nornir_netmiko.tasks import netmiko_send_command
except Exception:  # pragma: no cover
    netmiko_send_command = None


SAMPLE_OUTPUTS = {
    ("cisco_ios", "show ip interface brief"): """Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.0.0.1        YES NVRAM  up                    up
GigabitEthernet0/1     unassigned      YES unset  administratively down down
""",
    ("cisco_nxos", "show ip interface brief"): """IP Interface Status for VRF \"default\"(1)
Eth1/1        10.1.1.1        protocol-up/link-up/admin-up
Eth1/2        unassigned      protocol-down/link-down/admin-down
""",
    ("arista_eos", "show ip interface brief"): """Interface              IP Address         Status     Protocol MTU    Owner
Ethernet1              10.2.2.2           up         up       1500   network
Ethernet2              unassigned         down       down     1500   network
""",
    ("juniper_junos", "show interfaces terse"): """Interface               Admin Link Proto    Local                 Remote
ge-0/0/0                up    up
lo0                      up    up
lo0.0                    up    up   inet     10.10.10.1/32
""",
    ("cisco_ios", "show version"): "Cisco IOS XE Software, Version 17.09.01\n",
}


def _mock_output(platform: str, command: str, host_name: str) -> str:
    return SAMPLE_OUTPUTS.get((platform, command), f"MOCK CLI OUTPUT from {host_name}: {command}")


def netmiko_task(task: Task, command: str, parser_name: str, mock: bool = True) -> Result:
    platform = str(task.host.platform or "unknown")
    template_name = template_hint(platform, command)

    if mock:
        raw = _mock_output(platform, command, task.host.name)
        return Result(
            host=task.host,
            result={
                "raw": raw,
                "parsed": parse_output(raw, parser_name, platform, command, template_name),
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
            "parsed": parse_output(raw, parser_name, platform, command, template_name),
        },
    )
