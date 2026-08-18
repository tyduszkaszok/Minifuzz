import pytest
from fakedevice import (
    ChecksumMismatchError,
    FakeDevice,
    InvalidLengthError,
    InvalidSOFError,
    UnknownCommandError,
)

def test_check_length_long():
    frame_bytes = b"\xa5\x02\x00\xff\xa6\x67"
    with pytest.raises(InvalidLengthError):
        FakeDevice().receive_frame(frame_bytes)

def test_check_length_short():
    frame_bytes = b"\xa5\x02\x00\xff"
    with pytest.raises(InvalidLengthError):
        FakeDevice().receive_frame(frame_bytes)

def test_check_sof():
    frame_bytes = b"\x5b\x03\x00\x00\x5e"
    with pytest.raises(InvalidSOFError):
        FakeDevice().receive_frame(frame_bytes)

def test_check_checksum():
    frame_bytes = b"\xa5\x03\x00\x00\x21"
    with pytest.raises(ChecksumMismatchError):
        FakeDevice().receive_frame(frame_bytes)

def test_check_command():
    frame_bytes = b"\xa5\x04\x00\x00\xa9"
    with pytest.raises(UnknownCommandError):
        FakeDevice().receive_frame(frame_bytes)

def test_receive_frame_ping_success():
    valid_ping = b"\xa5\x03\x00\x00\xa8"
    response = FakeDevice().receive_frame(valid_ping)

    assert response["status"] == "SUCCESS"
    assert response["Response"] == "PONG"


def test_receive_frame_read_success():
    valid_read = b"\xa5\x01\x00\x0a\xb0"
    response = FakeDevice().receive_frame(valid_read)

    assert response["status"] == "SUCCESS"
    assert "Read value" in response
    assert 0 <= response["Read value"] <= 255


def test_receive_frame_write_success():
    valid_write = b"\xa5\x02\x01\x00\xa8"
    response = FakeDevice().receive_frame(valid_write)

    assert response["status"] == "SUCCESS"
    assert response["action"] == "ACK: Stored value 256"