from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple


DEFAULT_DEVICE_PATH = "./example/example.dev"
DEFAULT_NETWORK_PATH = "./example/example.net"
DEFAULT_SLEEP_S = 0.01


def is_valid_file(
    parser: ArgumentParser, _str: str, expected_suffix: str
) -> Path:
    path = Path(_str)
    if path.is_file() and path.suffix == expected_suffix:
        return path
    else:
        parser.error(
            f"Invalid path '{_str}', should be a file path such as"
            f" 'your_file{expected_suffix}'"
        )


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="flexfact_tina",
        description="A CLI tool to interface a Tina Petri net with FlexFact.",
    )

    parser.add_argument(
        "-d",
        "--device",
        type=lambda _str: is_valid_file(parser, _str, ".dev"),
        help="path to a device config file",
        default=DEFAULT_DEVICE_PATH,
    )
    parser.add_argument(
        "-n",
        "--net",
        type=lambda _str: is_valid_file(parser, _str, ".net"),
        help="path to a Petri net file",
        default=DEFAULT_NETWORK_PATH,
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=float,
        help="time (in seconds) between FlexFact calls",
        default=DEFAULT_SLEEP_S,
    )

    return parser


def get_args() -> Tuple[Path, Path, float]:
    parser = build_parser()
    args = parser.parse_args()

    device_path = args.device
    network_path = args.net
    sleep_period = args.sleep

    return device_path, network_path, sleep_period
