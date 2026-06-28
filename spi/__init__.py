"""
Społeczny Protokół Informacyjny (SPI) — Social Information Protocol v1.0

A geometry-based message encoding system that lets two parties exchange
text through an opaque geometric structure.  Only holders of the shared
passphrase can decode the structure back to the original message.

Quick start
-----------
>>> from spi import Channel
>>> ch = Channel("my-secret-passphrase")
>>> geo = ch.send("Hello, world!")
>>> ch.receive(geo)
'Hello, world!'

Or use the lower-level helpers directly:

>>> from spi import encode, decode
>>> geo = encode("Hello!", "my-secret")
>>> decode(geo, "my-secret")
'Hello!'
"""

from .encoder import encode
from .decoder import decode
from .channel import Channel

__all__ = ["encode", "decode", "Channel"]
__version__ = "1.0.0"
