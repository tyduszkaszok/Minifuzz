# MiniFuzz/1.0 Protocol Fuzzer

## What this project is about

The goal of this project is to implement a Python apllication that:
1. Generates valid data frames according to the MiniFuzz/1.0 protocol specification
2. Produces sequences of malformed frames from the initial valid frame using different mutation techniques
3. Simulates communication with a fake device that receives both valid and mutated frames, accepting or rejecting them

As the result, the application's user gets a detailed text output where the mutation process for a given initial valid frame as well as corresponding responses from the fake device are tracked. 

**Example output:**

```python
--- Frame set no. 11 ---
  [VALID]    A5 03 00 00 A8    -> [ACCEPTED] Response: PONG
  [MUTATED]  A5 03 00 01 A8    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa9, got 0xa8
  [MUTATED]  A5 03 00 01 A9    -> [ACCEPTED] Response: PONG
  [MUTATED]  A5 03 00 FE A9    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa6, got 0xa9
  [MUTATED]  A5 03 00 FC A9    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa4, got 0xa9
  [MUTATED]  A4 03 00 FC A9    -> [REJECTED: InvalidSOFError] Expected SOF 0xA5, got 0xa4
  [MUTATED]  A4 03 FF FC A9    -> [REJECTED: InvalidSOFError] Expected SOF 0xA5, got 0xa4
  [MUTATED]  5B 03 FF FC A9    -> [REJECTED: InvalidSOFError] Expected SOF 0xA5, got 0x5b
  [MUTATED]  03 FF FC A9       -> [REJECTED: InvalidLengthError] Expected 5 bytes, got 4
```

## Running the application

In order to run the application with default settings one should launch:

```python
python3 minifuzz.py
```
This command runs the mutation process for **one** randomly prepared valid frame and applies a series of 20 randomly selected mutations:

```python
--- Frame set no. 1 ---
  [VALID]    A5 03 00 00 A8
  [MUTATED]  A5 03 01 00 A8
  [MUTATED]  A5 03 01 00 57
  [MUTATED]  A5 02 01 00 57
  [MUTATED]  A5 02 01 00 56
  [MUTATED]  A5 02 00 00 56
  [MUTATED]  A5 02 00 00 55
  ...
  [MUTATED]  A3 A5 02 7E FF 53
  [MUTATED]  A3 A5 FD 7E FF 53
```
However, a detailed output that shows responses from the fake device can be enabled by adding the ```--device``` flag. In addition, to ensure reproducability of the outcomes one can add the ```--seed``` flag followed by a selected seed value:

```python
python3 minifuzz.py --device --seed 33
```

```python
--- Frame set no. 1 ---
  [VALID]    A5 03 00 00 A8    -> [ACCEPTED] Response: PONG
  [MUTATED]  A5 03 01 00 A8    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa9, got 0xa8
  [MUTATED]  A5 03 01 00 57    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa9, got 0x57
  [MUTATED]  A5 02 01 00 57    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa8, got 0x57
  [MUTATED]  A5 02 01 00 56    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa8, got 0x56
  [MUTATED]  A5 02 00 00 56    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa7, got 0x56
  [MUTATED]  A5 02 00 00 55    -> [REJECTED: ChecksumMismatchError] Expected CS 0xa7, got 0x55
  ...
    [MUTATED]  A3 A5 02 7E FF 53 -> [REJECTED: InvalidLengthError] Expected 5 bytes, got 6
  [MUTATED]  A3 A5 FD 7E FF 53 -> [REJECTED: InvalidLengthError] Expected 5 bytes, got 6
```
Moreover, it is possible to add the ```--count``` flag followed by an integer value that determines the number of generated frames:

```python
python3 minifuzz.py --count 33
```
```python
--- Frame set no. 1 ---
  [VALID]    A5 03 00 00 A8
  [MUTATED]  A5 03 00 00 A9
  [MUTATED]  A5 03 00 01 A9
  [MUTATED]  A5 03 20 01 A9
...

--- Frame set no. 2 ---
  [VALID]    A5 02 00 76 1D
  [MUTATED]  A5 02 00 66 1D
  [MUTATED]  A5 02 00 67 1D
  [MUTATED]  A5 02 00 65 1D

...
...
...

--- Frame set no. 32 ---
  [VALID]    A5 03 00 00 A8
  [MUTATED]  A5 03 00 FF A8
  [MUTATED]  A4 03 00 FF A8
  [MUTATED]  A5 03 00 FF A8
...

--- Frame set no. 33 ---
  [VALID]    A5 02 00 F2 99
  [MUTATED]  A5 02 00 F2
  [MUTATED]  A5 42 00 F2
  [MUTATED]  A5 42 01 F2
...
```