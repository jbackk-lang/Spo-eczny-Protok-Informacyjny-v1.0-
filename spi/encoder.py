"""
Geometric encoder for the Social Information Protocol (SPI).

Each byte of the plaintext is mapped to a 2-D point (x, y) on an integer
grid derived from the session key.  The resulting list of points forms the
"geometric structure" that is transmitted in place of the original message.

Grid layout
-----------
The grid is SIZE × SIZE where SIZE = ceil(sqrt(256)).  Each cell holds one
byte value under the key-derived permutation.  A byte value is therefore
encoded as the (column, row) coordinates of its cell.

Additionally, a per-message random nonce is mixed into the coordinate
offsets so that the same plaintext produces different geometric structures
each time it is encoded.
"""

import json
import math
import os
import struct

from .key import derive_key, build_permutation

_GRID_SIZE = math.ceil(math.sqrt(256))  # 16


def _make_grid(key: bytes) -> dict[int, tuple[int, int]]:
    """Return a mapping: byte_value → (col, row)."""
    perm = build_permutation(key, 256)
    grid: dict[int, tuple[int, int]] = {}
    for pos, byte_val in enumerate(perm):
        col = pos % _GRID_SIZE
        row = pos // _GRID_SIZE
        grid[byte_val] = (col, row)
    return grid


def encode(message: str, passphrase: str) -> str:
    """
    Encode *message* into a JSON geometric structure.

    Returns a JSON string containing:
    - ``"nonce"``  – 8-byte hex string (random per call)
    - ``"points"`` – list of ``[x, y]`` coordinate pairs
    - ``"version"`` – protocol version string
    """
    key = derive_key(passphrase)
    grid = _make_grid(key)

    nonce = os.urandom(8)
    nonce_int = struct.unpack(">Q", nonce)[0]

    data = message.encode("utf-8")
    points: list[list[int]] = []
    for i, byte_val in enumerate(data):
        col, row = grid[byte_val]
        # Apply a deterministic per-position offset derived from nonce
        offset_x = ((nonce_int >> ((i * 3) % 56)) & 0xF) % _GRID_SIZE
        offset_y = ((nonce_int >> ((i * 5) % 56)) & 0xF) % _GRID_SIZE
        px = (col + offset_x) % _GRID_SIZE
        py = (row + offset_y) % _GRID_SIZE
        points.append([px, py])

    structure = {
        "version": "SPI-1.0",
        "nonce": nonce.hex(),
        "points": points,
    }
    return json.dumps(structure, separators=(",", ":"))
