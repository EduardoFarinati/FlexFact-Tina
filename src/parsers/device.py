from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Tuple, Union
import xml.etree.cElementTree as ET


class TriggerTypes(Enum):
    POSITIVE_EDGE = auto()
    NEGATIVE_EDGE = auto()


@dataclass
class Trigger:
    address: int
    type: TriggerTypes

    def check(self, previous: bool, now: bool) -> bool:
        """A convenience function just to check if two values of a signal
        represent transition (event).
        """
        if self.type == TriggerTypes.POSITIVE_EDGE:
            return previous != now and now
        elif self.type == TriggerTypes.NEGATIVE_EDGE:
            return previous != now and not now

        raise ValueError(f"Invalid trigger type: {self.type}")


@dataclass
class InputEvent:
    triggers: List[Trigger] = field(default_factory=list)


@dataclass
class OutputEvent:
    actions: List[Tuple[int, bool]] = field(default_factory=list)


def parse(
    filepath: Union[Path, str]
) -> Tuple[Tuple[str, int], Dict[str, InputEvent], Dict[str, OutputEvent]]:
    """
    Parse config for virtual Modbus XML. It should be exported from flexfact.
    Returns (inputs, outputs)
    """
    inputs = {}
    outputs = {}

    root = ET.parse(filepath).getroot()

    # Parse slave address
    slave_address_tag = root.find("SlaveAddress")
    assert slave_address_tag is not None, "Expected SlaveAddress in XML"
    slave_address = slave_address_tag.get("value")
    assert slave_address is not None, "Expected SlaveAddress value in XML"
    slave_ip, slave_port_str = slave_address.split(":", 1)
    slave_port = int(slave_port_str)

    # Parse events
    for tag in root.findall("EventConfiguration/Event"):
        event = {}
        name = tag.get("name")
        assert name is not None, "Expected name in XML"

        if tag.get("iotype") == "input":
            event = InputEvent()
            raw_triggers = tag.find("Triggers")
            assert raw_triggers is not None, "Expected Triggers in XML"
            triggers = [
                trigger
                for trigger in raw_triggers.iter()
                if trigger is not tag.find("Triggers")
            ]
            for element in triggers:
                raw_address = element.get("address")
                assert raw_address is not None, "Expected address in XML"

                address = int(raw_address)

                if element.tag == "PositiveEdge":
                    event.triggers.append(
                        Trigger(address, TriggerTypes.POSITIVE_EDGE)
                    )
                elif element.tag == "NegativeEdge":
                    event.triggers.append(
                        Trigger(address, TriggerTypes.NEGATIVE_EDGE)
                    )
                else:
                    raise AssertionError(
                        "Expected positive or negative edge as triggers"
                    )
            inputs[name] = event
        else:
            event = OutputEvent()
            raw_actions = tag.find("Actions")
            assert raw_actions is not None, "Expected Actions in XML"
            actions = [
                action
                for action in raw_actions.iter()
                if action is not tag.find("Actions")
            ]
            for element in actions:
                raw_address = element.get("address")
                assert raw_address is not None, "Expected address in XML"
                address = int(raw_address)

                value = (
                    element.tag == "Set"
                )  # Otherwise it's clr so it should be false
                event.actions.append((address, value))
            outputs[name] = event

    return (slave_ip, slave_port), inputs, outputs
