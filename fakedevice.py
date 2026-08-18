import random
from typing import Any
from protocol import Command

class ProtocolError(Exception):
    """Base exception class for all protocol validation errors."""


class InvalidLengthError(ProtocolError):
    """Raised when the frame length does not equal the expected 5 bytes."""


class InvalidSOFError(ProtocolError):
    """Raised when the Start of Frame (SOF) byte is invalid (expected 0xA5)."""


class ChecksumMismatchError(ProtocolError):
    """Raised when the frame checksum does not match the computed checksum."""


class UnknownCommandError(ProtocolError):
    """Raised when the frame contains an unrecognized command byte."""

class FakeDevice:
    """Simulates a device processing incoming protocol frames and returning status responses."""

    def receive_frame(self, b: bytes) -> dict[str, Any]:
        """Simulates the reception and execution of a raw protocol frame.

        Validates the frame structure, verifies the checksum, and executes
        the corresponding command (PING, READ, or WRITE).

        Args:
            b (bytes): The raw 5-byte protocol frame.

        Returns:
            dict[str, Any]: A dictionary containing the execution status and response data.

        Raises:
            InvalidLengthError: If the frame is not exactly 5 bytes.
            InvalidSOFError: If the first byte is not 0xA5.
            ChecksumMismatchError: If the calculated checksum does not match byte 4.
            UnknownCommandError: If the command byte is not a valid Command enum.
        """
        self._check_length(b)
        self._check_sof(b)
        self._check_checksum(b)
        self._check_command(b)

        cmd = Command(b[1])

        if cmd == Command.PING:
            return {"status": "SUCCESS", "Response": "PONG"}

        if cmd == Command.READ:
            read_data = random.randint(0, 255)
            return {"status": "SUCCESS", "Read value": read_data}

        if cmd == Command.WRITE:
            value = int.from_bytes(b[2:4], byteorder="big")
            return {
                "status": "SUCCESS",
                "action": f"ACK: Stored value {value}",
            }

        raise UnknownCommandError(f"Unhandled command: {cmd}")

    def _check_length(self, b: bytes) -> bool:
        """Validates that the frame length is exactly 5 bytes."""
        if len(b) != 5:
            raise InvalidLengthError(f"Expected 5 bytes, got {len(b)}")
        return True

    def _check_sof(self, b: bytes) -> bool:
        """Validates the Start of Frame (SOF) magic byte (0xA5)."""
        if not b or b[0] != 0xA5:
            raise InvalidSOFError(
                f"Expected SOF 0xA5, got {hex(b[0]) if b else 'empty'}"
            )
        return True

    def _check_checksum(self, b: bytes) -> bool:
        """Validates the frame checksum (sum of first 4 bytes modulo 256)."""
        calculated_checksum = sum(b[:4]) % 256
        if calculated_checksum != b[4]:
            raise ChecksumMismatchError(
                f"Expected checksum {hex(calculated_checksum)}, got {hex(b[4])}"
            )
        return True

    def _check_command(self, b: bytes) -> bool:
        """Validates if the command byte corresponds to a known Command enum value."""
        valid_commands = [c.value for c in Command]
        if b[1] not in valid_commands:
            raise UnknownCommandError(f"Unknown command byte: {hex(b[1])}")
        return True