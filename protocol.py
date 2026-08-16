from enum import Enum

class Command(Enum):
    READ = 0x01
    WRITE = 0x02
    PING = 0x03


class ProtFrame:
    magic = 0xA5

    def __init__(self, command : Command, value : int):
        self.command = command
        if self.command == Command.PING and value != 0:
            raise ValueError("...")
        self.value = value
        self.calculate_checksum()

    def calculate_checksum(self):
        byte_left = (self.value >> 8) & 0xFF
        byte_right = self.value & 0xFF
        self.checksum = (self.magic + self.command.value  + byte_left + byte_right) % 256


    def to_bytes(self) -> bytes:
        magic_b = bytes([self.magic])
        command_b = bytes([self.command.value])
        value_b = self.value.to_bytes(2, byteorder="big")
        checksum_b = bytes([self.checksum])
        return magic_b + command_b + value_b + checksum_b