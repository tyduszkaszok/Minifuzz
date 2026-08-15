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

    @staticmethod
    def delete_random_byte():
        pass

    @staticmethod
    def insert_random_byte():
        pass

    @staticmethod
    def flip_random_bit():
        pass

    def mutate(self, b : bytes):
        mutators = [
            self.delete_random_byte,
            self.insert_random_byte,
            self.flip_random_bit,
        ]
        mutator = random.choice(mutators)
        return mutator(b)
