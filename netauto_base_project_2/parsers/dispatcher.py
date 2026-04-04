from typing import Any

from parsers.raw_parser import parse_raw
from parsers.textfsm_parser import parse_textfsm_output


def parse_output(output: str, parser_name: str, platform: str = "unknown", command: str = "") -> Any:
    parser_name = (parser_name or "raw").lower()
    if parser_name == "textfsm":
        return parse_textfsm_output(output, platform=platform, command=command)
    return parse_raw(output)
