from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.config import settings
from app.utils.yaml_loader import load_yaml_file


@dataclass
class ParserSelection:
    parser: str
    template: Optional[str] = None


def resolve_command(intent_or_command: str, platform: str) -> str:
    command_map = load_yaml_file(settings.command_map_file)
    intents = command_map.get("intents", {})
    if intent_or_command in intents:
        return intents[intent_or_command].get(platform, intent_or_command)
    return intent_or_command


def select_parser(parser_name: str, platform: str, command: str) -> ParserSelection:
    parser_name = (parser_name or "raw").lower()
    if parser_name != "auto":
        return ParserSelection(parser=parser_name)

    parser_map = load_yaml_file(settings.parser_map_file)
    platform_map = (parser_map.get("platforms") or {}).get(platform, {})
    command_map = platform_map.get(command, {})
    if command_map:
        return ParserSelection(
            parser=command_map.get("parser", "raw"),
            template=command_map.get("template"),
        )

    fallback = (parser_map.get("defaults") or {}).get("fallback_parser", "raw")
    return ParserSelection(parser=fallback)


def template_hint(platform: str, command: str) -> Optional[str]:
    parser_map = load_yaml_file(settings.parser_map_file)
    platform_map = (parser_map.get("platforms") or {}).get(platform, {})
    entry = platform_map.get(command, {})
    return entry.get("template")
