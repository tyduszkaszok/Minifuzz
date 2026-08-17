import argparse
import random
from fakedevice import FakeDevice, ProtocolError
from mutator import MutationFuzzer
from protocol import Command, ProtFrame


def format_frame_output(
    frame_bytes: bytes, label: str, device: FakeDevice | None = None
) -> str:
    hex_str = frame_bytes.hex(" ").upper()

    if device is None:
        return f"  {label:<10} {hex_str}"

    try:
        data_dict = device.receive_frame(frame_bytes)
        key, val = list(data_dict.items())[1]
        status_str = f"[ACCEPTED] {key}: {val}"
    except ProtocolError as e:
        status_str = f"[REJECTED: {type(e).__name__}] {e}"

    return f"  {label:<10} {hex_str:<17} -> {status_str}"


def main():
    parser = argparse.ArgumentParser(
        description="MiniFuzz CLI & Frame Generator"
    )
    parser.add_argument(
        "--count",
        help="specify number of frames to generate",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--seed",
        help="set constant seed value ensuring reproducibility of outcomes",
        type=int,
    )
    parser.add_argument(
        "--device",
        help="simulates communication with a fake device",
        action="store_true",
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    device = FakeDevice() if args.device else None
    fuzzer = MutationFuzzer(min_mutations=20, max_mutations=20)

    for i in range(args.count):
        command = random.choice(list(Command))
        value = 0 if command == Command.PING else random.randint(0, 255)

        frame = ProtFrame(command, value)
        valid_bytes = frame.to_bytes()

        print(f"\n--- Frame set no. {i+1} ---")
        print(format_frame_output(valid_bytes, "[VALID]", device))

        mutated_frames = fuzzer.fuzz_full(valid_bytes)
        for f in mutated_frames:
            print(format_frame_output(f, "[MUTATED]", device))


if __name__ == "__main__":
    main()