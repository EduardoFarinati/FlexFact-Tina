from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple


DEFAULT_DEVICE_PATH = "config.dev"
DEFAULT_NETWORK_PATH = "example.net"
DEFAULT_SLEEP_S = 0.01


def checkFilepath(string: str) -> str:
    if Path(string).is_file():
        return string
    else:
        raise Exception(f"This isn't a valid file: {string}")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Run a Tina Petri net in FlexFact.")

    parser.add_argument(
        "-d",
        "--device",
        type=checkFilepath,
        help="Path to a device config file",
        default=DEFAULT_DEVICE_PATH,
    )
    parser.add_argument(
        "-n",
        "--net",
        type=checkFilepath,
        help="Path to a Petri net file",
        default=DEFAULT_NETWORK_PATH,
    )
    parser.add_argument(
        "-p",
        "--period",
        type=float,
        help="Time (in seconds) between loops",
        default=DEFAULT_SLEEP_S,
    )

    return parser


def parse_args() -> Tuple[Path, Path, float]:
    parser = build_parser()
    args = parser.parse_args()

    device_path = Path(args.device)
    network_path = Path(args.net)
    period = args.period

    return device_path, network_path, period
