# Społeczny Protokół Informacyjny v1.0

**Social Information Protocol — geometry-based message encoding**

SPI is a communication system that encodes plaintext messages into geometric
structures (sequences of 2-D coordinate pairs).  The encoded structure looks
like an opaque set of grid points; only a holder of the shared passphrase can
decode it back to the original text.

---

## Features

| Feature | Description |
|---------|-------------|
| **Geometric encoding** | Every byte of the message is mapped to a `(x, y)` point on a 16 × 16 integer grid.  The mapping is derived from the key, so the structure reveals nothing about the content without it. |
| **Key-based decoding** | A passphrase is stretched with PBKDF2-HMAC-SHA256 (100 000 iterations) to produce a deterministic permutation of the grid.  The same key is required to decode any message. |
| **Per-message nonces** | A random 8-byte nonce is mixed into the coordinate offsets on each encode call, so the same plaintext always produces a different geometric structure. |
| **Private channels** | The `Channel` class pairs a fixed passphrase with the encode/decode operations, providing a reusable object that represents a named private channel. |
| **Zero external dependencies** | The package uses only the Python standard library (`hashlib`, `hmac`, `json`, `os`, `struct`). |

---

## Requirements

- Python 3.10 or later

---

## Installation

```bash
git clone https://github.com/jbackk-lang/Spo-eczny-Protok-Informacyjny-v1.0-.git
cd Spo-eczny-Protok-Informacyjny-v1.0-
```

No installation step is needed — the package has no external dependencies.

---

## Quick start (Python API)

```python
from spi import Channel

# Both sender and receiver share the same passphrase.
ch = Channel("my-secret-passphrase")

# Encode
geo = ch.send("Hello, world!")
print(geo)
# → {"version":"SPI-1.0","nonce":"...","points":[[3,9],[7,2],...]}

# Decode
message = ch.receive(geo)
print(message)
# → Hello, world!
```

Lower-level helpers are also available:

```python
from spi import encode, decode

geo     = encode("Hello!", "my-secret")
message = decode(geo,      "my-secret")
```

---

## Command-line interface

```
python main.py encode --key "my-secret" --message "Hello!"
python main.py decode --key "my-secret" --structure '{"version":"SPI-1.0",...}'
```

Pipe support:

```bash
# Encode to file
python main.py encode --key "shared-key" --message "Hello!" > message.spi

# Decode from file
python main.py decode --key "shared-key" < message.spi
```

---

## How it works

### Grid layout

The 256 possible byte values are arranged in a 16 × 16 grid.  The key
(derived from the passphrase) defines a permutation of those 256 positions,
so each key assigns a unique `(col, row)` address to every byte value.

### Encoding a message

1. The passphrase is expanded to a 64-byte key via PBKDF2-HMAC-SHA256.
2. A random 8-byte nonce is generated.
3. For each byte `b` in the UTF-8 encoded message:
   - The key-derived permutation maps `b` → `(col, row)`.
   - A deterministic per-position offset (derived from the nonce) is added
     modulo 16, producing the transmitted point `(px, py)`.
4. The output is a JSON object with the version tag, nonce, and the list of
   points.

### Decoding

1. The receiver uses the same passphrase to reconstruct the permutation.
2. For each received point `(px, py)`, the nonce offset is subtracted to
   recover `(col, row)`.
3. The inverse permutation maps `(col, row)` back to the original byte value.
4. The collected bytes are decoded as UTF-8.

Without the passphrase the permutation cannot be reconstructed and the
coordinate list appears as random grid noise.

---

## Running tests

```bash
python -m pytest tests/ -v
```

---

## Project structure

```
spi/
  __init__.py   — public API (encode, decode, Channel)
  key.py        — PBKDF2 key derivation and permutation helpers
  encoder.py    — plaintext → geometric structure
  decoder.py    — geometric structure → plaintext
  channel.py    — Channel class (private channel abstraction)
main.py         — CLI entry point
tests/
  test_spi.py   — unit tests
```

---

## License

MIT — see [LICENSE](LICENSE).
