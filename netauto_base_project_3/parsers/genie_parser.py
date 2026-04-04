from typing import Any

def parse(raw_output: str, platform: str, command: str) -> Any:
    return {
        "parser": "genie",
        "platform": platform,
        "command": command,
        "note": "Base project placeholder. Replace with real pyATS/Genie parser later.",
        "raw_preview": raw_output[:200],
    }
