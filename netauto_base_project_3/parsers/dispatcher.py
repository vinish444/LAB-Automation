from typing import Any
from parsers.genie_parser import parse as parse_genie
from parsers.raw_parser import parse as parse_raw
from parsers.textfsm_parser import parse as parse_textfsm
from parsers.ttp_parser import parse as parse_ttp


def parse_output(raw_output: str, parser_name: str, platform: str, command: str) -> Any:
    parser_name = (parser_name or "raw").lower()

    if parser_name == "genie":
        return parse_genie(raw_output, platform, command)
    if parser_name == "textfsm":
        return parse_textfsm(raw_output, platform, command)
    if parser_name == "ttp":
        return parse_ttp(raw_output, platform, command)
    if parser_name == "auto":
        if platform.startswith("cisco"):
            return parse_genie(raw_output, platform, command)
        if "show" in command.lower():
            return parse_textfsm(raw_output, platform, command)
        return parse_ttp(raw_output, platform, command)
    return parse_raw(raw_output, platform, command)
