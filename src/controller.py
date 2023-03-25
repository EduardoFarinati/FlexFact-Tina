import re
from typing import Dict, List, Tuple
from pymodbus.exceptions import ModbusException

from tina_utils import Transition
from modbus_utils import InputEvent, ModbusClient, OutputEvent
from special_tokens import strip_name, COMMENT


# Modbus port
PORT = 1502


def check_transition(rising: bool, ba_tup: Tuple[bool, bool]):
    """
    A convenience function just to check if two values of a signal
    represent a rising or falling transition.
    """
    return ba_tup[0] != ba_tup[1] == rising


class Controller:
    def __init__(
        self,
        transitions: List[Transition],
        places: Dict[str, int],
        inputs: Dict[str, InputEvent],
        outputs: Dict[str, OutputEvent],
    ):
        self.client = ModbusClient(host="localhost", port=PORT)
        self.transitions = transitions
        self.places = places
        self.inputs = inputs
        self.outputs = outputs

        print(f"Controlling plant at {PORT}, with:")
        print(f"  Transitions: {len(transitions)}")
        print(f"  Places: {len(places)}")
        print("")

        # Get all the addresses. These addresses appear more than once in the .net file
        # so use a set to avoid repeats
        self.addresses = set(
            [i[0] for value in self.inputs.values() for i in value.triggers]
        )

        # Intantiate the read values to false. This is needed because we use rising and falling
        # edges. While it would be possible to use the direct values, this misses the point because
        # tina is supposed to be for *event* oriented programming
        # This using a tuple because it stores the current and previous value
        self.read_values = {
            address: (False, False) for address in self.addresses
        }

    def read(self, event: str) -> bool:
        """
        Read the value of a signal from the bus. This isn't very useful in practice,
        I *think* because this would read an address multiple times if it appeared more than once
        It's probably faster to use the current system of reading all the values and
        acting based on that
        """
        result = False
        for trigger in self.inputs[event].triggers:
            try:
                readval = self.client.read_discrete_inputs(trigger[0])
                result = result or readval.bits[0]
            except ModbusException as e:
                raise ConnectionError("Can't read discrete input") from e

        return result

    def write(self, event: str):
        """
        Write an event to the bus to trigger eg. a belt
        """
        print(f"  e: {event}")
        for action in self.outputs[event].actions:
            try:
                self.client.write_coil(*action)
            except ModbusException as e:
                raise ConnectionError("Can't write to coils") from e

    def read_all(self):
        """
        Read the values from all available addresses and update [read_values]
        """
        for address in self.addresses:
            try:
                input_vals = self.client.read_discrete_inputs(address)
                self.read_values[address] = (
                    self.read_values[address][1],
                    input_vals.bits[0],
                )
            except ModbusException as e:
                raise ConnectionError("Can't read discrete inputs") from e

    def loop(self):
        """
        The main loop. I ran this every 10ms
        """

        # Update the read values
        self.read_all()

        # Iterate through all the transitions in a network
        for transition in self.transitions:
            is_enabled = True

            # Check if the token requirements to transition are met
            # (ie. if there is a token present at the correct location)
            for req in transition.reqs:
                if req[2] == False and self.places[req[0]] >= req[1]:
                    is_enabled = False
                elif req[2] != False and self.places[req[0]] < req[1]:
                    is_enabled = False

            # Check if the FlexFact requirements are met (ie. if a sensor has just turn on or off)
            # Adding ; to the start of a name means it is ignored and the transition is allowed
            if not transition.name.startswith(COMMENT):
                name = strip_name(transition.name)
                if name in self.inputs:
                    # There are technically multiple triggers defined
                    # This probably should be modified to work too, instead of using [0],
                    # but in my use it was never needed. I can't actually think when this
                    # would be used

                    # Should it be rising or falling to transition
                    rising = self.inputs[name].triggers[0][1]
                    address = self.inputs[name].triggers[0][0]

                    # Check if the signal is rising or falling, or vice-versa
                    did_transition = check_transition(
                        rising, self.read_values[address]
                    )
                else:
                    did_transition = True
            else:
                did_transition = True

            # If all requirements are met
            if is_enabled and did_transition:
                print(f"  t: {transition.name}")

                # Move the tokens around
                # This is a basic implementation of a Petri net runner
                for req in transition.reqs:
                    if req[2] == None:
                        self.places[req[0]] -= req[1]
                for out in transition.outs:
                    self.places[out[0]] += out[1]

                # Issue the commands via Modbus. Note that ; is also used to
                # separate between command in the name, so you can use less places
                # This hasn't been tested much
                if strip_name(transition.name) in self.outputs:
                    values = transition.name.split(COMMENT)
                    if values[0]:
                        for v in values:
                            self.write(strip_name(v))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.client.close()
