# %% Imports
from typing import Dict, Set, Tuple
import time

from tina_utils import parseTina
from modbus_utils import ModbusClient, parseXMLConfig
# from controller import parseXMLConfig

# %% Parse config
transitions, places = parseTina('..\\Trab 2\\TrabSEDvFinal.net')

inputs, outputs = parseXMLConfig('config.dev')
# print(outputs)

# %% Control system

with ModbusClient(host="localhost", port=1502) as c:
    def read(event: str) -> bool:
        result = False
        for trigger in inputs[event].triggers:
            assert (readval := c.read_discrete_inputs(
                trigger[0])) is not None, "Can't read discrete inputs"
            result = result or readval[0]

        return result

    def write(event: str):
        print(event)
        for action in outputs[event].actions:
            c.write_single_coil(*action)

    # write('sf_fdon')
    # write('cb1_bm+')
    # write('cb2_bm+')
    # write('cb3_bm+')

    addresses: Set[int] = set()
    for key, value in inputs.items():
        for i in value.triggers:
            addresses.add(i[0])

    read_values: Dict[int, Tuple[bool, bool]] = {}
    for address in addresses:
        read_values[address] = (False, False)

    def readAll():
        for address in addresses:
            assert (input_vals := c.read_discrete_inputs(address)
                    ) is not None, "Can't read discrete inputs"
            read_values[address] = (read_values[address][1],
                                    input_vals[0])

    def checkTransition(rising: bool, ba_tup: Tuple[bool, bool]):
        if rising:
            return ba_tup[0] == False and ba_tup[1] == True
        else:
            return ba_tup[0] == True and ba_tup[1] == False

    def loop():
        readAll()
        for transition in transitions:
            can_move = True
            for req in transition.reqs:
                if req[2] == False and places[req[0]] >= req[1]:
                    can_move = False
                elif req[2] != False and places[req[0]] < req[1]:
                    can_move = False

            if transition.name[0] != 'Z':
                name = transition.name.replace('X', '')
                # there are technically multiple triggers defined. I don't care
                if name in inputs.keys():
                    rising = inputs[name].triggers[0][1]
                    address = inputs[name].triggers[0][0]
                    can_trans = checkTransition(rising, read_values[address])
                else:
                    can_trans = True
            else:
                can_trans = True

            if can_move and can_trans:
                print(transition.name)
                # print(transition.name.replace('Z', '').replace('X', ''))
                # print(transition.reqs)
                # for req in transition.reqs:
                #     print(places[req[0]])
                for req in transition.reqs:
                    if req[2] == None:
                        places[req[0]] -= req[1]
                for out in transition.outs:
                    places[out[0]] += out[1]

                if transition.name.replace('X', '') in outputs:
                    values = transition.name.split('Z')
                    for v in values:
                        write(v.replace('X', ''))

        # for key, value in places.items():
        #     if key[0] != 'Z':
        #         values = key.split('Z')
        #         if value > 0:
        #             for v in values:
        #                 write(v.replace('X', ''))

        # print(places)

    while True:
        loop()
        time.sleep(0.01)
