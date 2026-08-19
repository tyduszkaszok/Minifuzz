from protocol import Command, ProtFrame
from mutator import MutationFuzzer
import random
import pytest

def test_mutation_difference():
    frame_original = ProtFrame(Command.READ, 21)
    fuzzer = MutationFuzzer()
    original_bytes = frame_original.to_bytes()
    basic_mutator = random.choice(fuzzer.basic_mutators)
    frame_mutated = basic_mutator(original_bytes)
    assert frame_mutated != original_bytes

def test_delete_random_byte_shortens_buffer():
    original = b"\xa5\x01\x00\x0a\xb0" 
    mutated = MutationFuzzer.delete_random_byte(original)
    assert len(mutated) == 4


def test_insert_random_byte_lengthens_buffer():
    original = b"\xa5\x01\x00\x0a\xb0"  
    mutated = MutationFuzzer.insert_random_byte(original)
    assert len(mutated) == 6


def test_flip_random_bit_keeps_length_but_changes_data():
    original = b"\xa5\x01\x00\x0a\xb0"  
    mutated = MutationFuzzer.flip_random_bit(original)
    assert len(mutated) == len(original)  
    assert mutated != original  


def test_flip_random_byte_keeps_length_but_changes_data():
    original = b"\xa5\x01\x00\x0a\xb0"
    mutated = MutationFuzzer.flip_random_byte(original)
    assert len(mutated) == len(original)
    assert mutated != original


def test_increase_byte_keeps_length_but_changes_data():
    original = b"\xa5\x01\x00\x0a\xb0"
    mutated = MutationFuzzer.increase_byte(original)
    assert len(mutated) == len(original)
    assert mutated != original


def test_decrease_byte_keeps_length_but_changes_data():
    original = b"\xa5\x01\x00\x0a\xb0"
    mutated = MutationFuzzer.decrease_byte(original)
    assert len(mutated) == len(original)
    assert mutated != original

def test_fuzzer_reproducibility_with_seed():
    original = b"\xa5\x03\x00\x00\xa8"
    random.seed(44)
    fuzzer1 = MutationFuzzer()
    res1 = fuzzer1.fuzz_frame(original)
    random.seed(44)
    fuzzer2 = MutationFuzzer()
    res2 = fuzzer2.fuzz_frame(original)
    assert res1 == res2

def test_fuzz_empty_bytes_handling():
    fuzzer = MutationFuzzer()
    assert fuzzer.fuzz_frame(b"") == b""

def test_fuzz_full_generates_correct_number_of_frames():
    original = b"\xa5\x01\x00\x0a\xb0"
    fuzzer = MutationFuzzer(min_mutations=5, max_mutations=5)
    mutated_frames = fuzzer.fuzz_full(original)
    assert len(mutated_frames) == 5

def test_min_max_handling():
    with pytest.raises(ValueError):
        MutationFuzzer(min_mutations=20, max_mutations=10)


def test_correct_sof_wrapper_always_forces_sof():
    original = b"\xa5\x01\x00\x0a\xb0"
    wrapped_mutator = MutationFuzzer.correct_sof_wrapper(MutationFuzzer.flip_random_byte)

    for _ in range(20):
        mutated = wrapped_mutator(original)
        assert mutated[0] == 0xA5


def test_correct_checksum_wrapper_recalculates_valid_checksum():
    original = b"\xa5\x01\x00\x0a\xb0"
    wrapped_mutator = MutationFuzzer.correct_checksum_wrapper(MutationFuzzer.flip_random_bit)

    for _ in range(20):
        mutated = wrapped_mutator(original)
        if len(mutated) == 5:
            expected_checksum = sum(mutated[:4]) % 256
            assert mutated[4] == expected_checksum


def test_chained_wrappers_force_both_sof_and_checksum():
    original = b"\xa5\x01\x00\x0a\xb0"
    chained_mutator = MutationFuzzer.correct_checksum_wrapper(
        MutationFuzzer.correct_sof_wrapper(MutationFuzzer.flip_random_bit)
    )

    for _ in range(20):
        mutated = chained_mutator(original)
        assert mutated[0] == 0xA5
        if len(mutated) == 5:
            expected_checksum = sum(mutated[:4]) % 256
            assert mutated[4] == expected_checksum