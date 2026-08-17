from enum import Enum
from protocol import Command


class ProtocolError(Exception):
    pass


class InvalidLengthError(ProtocolError):
    pass


class InvalidSOFError(ProtocolError):
    pass


class ChecksumMismatchError(ProtocolError):
    pass


class UnknownCommandError(ProtocolError):
    pass


class FakeDeviceStatus(Enum):
    SUCCESS = 0


class FakeDevice:

    def receive_frame(self, b: bytes) -> FakeDeviceStatus:
        self._check_length(b)
        self._check_sof(b)
        self._check_checksum(b)
        self._check_command(b)

        return FakeDeviceStatus.SUCCESS

    def _check_length(self, b: bytes) -> bool:
        if len(b) != 5:
            raise InvalidLengthError(f"Expected 5 bytes, got {len(b)}")
        return True

    def _check_sof(self, b: bytes) -> bool:
        if b[0] != 0xA5:
            raise InvalidSOFError(f"Expected SOF 0xA5, got {hex(b[0])}")
        return True

    def _check_checksum(self, b: bytes) -> bool:
        calculated_checksum = sum(b[:4]) % 256
        if calculated_checksum != b[4]:
            raise ChecksumMismatchError(
                f"Expected CS {hex(calculated_checksum)}, got {hex(b[4])}"
            )
        return True

    def _check_command(self, b: bytes) -> bool:
        valid_commands = [c.value for c in Command]
        if b[1] not in valid_commands:
            raise UnknownCommandError(f"Unknown command byte: {hex(b[1])}")
        return True