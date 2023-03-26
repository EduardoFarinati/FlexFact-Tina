#!/usr/bin/env python3
import time

from cli import parse_args
from tina_utils import parse_network
from modbus_utils import parse_device
from controller import Controller


RECONNECT_PERIOD_S = 1.5


def main():
    # Parse cli arguments
    device_path, network_path, sleep_period = parse_args()

    # Parse config
    transitions, places = parse_network(network_path)
    address, inputs, outputs = parse_device(device_path)

    # Start controller
    while True:
        try:
            with Controller(
                address, transitions, places, inputs, outputs
            ) as controller:
                print("Operation display:")
                while True:
                    controller.loop()
                    time.sleep(sleep_period)
        except ConnectionError as e:
            print(f"Connection reset, because: {e}.")
            print(f"Caused by: {e.__cause__}.")
            print(f"Trying to reconnect in {RECONNECT_PERIOD_S} seconds...")
            print("")
            time.sleep(RECONNECT_PERIOD_S)
        except KeyboardInterrupt:
            print("")
            print("Stopping controller...")
            break


if __name__ == "__main__":
    main()
