
# MiniFuzz/1.0 Protocol Fuzzer

## What this project is about

The goal of this project is to implement a Python application that:
1. Generates valid data frames according to the MiniFuzz/1.0 protocol specification.
2. Produces sequences of malformed frames from the initial valid frame using different mutation techniques.
3. Simulates communication with a fake device that receives both valid and mutated frames, accepting or rejecting them.

As a result, the application's user gets a detailed text output where the mutation process for a given initial valid frame as well as corresponding responses from the fake device are tracked. 

**Example output:**

```text
--- Frame set no. 10 ---
  [VALID]    A5 03 00 00 A8    -> [ACCEPTED] Response: PONG
  [MUTATED]  A5 02 00 00 A8    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa7, got 0xa8
  [MUTATED]  A5 02 00 00 A7    -> [ACCEPTED] action: ACK: Stored value 0
  [MUTATED]  A5 02 00 00 A7    -> [ACCEPTED] action: ACK: Stored value 0
  [MUTATED]  A5 03 00 00 A8    -> [ACCEPTED] Response: PONG
  [MUTATED]  A5 03 FF 00 A8    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa7, got 0xa8
  [MUTATED]  A5 03 FE 00 A8    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa6, got 0xa8
  [MUTATED]  A5 03 FE 00 A9    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa6, got 0xa9
  [MUTATED]  A5 03 FE FF A9    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa5, got 0xa9
  [MUTATED]  A5 03 FE CD FF A9 -> [REJECTED: InvalidLengthError] Expected 5 bytes, got 6
  [MUTATED]  A5 03 FE CD 00 A9 -> [REJECTED: InvalidLengthError] Expected 5 bytes, got 6

```
## Requirements

The application was developed and tested using **Python 3.14.4** and **pytest 9.1.1**.

## Running the application

In order to run the application with default settings, launch:

```bash
python3 minifuzz.py
```

This command runs the mutation process for **one** randomly prepared valid frame and applies a series of randomly selected mutations:

```text
--- Frame set no. 1 ---
  [VALID]    A5 03 00 00 A8
  [MUTATED]  A5 03 FF 00 A7
  [MUTATED]  A5 03 FF 00 A6
  [MUTATED]  A5 FC FF 00 A0
  ...
  [MUTATED]  A5 FC 00 00 A0
  [MUTATED]  A4 FC 00 00 A0

```

A detailed output that shows responses from the fake device can be enabled by adding the `--device` flag. In addition, to ensure reproducibility of the outcomes, one can add the `--seed` flag followed by a selected seed value:

```bash
python3 minifuzz.py --device --seed 33
```

```text
  [VALID]    A5 03 00 00 A8    -> [ACCEPTED] Response: PONG
  [MUTATED]  A5 03 FF 00 A7    -> [REJECTED: InvalidValueError] PING frame must have value set to 0, got 65280
  [MUTATED]  A5 03 FF 00 A6    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa7, got 0xa6
  [MUTATED]  A5 FC FF 00 A0    -> [REJECTED: UnknownCommandError] Unknown command byte: 0xfc
  ...
  [MUTATED]  A5 FC 00 00 A0    -> [REJECTED: ChecksumMismatchError] Expected checksum 0xa1, got 0xa0
  [MUTATED]  A4 FC 00 00 A0    -> [REJECTED: InvalidSOFError] Expected SOF 0xA5, got 0xa4

```

Moreover, it is possible to add the `--count` flag followed by an integer value that determines the number of generated frame sets:

```bash
python3 minifuzz.py --count 33
```

Last but not least, one can use the `--min_mut` and `--max_mut` flags to specify the range for the number of mutations applied to each initial valid frame. During the fuzzing procedure, a random amount of distortions is selected within this range for every initial frame:

```bash
python3 minifuzz.py --min_mut 5 --max_mut 10
```

In order to obtain a fixed number of mutations for every valid frame, it is sufficient to set both `--min_mut` and `--max_mut` to the same value:

```bash
python3 minifuzz.py --min_mut 5 --max_mut 5
```
The default value for both flags is 10.

## Running the tests

The tests of the application are located in the `tests/` directory. They cover testing checksum calculation, valid frame construction for all three command types, and boundary values handling for `ProtFrame` objects, as well as asserting mutation process reliability and reproducibility for given seeds in `MutationFuzzer`. Moreover, communication-related error handling testing is performed for the `FakeDevice` class as well.

In order to run the tests, create a virtual Python environment (recommended) and install pytest:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
```

Then, run the test suite:

```bash
python3 -m pytest -v
```

## MiniFuzz/1.0 Protocol

The protocol is a simple binary communication mechanism simulating data transmission between IoT devices. It produces 5-byte frames consisting of 4 fields:

| Field | Size | Description |
| --- | --- | --- |
| **SOF** (Start of Frame) | 1 byte | Magic byte, fixed value `0xA5`. |
| **Command** | 1 byte | Command type: `READ` (`0x01`), `WRITE` (`0x02`), `PING` (`0x03`). |
| **Value** | 2 bytes | Big-endian unsigned integer (`0-65535`). Must be `0` for `PING`. |
| **Checksum** | 1 byte | Sum of the first 4 bytes modulo 256. |

The Command field supports three operations:

* `READ` (`0x01`): Requests reading data from a specified device memory location or register. The 2-byte Value field specifies the target address (`0-65535`). In response, the fake device sends a 2-byte value.
* `WRITE` (`0x02`): Delivers a 2-byte payload value (`0-65535`) to be stored or processed by the target device. In response, the fake device returns an acknowledgment (ACK).
* `PING` (`0x03`): Heartbeat frame used to test connectivity. The Value field is unused and must strictly be set to `0` (`0x0000`). In response, the fake device returns PONG.

## Mutation strategies

The `MutationFuzzer` class provides a set of different mutations applied to the protocol frames, divided into three main categories:

### 1. **Size-altering mutations**

Responsible for modifying the length of frames by inserting or deleting a randomly selected byte.

* `delete_random_byte`: Deletes a byte at a uniform random position.
* `insert_random_byte`: Inserts a random byte (`0-255`) at a uniform random position.

### 2. **Content-altering mutations**

Responsible for modifying bit or byte values within the frame:

* `flip_random_bit`: Inverts a single randomly chosen bit using a bitwise XOR operation.
* `flip_random_byte`: Inverts all 8 bits of a randomly selected byte using XOR `0xFF`.
* `increase_byte`: Increments a randomly selected byte by `1` (modulo 256).
* `decrease_byte`: Decrements a randomly selected byte by `1` (modulo 256).

### 3. **Fixing mutations**

Due to the hierarchy of exceptions thrown by the `FakeDevice` class (1. `InvalidLengthError`, 2. `InvalidSOFError`, 3. `ChecksumMismatchError`, 4. `UnknownCommandError`, 5. `InvalidValueError`), certain errors are significantly less likely to be triggered during blind fuzzing. For instance, the probability of reaching an unknown command error is very low because frames are usually discarded earlier due to SOF or checksum mismatches.

To address this, a set of fixing mutations is provided in the form of function wrappers:

* `correct_checksum_wrapper(...)` 
  * `flip_random_bit`
  * `flip_random_byte`
  * `increase_byte`
  * `decrease_byte`

* `correct_sof_wrapper(...)` 
  * `flip_random_bit`
  * `flip_random_byte`
  * `increase_byte`
  * `decrease_byte`

* `correct_checksum_wrapper(correct_sof_wrapper(...))` 
  * `flip_random_bit`
  * `flip_random_byte`
  * `increase_byte`
  * `decrease_byte`

This approach enables deeper protocol testing.

### Selection Weights & Rationale

Mutations are selected in `fuzz_frame()` according to assigned probability weights. The `fuzz_full()` function applies a sequence of these consecutive mutations to an initial valid frame and returns the full mutation history. The weights for every mutation are:

* **Basic mutations (60% overall probability):**
  * `delete_random_byte`: 3
  * `insert_random_byte`: 3
  * `flip_random_bit`: 12
  * `flip_random_byte`: 6
  * `increase_byte`: 9
  * `decrease_byte`: 9

* **Fixing mutations (40% overall probability):**
  * `correct_checksum_wrapper` (4 variants): weight of 2 each (total = 8)
  * `correct_sof_wrapper` (4 variants): weight of 2 each (total = 8)
  * `correct_checksum_wrapper(correct_sof_wrapper(...))` (4 variants): weight of 3 each (total = 12)

These probability values were chosen intuitively based on real-world transmission error scenarios. Single-bit flips (noise on physical lines) and minor arithmetic shifts (off-by-one errors) are far more common than complete byte corruption or structural packet loss/insertion. Furthermore, maintaining a 3:2 overall ratio (60% blind mutations to 40% fixing/smart mutations) balances raw physical line error simulation with business logic testing. Notably, the weight ratios for both basic and fixing mutations can be further adjusted based on the specification of the simulated device or derived empirically.