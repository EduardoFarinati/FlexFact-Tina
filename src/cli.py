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
        parser.error(f"Invalid file path: {_str}")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Run a Tina Petri net in FlexFact.")

    def is_valid_device_config(_str: str) -> Path:
        return is_valid_file(parser, _str, ".dev")

    def is_valid_tina_network(_str: str) -> Path:
        return is_valid_file(parser, _str, ".net")

    parser.add_argument(
        "-d",
        "--device",
        type=is_valid_device_config,
        help="Path to a device config file",
        default=DEFAULT_DEVICE_PATH,
    )
    parser.add_argument(
        "-n",
        "--net",
        type=is_valid_tina_network,
        help="Path to a Petri net file",
        default=DEFAULT_NETWORK_PATH,
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=float,
        help="Time (in seconds) between loops",
        default=DEFAULT_SLEEP_S,
    )

    return parser


def parse_args() -> Tuple[Path, Path, float]:
    parser = build_parser()
    args = parser.parse_args()

    device_path = args.device
    network_path = args.net
    sleep_period = args.sleep

    return device_path, network_path, sleep_period
