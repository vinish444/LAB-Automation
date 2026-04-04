from typing import Any

def parse(raw_output: str, platform: str, command: str) -> Any:
    return {
        "parser": "textfsm",
        "platform": platform,
        "command": command,
        "records": [{"line_count": len(raw_output.splitlines())}],
        "raw_preview": raw_output[:200],
    }
