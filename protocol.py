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

    def show_frame(self):
        print(f"Magic: {hex(self.magic)} \
              \n Command: {hex(self.command.value)} \
              \n Value: {hex(self.value)} \
              \n Checksum: {hex(self.checksum)}")


frame = ProtFrame(Command.READ, 145)
frame.show_frame()