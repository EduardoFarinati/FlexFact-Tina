from typing import Tuple
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

        # Try to connect
        if not self.connect():
            raise ConnectionAbortedError(
                "Unable to connect to modbus socket, is FlexFact open? "
                "Is Modbus selected on the Simulation menu?"
            )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

