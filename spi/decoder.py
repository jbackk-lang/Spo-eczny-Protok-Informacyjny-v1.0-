"""
Geometric decoder for the Social Information Protocol (SPI).

Reverses the encoding performed by :mod:`spi.encoder`.  The same key
(passphrase) that was used for encoding is required; without it the
coordinate structure cannot be mapped back to the original byte values.
"""

import json
import struct

from .key import derive_key, build_permutation

_GRID_SIZE = 16


def _make_reverse_grid(key: bytes) -> dict[tuple[int, int], int]:
    """Return a mapping: (col, row) → byte_value."""
    perm = build_permutation(key, 256)
    reverse: dict[tuple[int, int], int] = {}
    for pos, byte_val in enumerate(perm):
        col = pos % _GRID_SIZE
        row = pos // _GRID_SIZE
        reverse[(col, row)] = byte_val
    return reverse


def decode(structure: str, passphrase: str) -> str:
    """
    Decode a geometric structure produced by :func:`spi.encoder.encode`.

    Parameters
    ----------
    structure:
        JSON string as returned by :func:`~spi.encoder.encode`.
    passphrase:
        The same passphrase that was used during encoding.

    Returns
    -------
    str
        The original plaintext message.

    Raises
    ------
    ValueError
        If the structure is malformed or the version tag is unrecognised.
    KeyError
        If a coordinate pair does not map to any byte value, which
        indicates that a wrong passphrase was supplied.
    """
    try:
        data = json.loads(structure)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid geometric structure: {exc}") from exc

    if data.get("version") != "SPI-1.0":
        raise ValueError(f"Unsupported version: {data.get('version')!r}")

    nonce_hex = data["nonce"]
    points = data["points"]

    nonce = bytes.fromhex(nonce_hex)
    nonce_int = struct.unpack(">Q", nonce)[0]

    key = derive_key(passphrase)
    reverse_grid = _make_reverse_grid(key)

    raw_bytes = bytearray()
    for i, (px, py) in enumerate(points):
        offset_x = ((nonce_int >> ((i * 3) % 56)) & 0xF) % _GRID_SIZE
        offset_y = ((nonce_int >> ((i * 5) % 56)) & 0xF) % _GRID_SIZE
        col = (px - offset_x) % _GRID_SIZE
        row = (py - offset_y) % _GRID_SIZE
        try:
            byte_val = reverse_grid[(col, row)]
        except KeyError:
            raise KeyError(
                f"Coordinate ({col}, {row}) at position {i} does not map to any "
                "byte value — the passphrase is likely incorrect."
            ) from None
        raw_bytes.append(byte_val)

    return raw_bytes.decode("utf-8")
