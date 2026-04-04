from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import textfsm

from app.core.config import settings


CUSTOM_TEMPLATE_DIR = Path("templates/textfsm/custom")


def _resolve_template_path(template_name: Optional[str]) -> Optional[Path]:
    if not template_name:
        return None

    direct = Path(template_name)
    if direct.exists():
        return direct

    custom = CUSTOM_TEMPLATE_DIR / template_name
    if custom.exists():
        return custom

    ntc_base = os.getenv("NET_TEXTFSM") or settings.net_textfsm
    if ntc_base:
        ntc_path = Path(ntc_base) / template_name
        if ntc_path.exists():
            return ntc_path
    return None


def parse(raw_output: str, platform: str, command: str, template_name: Optional[str] = None) -> Any:
    template_path = _resolve_template_path(template_name)
    if not template_path:
        return {
            "parser": "textfsm",
            "platform": platform,
            "command": command,
            "template": template_name,
            "status": "template_not_found",
            "raw_preview": raw_output[:200],
        }

    with open(template_path, "r", encoding="utf-8") as handle:
        fsm = textfsm.TextFSM(handle)
        rows = fsm.ParseText(raw_output)

    records = [dict(zip(fsm.header, row)) for row in rows]
    return {
        "parser": "textfsm",
        "platform": platform,
        "command": command,
        "template": str(template_path),
        "records": records,
    }
