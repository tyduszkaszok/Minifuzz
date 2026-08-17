import random
from typing import List


class MutationFuzzer:

    def __init__(
        self,
        min_mutations: int = 2,
        max_mutations: int = 10,
    ) -> None:
        self.min_mutations = min_mutations
        self.max_mutations = max_mutations
        self.mutators = [
            self.delete_random_byte,
            self.insert_random_byte,
            self.flip_random_bit,
            self.flip_random_byte,
            self.increase_byte,
            self.decrease_byte
        ]

        self.weights = [1, 1, 4, 2, 3, 3]

    def fuzz_full(self, b : bytes) -> List[bytes]:
        frames_fuzzed = []
        num_mutations = random.randint(self.min_mutations, self.max_mutations)
        for _ in range(num_mutations):
            b = self.fuzz_frame(b)
            frames_fuzzed.append(b)
        return frames_fuzzed

    def fuzz_frame(self, b: bytes) -> bytes:
        mutator = random.choices(self.mutators, weights=self.weights, k=1)[0]
        return mutator(b)
    
    @staticmethod
    def delete_random_byte(b : bytes) -> bytes:
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        return b[:pos] + b[pos+1:]
   

    @staticmethod
    def insert_random_byte(b : bytes) -> bytes:
        pos = random.randint(0, len(b))
        random_byte = random.randint(0, 255)
        return b[:pos] + bytes([random_byte]) + b[pos:]

    @staticmethod
    def flip_random_bit(b : bytes) -> bytes:
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        byte = b[pos]
        bit = 1 << random.randint(0, 7)
        new_byte = byte ^ bit

        return b[:pos] + bytes([new_byte]) + b[pos+1:]

    @staticmethod
    def flip_random_byte(b : bytes) -> bytes:
        if not b:
            return b
        pos = random.randint(0, len(b)-1)
        new_byte = b[pos] ^ 0xFF
        return b[:pos] + bytes([new_byte]) + b[pos+1:]

    @staticmethod
    def increase_byte(b : bytes) -> bytes:
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        new_byte = (b[pos] + 1) % 256
        return b[:pos] + bytes([new_byte]) + b[pos+1:]

    @staticmethod
    def decrease_byte(b: bytes) -> bytes:
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        new_byte = (b[pos] - 1) % 256
        return b[:pos] + bytes([new_byte]) + b[pos + 1:]