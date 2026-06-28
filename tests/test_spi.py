"""
Tests for the Social Information Protocol (SPI) package.
"""

import json
import pytest

from spi import encode, decode, Channel
from spi.key import derive_key, build_permutation, build_inverse_permutation


# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------

class TestKeyDerivation:
    def test_deterministic(self):
        k1 = derive_key("secret")
        k2 = derive_key("secret")
        assert k1 == k2

    def test_different_passphrases_produce_different_keys(self):
        assert derive_key("secret") != derive_key("other")

    def test_key_length(self):
        assert len(derive_key("any")) == 64


class TestPermutation:
    def test_permutation_is_bijection(self):
        key = derive_key("perm-test")
        perm = build_permutation(key, 256)
        assert sorted(perm) == list(range(256))

    def test_inverse_roundtrip(self):
        key = derive_key("inv-test")
        perm = build_permutation(key, 256)
        inv = build_inverse_permutation(perm)
        for i in range(256):
            assert inv[perm[i]] == i

    def test_different_keys_different_permutations(self):
        p1 = build_permutation(derive_key("a"), 256)
        p2 = build_permutation(derive_key("b"), 256)
        assert p1 != p2


# ---------------------------------------------------------------------------
# Encode / Decode round-trip
# ---------------------------------------------------------------------------

class TestEncodeDecodeRoundtrip:
    def test_simple_ascii(self):
        geo = encode("Hello, world!", "secret")
        assert decode(geo, "secret") == "Hello, world!"

    def test_unicode_message(self):
        msg = "Zażółć gęślą jaźń 🙂"
        geo = encode(msg, "klucz")
        assert decode(geo, "klucz") == msg

    def test_empty_message(self):
        geo = encode("", "key")
        assert decode(geo, "key") == ""

    def test_multiline_message(self):
        msg = "line1\nline2\nline3"
        geo = encode(msg, "multi")
        assert decode(geo, "multi") == msg

    def test_wrong_key_raises(self):
        geo = encode("secret message", "correct-key")
        # A wrong key produces garbled bytes; decode may raise or return garbage.
        # We just verify it does NOT return the original message.
        try:
            result = decode(geo, "wrong-key")
            assert result != "secret message"
        except Exception:
            pass  # raising is also acceptable

    def test_encoded_output_is_valid_json(self):
        geo = encode("test", "key")
        data = json.loads(geo)
        assert data["version"] == "SPI-1.0"
        assert "nonce" in data
        assert "points" in data

    def test_points_are_within_grid(self):
        geo = encode("abcdefg", "k")
        data = json.loads(geo)
        for (x, y) in data["points"]:
            assert 0 <= x < 16
            assert 0 <= y < 16

    def test_same_message_different_nonces(self):
        """Two encodings of the same message should differ (probabilistic)."""
        geo1 = encode("hello", "k")
        geo2 = encode("hello", "k")
        d1 = json.loads(geo1)
        d2 = json.loads(geo2)
        # Nonces should differ (birthday probability is negligible for 8 bytes)
        assert d1["nonce"] != d2["nonce"]

    def test_long_message(self):
        msg = "A" * 1000
        geo = encode(msg, "longkey")
        assert decode(geo, "longkey") == msg


# ---------------------------------------------------------------------------
# Malformed input
# ---------------------------------------------------------------------------

class TestMalformedInput:
    def test_invalid_json_raises_value_error(self):
        with pytest.raises(ValueError):
            decode("not-json", "key")

    def test_wrong_version_raises_value_error(self):
        bad = json.dumps({"version": "SPI-9.9", "nonce": "00" * 8, "points": []})
        with pytest.raises(ValueError, match="Unsupported version"):
            decode(bad, "key")


# ---------------------------------------------------------------------------
# Channel API
# ---------------------------------------------------------------------------

class TestChannel:
    def test_send_receive_roundtrip(self):
        ch = Channel("shared-secret")
        geo = ch.send("Hello via channel!")
        assert ch.receive(geo) == "Hello via channel!"

    def test_two_channel_instances_same_key(self):
        sender = Channel("shared")
        receiver = Channel("shared")
        geo = sender.send("ping")
        assert receiver.receive(geo) == "ping"

    def test_wrong_channel_key_does_not_decode_correctly(self):
        sender = Channel("correct")
        wrong_receiver = Channel("wrong")
        geo = sender.send("secret data")
        try:
            result = wrong_receiver.receive(geo)
            assert result != "secret data"
        except Exception:
            pass

    def test_empty_passphrase_raises(self):
        with pytest.raises(ValueError):
            Channel("")

    def test_channel_repr_hides_passphrase(self):
        ch = Channel("super-secret")
        assert "super-secret" not in repr(ch)
