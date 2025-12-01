import random

class Seed:
    def __init__(self, rng_seed, file):
        init_rng = random.Random(file)
        rng_seed = init_rng.getrandbits(32) ^ rng_seed
        self.rng_seed = random.Random(rng_seed)

    def seeds_for_file(self, n):
        return [self.rng_seed.randint(0, 2**32 - 1) for _ in range(0, n)]
