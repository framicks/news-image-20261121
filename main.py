#!/usr/bin/env python3
"""Copy today's newspaper front-page image to the output directory.

Locates entry.png next to this script, checks that it is a genuine PNG
of 1024x1024 pixels, copies it to /output/entry.png (creating the
directory when needed), and verifies the copy is byte-for-byte identical
to the source by comparing SHA-256 digests.
"""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_png_dimensions(path: Path) -> tuple[int, int]:
    """Read width and height from the IHDR chunk of a PNG file."""
    with path.open("rb") as handle:
        header = handle.read(8)
        if header != PNG_SIGNATURE:
            raise ValueError(f"{path} is not a PNG file (bad signature)")
        length_bytes = handle.read(4)
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR":
            raise ValueError(f"{path} has no IHDR chunk first")
        if len(length_bytes) != 4:
            raise ValueError(f"{path} is truncated")
        ihdr = handle.read(13)
        if len(ihdr) != 13:
            raise ValueError(f"{path} has a truncated IHDR chunk")
        width = int.from_bytes(ihdr[0:4], "big")
        height = int.from_bytes(ihdr[4:8], "big")
    return width, height


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy entry.png to the output directory and verify it."
    )
    parser.add_argument(
        "--output",
        default="/output/entry.png",
        help="destination path for the copied image (default: /output/entry.png)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the confirmation line on success",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    source = script_dir / "entry.png"

    if not source.is_file():
        print(f"error: {source} not found", file=sys.stderr)
        return 1

    try:
        width, height = read_png_dimensions(source)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print(
            f"error: expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, "
            f"got {width}x{height}",
            file=sys.stderr,
        )
        return 1

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(source, destination)

    source_hash = sha256_of(source)
    dest_hash = sha256_of(destination)
    if source_hash != dest_hash:
        print("error: copy failed verification (sha256 mismatch)", file=sys.stderr)
        return 1

    if not args.quiet:
        print(
            f"OK: {source.name} ({width}x{height}) copied to {destination} "
            f"and verified (sha256 {dest_hash[:16]}...)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
