import pytest
from protocol import Command, ProtFrame

def test_ping_checksum_building():
    frame = ProtFrame(Command.PING, value = 0)
    data = frame.to_bytes()
    assert data == b"\xa5\x03\x00\x00\xa8"
    assert frame.checksum == 0xA8

def test_read_frame_building():
    frame = ProtFrame(Command.READ, value=10)
    assert frame.to_bytes() == b"\xa5\x01\x00\x0a\xb0"
    assert frame.checksum == 0xB0


def test_write_frame_building():
    frame = ProtFrame(Command.WRITE, value=255)
    assert frame.to_bytes() == b"\xa5\x02\x00\xff\xa6"
    assert frame.checksum == 0xA6

def test_value_boundary_limits():

    frame_min = ProtFrame(Command.READ, value=0)
    frame_max = ProtFrame(Command.READ, value=65535)

    assert frame_min.value == 0
    assert frame_max.value == 65535

def test_value_out_of_range_raises_error():
    with pytest.raises(ValueError):
        ProtFrame(Command.READ, value=65536)

    with pytest.raises(ValueError):
        ProtFrame(Command.READ, value=-1)


def test_ping_with_non_zero_value_raises_error():
    with pytest.raises(ValueError):
        ProtFrame(Command.PING, value=1)