from enum import Enum


class Command(Enum):
    READ = 0x01
    WRITE = 0x02
    PING = 0x03


class ProtFrame:
    """Represents a MiniFuzz protocol frame.

    Attributes:
        command (Command): 1-byte command inserted into a frame (READ, WRITE, or PING).
        value (int): Value related to the command type (0-65535). For READ, it specifies
            the register address; for WRITE, the payload value; for PING, it must be 0.
        checksum (int): Calculated 1-byte modulo-256 checksum of the frame.
    """

    magic = 0xA5

    def __init__(self, command: Command, value: int):
        self.command = command
        if self.command == Command.PING and value != 0:
            raise ValueError("Field 'value' should be 0 for the PING frame")
        if not (0 <= value <= 65535):
            raise ValueError("Field 'value' should be in range 0-65535")
        self.value = value
        self.calculate_checksum()

    def calculate_checksum(self) -> None:
        """Calculates the checksum according to the protocol specification.

        Computes a 1-byte checksum by summing MAGIC, command byte,
        and both bytes of the value field modulo 256.
        """
        byte_left = (self.value >> 8) & 0xFF
        byte_right = self.value & 0xFF
        self.checksum = (
            self.magic + self.command.value + byte_left + byte_right
        ) % 256

    def to_bytes(self) -> bytes:
        """Converts the frame object into its raw byte representation.

        Returns:
            bytes: A 5-byte sequence representing [MAGIC, CMD, VALUE_HI, VALUE_LO, CHECKSUM].
        """
        magic_b = bytes([self.magic])
        command_b = bytes([self.command.value])
        value_b = self.value.to_bytes(2, byteorder="big")
        checksum_b = bytes([self.checksum])
        return magic_b + command_b + value_b + checksum_b