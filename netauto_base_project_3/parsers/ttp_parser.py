from typing import Any

def parse(raw_output: str, platform: str, command: str) -> Any:
    return {
        "parser": "ttp",
        "platform": platform,
        "command": command,
        "tokens": raw_output.split()[:20],
    }
