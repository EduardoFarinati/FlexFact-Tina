# %% Imports
from typing import Dict, Set, Tuple
import time

from tina_utils import parseTina
from modbus_utils import ModbusClient, parseXMLConfig
import re
import argparse
from pathlib import Path

device_path = 'config.dev'
tina_path = 'example.net'
period = 0.01

# %% Parse command line args


def checkFilepath(string: str) -> str:
    if Path(string).is_file():
        return string
    else:
        raise Exception(f"This isn't a valid file: {string}")


parser = argparse.ArgumentParser(
    description='Run a Tina Petri net in FlexFact.')
parser.add_argument('-d', '--device', type=checkFilepath,
                    help='path to a device config file', default=device_path)
parser.add_argument('-n', '--net', type=checkFilepath,
                    help='path to a Petri net file', default=tina_path)
parser.add_argument('-p', '--period', type=float,
                    help='Time (in seconds) between loops', default=period)

args = parser.parse_args()
device_path = args.device
tina_path = args.net
period = args.period

# %% Parse config
device_path = Path(device_path)
tina_path = Path(tina_path)

transitions, places = parseTina(tina_path)

inputs, outputs = parseXMLConfig(device_path)
# print(outputs)

# %% Control system

with ModbusClient(host="localhost", port=1502) as c:
    def read(event: str) -> bool:
        """
        Read the value of a signal from the bus. This isn't very useful in practice,
        I *think* because this would read an address multiple times if it appeared more than once
        It's probably faster to use the current system of reading all the values and
        acting based on that
        """
        result = False
        for trigger in inputs[event].triggers:
            readval = c.read_discrete_inputs(
                trigger[0])
            assert readval is not None, "Can't read discrete inputs"
            result = result or readval[0]

        return result

    def write(event: str):
        """
        Write an event to the bus to trigger eg. a belt
        """
        print(event)
        for action in outputs[event].actions:
            c.write_single_coil(*action)

    # Get all the addresses. These addresses appear more than once in the .net file
    # so use a set to avoid repeats
    addresses: Set[int] = set()
    for key, value in inputs.items():
        for i in value.triggers:
            addresses.add(i[0])

    # Intantiate the read values to false. This is needed because we use rising and falling
    # edges. While it would be possible to use the direct values, this misses the point because
    # tina is supposed to be for *event* oriented programming
    # This using a tuple because it stores the current and previous value
    read_values: Dict[int, Tuple[bool, bool]] = {
        ad: (False, False) for ad in addresses}

    def readAll():
        """
        Read the values from all available addresses and update [read_values]
        """
        for address in addresses:
            input_vals = c.read_discrete_inputs(address)
            assert input_vals is not None, "Can't read discrete inputs"
            read_values[address] = (read_values[address][1],
                                    input_vals[0])

    def checkTransition(rising: bool, ba_tup: Tuple[bool, bool]):
        """
        A convenience function just to check if two values are rising or falling
        """
        if rising:
            return ba_tup[0] == False and ba_tup[1] == True
        else:
            return ba_tup[0] == True and ba_tup[1] == False

    def loop():
        """
        The main loop. I ran this every 10ms
        """
        # Remove everything after X in a given name
        dup_re = re.compile(r'X.*')

        # Update the read values
        readAll()

        # Iterate through all the transitions in a network
        for transition in transitions:
            can_move = True

            # Check if the token requirements to transition are met
            # (ie. if there is a token present at the correct location)
            for req in transition.reqs:
                if req[2] == False and places[req[0]] >= req[1]:
                    can_move = False
                elif req[2] != False and places[req[0]] < req[1]:
                    can_move = False

            # Check if the FlexFact requirements are met (ie. if a sensor has just turn on or off)
            # Adding ; to the start of a name means it is ignored and the transition is allowed
            if transition.name[0] != ';':
                name = dup_re.sub('', transition.name)
                if name in inputs.keys():
                    # There are technically multiple triggers defined
                    # This probably should be modified to work too, instead of using [0],
                    # but in my use it was never needed. I can't actually think when this
                    # would be used

                    # Should it be rising or falling to transition
                    rising = inputs[name].triggers[0][1]
                    address = inputs[name].triggers[0][0]

                    # Is it rising or falling, or vice-versa
                    can_trans = checkTransition(rising, read_values[address])
                else:
                    can_trans = True
            else:
                can_trans = True

            # If all requirements are met
            if can_move and can_trans:
                print(transition.name)

                # Move the tokens around
                # This is a basic implementation of a Petri net runner
                for req in transition.reqs:
                    if req[2] == None:
                        places[req[0]] -= req[1]
                for out in transition.outs:
                    places[out[0]] += out[1]

                # Issue the commands via Modbus. Note that ; is also used to
                # separate between command in the name, so you can use less places
                # This hasn't been tested much
                if dup_re.sub('', transition.name) in outputs:
                    values = transition.name.split(';')
                    if values[0] != '':
                        for v in values:
                            write(dup_re.sub('', v))

    while True:
        try:
            loop()
            time.sleep(period)
        except KeyboardInterrupt:
            print('Stopping controller')
            break
