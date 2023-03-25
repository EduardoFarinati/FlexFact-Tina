import time

from cli import parse_args
from tina_utils import parse_network
from modbus_utils import parse_device
from controller import Controller


def main():
    # Parse cli arguments
    device_path, network_path, period = parse_args()

    # Parse config
    transitions, places = parse_network(network_path)
    inputs, outputs = parse_device(device_path)

    with Controller(transitions, places, inputs, outputs) as controller:
        print("Operation display:")

        try:
            while True:
                controller.loop()
                time.sleep(period)
        except ConnectionError as e:
            print("")
            print(f"Connection closed, because: {e}.")
            print(f"Caused by: {e.__cause__}")
        except KeyboardInterrupt:
            pass

        print("")
        print("Stopping controller...")


if __name__ == "__main__":
    main()
