from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ttp import ttp


TTP_TEMPLATE_DIR = Path("templates/ttp")


def _resolve_template_path(template_name: Optional[str]) -> Optional[Path]:
    if not template_name:
        return None
    direct = Path(template_name)
    if direct.exists():
        return direct
    candidate = TTP_TEMPLATE_DIR / template_name
    if candidate.exists():
        return candidate
    return None


def parse(raw_output: str, platform: str, command: str, template_name: Optional[str] = None) -> Any:
    template_path = _resolve_template_path(template_name)
    if not template_path:
        return {
            "parser": "ttp",
            "platform": platform,
            "command": command,
            "template": template_name,
            "status": "template_not_found",
            "raw_preview": raw_output[:200],
        }

    parser = ttp(data=raw_output, template=template_path.read_text(encoding="utf-8"))
    parser.parse()
    result = parser.result(format="json")[0]
    return {
        "parser": "ttp",
        "platform": platform,
        "command": command,
        "template": str(template_path),
        "records": result,
    }
