from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import xml.etree.cElementTree as ET
from pymodbus.client import ModbusTcpClient as mbClient


class ModbusClient(mbClient):
    def __init__(
        self,
        host: str,
        port: int,
        unit_id: Optional[int] = None,
        #timeout: Optional[float] = None,
        debug: Optional[bool] = None,
    ):
        try:
            super().__init__(
                host=host,
                port=port,
                unit_id=unit_id,
                #timeout=timeout,
                debug=debug,
                auto_open=True,
            )
        except ValueError:
            print("Error with host or port params")

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
        self.close()


@dataclass
class InputEvent:
    triggers: List[Tuple[int, bool]] = field(default_factory=list)


@dataclass
class OutputEvent:
    actions: List[Tuple[int, bool]] = field(default_factory=list)


def parse_device(filepath: Union[Path, str]):
    """
    Parse config for virtual Modbus. The XML can be exported from
    (tina/flexfact)
    Returns (inputs, outputs)
    """
    inputs: Dict[str, InputEvent] = {}
    outputs: Dict[str, OutputEvent] = {}

    root = ET.parse(filepath).getroot()

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

                rising = element.tag == "PositiveEdge"  # Rising edge or not
                event.triggers.append((address, rising))
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

    return inputs, outputs
