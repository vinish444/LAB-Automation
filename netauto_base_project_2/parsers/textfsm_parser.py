def parse_textfsm_output(output: str, platform: str = "unknown", command: str = ""):
    # Base project placeholder. Replace with real ntc-templates lookup later.
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return {
        "parser": "textfsm",
        "platform": platform,
        "command": command,
        "line_count": len(lines),
        "lines": lines,
    }
