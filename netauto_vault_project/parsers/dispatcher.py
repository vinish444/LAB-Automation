from typing import Any, Optional

from parsers.genie_parser import parse as parse_genie
from parsers.raw_parser import parse as parse_raw
from parsers.selector import select_parser
from parsers.textfsm_parser import parse as parse_textfsm
from parsers.ttp_parser import parse as parse_ttp


def parse_output(
    raw_output: str,
    parser_name: str,
    platform: str,
    command: str,
    template_name: Optional[str] = None,
) -> Any:
    selection = select_parser(parser_name, platform, command)
    template_name = template_name or selection.template

    if selection.parser == "genie":
        return parse_genie(raw_output, platform, command)
    if selection.parser == "textfsm":
        return parse_textfsm(raw_output, platform, command, template_name)
    if selection.parser == "ttp":
        return parse_ttp(raw_output, platform, command, template_name)
    return parse_raw(raw_output, platform, command)
