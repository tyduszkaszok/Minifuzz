import random
from typing import List, Callable


class MutationFuzzer:
    """Fuzzer that applies sequences of randomly selected mutations to frames.

    Attributes:
        min_mutations (int): Lower boundary of the number of mutations to apply.
        max_mutations (int): Upper boundary of the number of mutations to apply.
        mutators (list[Callable[[bytes], bytes]]): List of basic mutation functions.
        fixing_mutators (list[Callable[[bytes], bytes]]): List of fixing mutation functions.
        all_mutators (list[Callable[[bytes], bytes]]): List of both basic and fixing mutators.
             During fuzzing, specific mutators are chosen according to probability weights.
        weights (list[int]): List of probability weights corresponding to each mutator.
    """
    def __init__(
        self,
        min_mutations: int = 10,
        max_mutations: int = 10,
    ) -> None:
        if min_mutations > max_mutations:
            raise ValueError(
                    f"min_mutations ({min_mutations}) cannot be greater than max_mutations ({max_mutations})"
                ) 
        self.min_mutations = min_mutations
        self.max_mutations = max_mutations
        basic_weighted: list[tuple[Callable[[bytes], bytes], int]] = [
            (self.delete_random_byte, 3),
            (self.insert_random_byte, 3),
            (self.flip_random_bit, 12),
            (self.flip_random_byte, 6),
            (self.increase_byte, 8),
            (self.decrease_byte, 8),
            (self.set_boundary_byte, 2)
        ]

        fixing_weighted: list[tuple[Callable[[bytes], bytes], int]] = [

            (self.correct_checksum_wrapper(self.flip_random_bit), 2),
            (self.correct_checksum_wrapper(self.flip_random_byte), 2),
            (self.correct_checksum_wrapper(self.increase_byte), 2),
            (self.correct_checksum_wrapper(self.decrease_byte), 2),

            (self.correct_sof_wrapper(self.flip_random_bit), 2),
            (self.correct_sof_wrapper(self.flip_random_byte), 2),
            (self.correct_sof_wrapper(self.increase_byte), 2),
            (self.correct_sof_wrapper(self.decrease_byte), 2),

            (self.correct_checksum_wrapper(self.correct_sof_wrapper(self.flip_random_bit)), 3),
            (self.correct_checksum_wrapper(self.correct_sof_wrapper(self.flip_random_byte)), 3),
            (self.correct_checksum_wrapper(self.correct_sof_wrapper(self.increase_byte)), 3),
            (self.correct_checksum_wrapper(self.correct_sof_wrapper(self.decrease_byte)), 3),
        ]

        self.basic_mutators = [mutator for mutator, _ in basic_weighted]
        self.fixing_mutators = [mutator for mutator, _ in fixing_weighted]

        all_weighted = basic_weighted + fixing_weighted
        self.all_mutators, self.weights = zip(*all_weighted)

    def fuzz_full(self, b : bytes) -> List[bytes]:
        """Generates a sequence of mutated frames derived from an initial valid frame.

        Args:
            b (bytes): Initial valid byte frame to be mutated.

        Returns:
            list[bytes]: List of consecutive mutated byte frames.
        """

        frames_fuzzed = []
        num_mutations = random.randint(self.min_mutations, self.max_mutations)
        for _ in range(num_mutations):
            b = self.fuzz_frame(b)
            frames_fuzzed.append(b)
        return frames_fuzzed

    def fuzz_frame(self, b: bytes) -> bytes:
        """Applies a single random mutation to a given byte frame based on weight probabilities.

        Args:
            b (bytes): Byte frame to be mutated.

        Returns:
            bytes: Mutated byte frame after applying a randomly selected mutator.
        """
        mutator = random.choices(self.all_mutators, weights=self.weights, k=1)[0]
        return mutator(b)
    
    @staticmethod
    def delete_random_byte(b: bytes) -> bytes:
        """Deletes a single randomly chosen byte from the buffer."""
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        return b[:pos] + b[pos + 1 :]

    @staticmethod
    def insert_random_byte(b: bytes) -> bytes:
        """Inserts a single random byte (0-255) at a random position."""
        pos = random.randint(0, len(b))
        random_byte = random.randint(0, 255)
        return b[:pos] + bytes([random_byte]) + b[pos:]

    @staticmethod
    def flip_random_bit(b: bytes) -> bytes:
        """Inverts a single randomly selected bit in the buffer."""
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        byte = b[pos]
        bit = 1 << random.randint(0, 7)
        new_byte = byte ^ bit
        return b[:pos] + bytes([new_byte]) + b[pos + 1 :]

    @staticmethod
    def flip_random_byte(b: bytes) -> bytes:
        """Inverts all bits (XOR 0xFF) of a single randomly chosen byte."""
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        new_byte = b[pos] ^ 0xFF
        return b[:pos] + bytes([new_byte]) + b[pos + 1 :]

    @staticmethod
    def increase_byte(b: bytes) -> bytes:
        """Increments a single randomly selected byte by 1 (modulo 256)."""
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        new_byte = (b[pos] + 1) % 256
        return b[:pos] + bytes([new_byte]) + b[pos + 1 :]

    @staticmethod
    def decrease_byte(b: bytes) -> bytes:
        """Decrements a single randomly selected byte by 1 (modulo 256)."""
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        new_byte = (b[pos] - 1) % 256
        return b[:pos] + bytes([new_byte]) + b[pos + 1 :]

    @staticmethod
    def set_boundary_byte(b: bytes) -> bytes:
        """Replaces a random byte with a boundary value (0x00, 0xFF, 0x7F, 0x80)."""
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        boundary_value = random.choice([0x00, 0xFF, 0x7F, 0x80])
        return b[:pos] + bytes([boundary_value]) + b[pos + 1 :]

    @staticmethod
    def correct_sof_wrapper(mutator: Callable[[bytes], bytes]) -> Callable[[bytes], bytes]:
        """Fixes mutations that modify the magic byte."""
        def correct_sof(b: bytes) -> bytes:
            mutated = mutator(b)
            if mutated:
                return bytes([0xA5]) + mutated[1:]
            return mutated
        return correct_sof

    @staticmethod
    def correct_checksum_wrapper(mutator: Callable[[bytes], bytes]) -> Callable[[bytes], bytes]:
        """Fixes mutations that modify the checksum."""
        def correct_checksum(b: bytes) -> bytes:
            mutated = mutator(b)
            if len(mutated) == 5:
                new_cs = sum(mutated[:4]) % 256
                return mutated[:4] + bytes([new_cs])
            return mutated
        return correct_checksum
