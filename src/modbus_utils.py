from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path
import xml.etree.cElementTree as ET
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusSocketFramer


# Default modbus connection
DEFAULT_IP = "localhost"
DEFAULT_PORT = 1502


class ModbusClient(ModbusTcpClient):
    def __init__(
        self,
        address: Tuple[str, int] = (DEFAULT_IP, DEFAULT_PORT),
    ):
        ip, port = address

        super().__init__(
            host=ip,
            port=port,
            framer=ModbusSocketFramer,  # type: ignore
            retry_on_empty=True,
            close_on_comm_error=False,
            timeout=1,
            retries=3,
        )

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


def parse_device(
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

    return (slave_ip, slave_port), inputs, outputs
