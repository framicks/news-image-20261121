"""Copy the front page for 21 November 2026 to the output directory.

The entry image lives next to this script as ``entry.png``. The program
copies it byte for byte to ``$MAKEFUN_OUTPUT_DIR/entry.png`` (default
``/output``), creating the directory if needed. Standard library only, no
network access.
"""

import os
import sys

SOURCE_NAME = "entry.png"
MAX_BYTES = 1_048_576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    with open(source, "rb") as handle:
        blob = handle.read()
    if len(blob) > MAX_BYTES:
        raise ValueError(f"{source} is {len(blob)} bytes, over the 1 MiB limit")
    if not blob.startswith(PNG_MAGIC):
        raise ValueError(f"{source} does not start with the PNG signature")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, SOURCE_NAME)
    with open(target, "wb") as handle:
        handle.write(blob)
    print(f"wrote {target} ({len(blob)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
