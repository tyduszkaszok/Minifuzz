from mutator import MutationFuzzer
from protocol import ProtFrame, Command

import argparse, random

frame_count = 1

parser = argparse.ArgumentParser()
parser.add_argument("--count", help="specify number of frames to generate", type=int)
parser.add_argument("--seed", help="set constant seed value ensuring reproducability of outcomes", type=int)
args = parser.parse_args()

if args.count:
    frame_count = args.count
if args.seed:
    random.seed(args.seed)

min_mutations = 20
max_mutations = 20

fuzzer = MutationFuzzer(min_mutations, max_mutations)

for i in range(frame_count):
    command = random.choice(list(Command))
    value = 0
    if command != Command.PING:
        value = random.randint(0, 255)
    frame = ProtFrame(command, value)
    frame_in_bytes = frame.to_bytes()
    print(f"Frame no. {i+1}")
    print(f"[VALID] {frame_in_bytes.hex(' ').upper()}")

    frames_mutated = fuzzer.fuzz_full(frame_in_bytes)
    for f in frames_mutated:
        print(f"[MUTATED] {f.hex(' ').upper()}")
    print()


