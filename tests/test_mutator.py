from protocol import Command, ProtFrame
from mutator import MutationFuzzer
import random
import pytest

def test_mutation_difference():
    frame_original = ProtFrame(Command.READ, 21)
    fuzzer = MutationFuzzer()
    original_bytes = frame_original.to_bytes()
    frame_mutated = fuzzer.fuzz_frame(original_bytes)
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

def test_min_max_handling():
    with pytest.raises(ValueError):
        MutationFuzzer(min_mutations=20, max_mutations=10)
