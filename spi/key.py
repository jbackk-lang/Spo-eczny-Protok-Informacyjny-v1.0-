"""
Key derivation for the Social Information Protocol (SPI).

A passphrase is stretched with PBKDF2-HMAC-SHA256 to produce a
deterministic byte sequence that drives all geometric transformations.
"""

import hashlib
import hmac
import struct

_SALT = b"SPI-v1.0-salt"
_ITERATIONS = 100_000
_KEY_BYTES = 64


def derive_key(passphrase: str) -> bytes:
    """Derive a fixed-length key from *passphrase* using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        _SALT,
        _ITERATIONS,
        dklen=_KEY_BYTES,
    )


def _prf(key: bytes, index: int) -> int:
    """Pseudo-random function: maps (key, index) → integer in [0, 2^32)."""
    digest = hmac.new(key, struct.pack(">Q", index), "sha256").digest()
    return struct.unpack(">I", digest[:4])[0]


def build_permutation(key: bytes, size: int) -> list[int]:
    """
    Build a deterministic permutation of [0, size) using a Fisher-Yates
    shuffle seeded from *key*.
    """
    perm = list(range(size))
    for i in range(size - 1, 0, -1):
        j = _prf(key, i) % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def build_inverse_permutation(perm: list[int]) -> list[int]:
    """Return the inverse of *perm*."""
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv
