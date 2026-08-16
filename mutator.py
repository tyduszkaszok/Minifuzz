import random
from typing import List


class MutationFuzzer:

    def __init__(self, seed: List[bytes],
                 min_mutations: int = 2,
                 max_mutations: int = 10) -> None:
        self.seed = seed
        self.min_mutations = min_mutations
        self.max_mutations = max_mutations
        self.reset()

    def reset(self) -> None:
        self.population = self.seed
        self.seed_index = 0

    def fuzz(self) -> bytes:
        if self.seed_index < len(self.seed):
            self.inp = self.seed[self.seed_index]
            self.seed_index += 1
        else:
            self.inp = self.create_candidate()
        return self.inp

    def create_candidate(self) -> bytes:
        candidate = random.choice(self.seed)
        num_mut = random.randint(self.min_mutations, self.max_mutations)
        for _ in range(num_mut):
            candidate = self.mutate(candidate)
        return candidate

    @staticmethod
    def delete_random_byte(b : bytes) -> bytes:
        if not b:
            return b
        pos = random.randint(0, len(b) - 1)
        return b[:pos] + b[pos+1:]
   

    @staticmethod
    def insert_random_byte(b : bytes) -> bytes:
        if b is None:
            return b
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

    def mutate(self, b : bytes):
        mutators = [
            self.delete_random_byte,
            self.insert_random_byte,
            self.flip_random_bit,
        ]
        mutator = random.choice(mutators)
        return mutator(b)
