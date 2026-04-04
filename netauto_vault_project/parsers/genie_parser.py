from typing import Any


def parse(raw_output: str, platform: str, command: str) -> Any:
    return {
        "parser": "genie",
        "platform": platform,
        "command": command,
        "note": "Genie integration point. Install pyATS/Genie in a dedicated image if you want real Cisco parser execution.",
        "raw_preview": raw_output[:200],
    }
