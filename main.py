#!/usr/bin/env python3
"""
SPI command-line interface.

Usage
-----
Encode a message::

    python main.py encode --key "my-secret" --message "Hello!"

Decode a geometric structure::

    python main.py decode --key "my-secret" --structure '{"version":"SPI-1.0",...}'

Or pipe the structure from a file::

    python main.py encode --key "my-secret" --message "Hello!" > msg.spi
    python main.py decode --key "my-secret" < msg.spi
"""

import argparse
import sys

from spi import encode, decode


def cmd_encode(args: argparse.Namespace) -> None:
    message = args.message or sys.stdin.read().rstrip("\n")
    print(encode(message, args.key))


def cmd_decode(args: argparse.Namespace) -> None:
    structure = args.structure or sys.stdin.read().rstrip("\n")
    try:
        print(decode(structure, args.key))
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spi",
        description="Społeczny Protokół Informacyjny — geometry-based message encoding",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # encode sub-command
    enc = sub.add_parser("encode", help="Encode a message into a geometric structure")
    enc.add_argument("--key", required=True, help="Shared passphrase")
    enc.add_argument("--message", default="", help="Plaintext message (or use stdin)")
    enc.set_defaults(func=cmd_encode)

    # decode sub-command
    dec = sub.add_parser("decode", help="Decode a geometric structure to plaintext")
    dec.add_argument("--key", required=True, help="Shared passphrase")
    dec.add_argument("--structure", default="", help="Geometric structure JSON (or use stdin)")
    dec.set_defaults(func=cmd_decode)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
