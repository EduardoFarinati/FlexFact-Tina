#!/usr/bin/env python3
import time
from typing import Dict, List, Tuple

from cli import parse_args
from tina_utils import Transition, parse_network
from modbus_utils import parse_device
from controller import Controller


RECONNECT_PERIOD_S = 1.5


def header_message(
    address: Tuple[str, int],
    transitions: List[Transition],
    places: Dict[str, int],
):
    print(f"Controlling FlexFact plant at {address}, with:")
    print(f"  Transitions: {len(transitions)}")
    print(f"  Places: {len(places)}")
    print("")


def connection_reset_message(e: ConnectionResetError):
    print(f"Connection reset, because: {e}.")
    print(f"Caused by: {e.__cause__}.")
    print(f"Trying to reconnect in {RECONNECT_PERIOD_S} seconds...")
    print("")
    time.sleep(RECONNECT_PERIOD_S)


def closing_message():
    print("")
    print("Stopping controller...")


def main():
    # Parse cli arguments
    device_path, network_path, sleep_period = parse_args()

    # Parse config
    transitions, places = parse_network(network_path)
    address, inputs, outputs = parse_device(device_path)

    # Start controller
    while True:
        header_message(address, transitions, places)
        try:
            with Controller(
                address, transitions, places, inputs, outputs
            ) as controller:
                print("Operation display:")
                while True:
                    controller.loop()
                    time.sleep(sleep_period)
        except ConnectionResetError as e:
            connection_reset_message(e)
        except KeyboardInterrupt:
            closing_message()
            break


if __name__ == "__main__":
    main()
