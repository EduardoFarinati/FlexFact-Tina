from pyModbusTCP.client import ModbusClient
import xml.etree.cElementTree as ET
import time


class Transition:
    def __init__(self, name):
        self.name = name
        self.reqs = []
        self.outs = []


def parseTina(filename):
    transitions = []
    places = {}
    with open(filename, 'r') as file:
        for line in file:
            elements = line.strip().replace('\n', '').replace(
                '\r', '').replace('{', '').replace('}', '').split()
            if len(elements) == 0:
                continue
            elif elements[0] == 'tr':
                transition = Transition(elements[1])
                arrow_index = elements.index('->')
                for element in elements[3:arrow_index]:
                    if ('?' in element):
                        parts = element.split('?')
                        if (int(parts[1]) > 0):
                            transition.reqs.append(
                                (parts[0], int(parts[1]), True))
                        else:
                            transition.reqs.append(
                                (parts[0], abs(int(parts[1])), False))
                    else:
                        parts = element.split('*')
                        if (len(parts) == 1):
                            transition.reqs.append((parts[0], 1, None))
                        else:
                            transition.reqs.append(
                                (parts[0], int(parts[1]), None))
                if arrow_index + 1 != len(elements):
                    for element in elements[arrow_index+1:]:
                        parts = element.split('*')
                        places[parts[0]] = 0
                        if (len(parts) == 1):
                            transition.outs.append((parts[0], 1))
                        else:
                            transition.outs.append((parts[0], int(parts[1])))

                transitions.append(transition)

            elif elements[0] == 'pl':
                places[elements[1]] = int(
                    elements[2].replace('(', '').replace(')', ''))

    return transitions, places


transitions, places = parseTina('..\\Trab 2\\TrabSEDvFinal.net')


def parseXMLConfig(filename):
    events = {}
    events['inputs'] = {}
    events['outputs'] = {}

    root = ET.parse(filename).getroot()
    for tag in root.findall('EventConfiguration/Event'):
        event = {}
        name = tag.get('name')

        if tag.get('iotype') == 'input':
            event['triggers'] = []
            raw_triggers = [trigger for trigger in tag.find(
                'Triggers').iter() if trigger is not tag.find('Triggers')]
            for element in raw_triggers:
                address = int(element.get('address'))
                rising = element.tag == 'PositiveEdge'  # Rising edge or not
                event['triggers'].append((address, rising))
            events['inputs'][name] = event
        else:
            event['actions'] = []
            raw_actions = [action for action in tag.find(
                'Actions').iter() if action is not tag.find('Actions')]
            for element in raw_actions:
                address = int(element.get('address'))
                value = element.tag == 'Set'  # Otherwise it's clr so it should be false
                event['actions'].append((address, value))
            events['outputs'][name] = event

    return events


events = parseXMLConfig('config.dev')

try:
    c = ModbusClient(host="localhost", port=1502, auto_open=True)
except ValueError:
    print("Error with host or port params")

# This probably isn't much use


def read(event):
    result = False
    for trigger in events['inputs'][event]['triggers']:
        readval = c.read_discrete_inputs(trigger[0])
        result = result or readval[0]

    return result


def write(event):
    print(event)
    for action in events['outputs'][event]['actions']:
        c.write_single_coil(*action)


# write('sf_fdon')
# write('cb1_bm+')
# write('cb2_bm+')
# write('cb3_bm+')

addresses = set()
for key, value in events['inputs'].items():
    for i in value['triggers']:
        addresses.add(i[0])

read_values = {}
for address in addresses:
    read_values[address] = (False, False)


def readAll():
    for address in addresses:
        read_values[address] = (read_values[address][1],
                                c.read_discrete_inputs(address)[0])


def checkTransition(rising, ba_tup):
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
            if name in events['inputs'].keys():
                rising = events['inputs'][name]['triggers'][0][1]
                address = events['inputs'][name]['triggers'][0][0]
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

            if transition.name.replace('X', '') in events['outputs']:
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

c.close()
