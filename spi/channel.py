"""
Private channel abstraction for the Social Information Protocol (SPI).

A :class:`Channel` pairs a fixed passphrase with the encode/decode
operations, providing a stable, reusable object that represents a
private communication channel between parties that share the passphrase.
"""

from .encoder import encode
from .decoder import decode


class Channel:
    """
    A private communication channel secured by a shared passphrase.

    Parameters
    ----------
    passphrase:
        The shared secret used to derive the geometric key.  Both sender
        and receiver must initialise their :class:`Channel` with the same
        passphrase.

    Example
    -------
    >>> ch = Channel("my-secret")
    >>> geo = ch.send("Hello!")
    >>> ch.receive(geo)
    'Hello!'
    """

    def __init__(self, passphrase: str) -> None:
        if not passphrase:
            raise ValueError("Passphrase must not be empty.")
        self._passphrase = passphrase

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send(self, message: str) -> str:
        """
        Encode *message* into a geometric structure ready for transmission.

        Returns
        -------
        str
            A JSON-encoded geometric structure.
        """
        return encode(message, self._passphrase)

    def receive(self, structure: str) -> str:
        """
        Decode a geometric structure received from the channel.

        Parameters
        ----------
        structure:
            A JSON-encoded geometric structure produced by :meth:`send`.

        Returns
        -------
        str
            The original plaintext message.
        """
        return decode(structure, self._passphrase)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Channel(passphrase='***')"
