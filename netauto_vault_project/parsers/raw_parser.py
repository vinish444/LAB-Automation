from typing import Any

def parse(raw_output: str, platform: str, command: str) -> Any:
    return {"platform": platform, "command": command, "output": raw_output}
