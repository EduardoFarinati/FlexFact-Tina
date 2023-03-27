#!/usr/bin/env python3
import time
from typing import Tuple

import cli
from parsers import network, device
from controller import Controller
from petri_net import PetriNet


RECONNECT_PERIOD_S = 1.5


def header_message(address: Tuple[str, int], petri_network: PetriNet):
    print(f"Controlling FlexFact plant at {address}, with:")
    print(f"  Transitions: {len(petri_network.transitions)}")
    print(f"  Places: {len(petri_network.places)}")
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
    # Parse CLI arguments
    device_path, network_path, sleep_period = cli.get_args()

    # Parse config
    petri_network = network.parse(network_path)
    address, inputs, outputs = device.parse(device_path)

    # Start controller
    while True:
        header_message(address, petri_network)
        try:
            with Controller(
                address, petri_network, inputs, outputs
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
