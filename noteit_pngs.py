"""A specific script for extracting PNG pages from NotateIt .nat files."""

from __future__ import annotations

__author__ = "NIKDISSV"

import re
import zlib

from argparse import ArgumentParser
from pathlib import Path


def extract_nat(
    fp: Path, force: bool = False, outdir: str = None, outfile: str = "page_%02d.png"
) -> None:
    data = fp.read_bytes()
    if not (data.startswith(b"NotateIt") or force):
        raise ValueError("The file doesn't look like NotateIt .nat")
    start = data.find(b"x\x9c")
    if start == -1:
        raise ValueError("zlib block not found")
    raw = zlib.decompress(data[start:])
    if outdir is None:
        outdir = fp.with_suffix("")
    outdir.mkdir(exist_ok=True, parents=True)
    png_magic = b"\x89PNG\r\n\x1a\n"
    png_end = b"IEND"
    positions = [m.start() for m in re.finditer(re.escape(png_magic), raw)]
    print(f"PNG found: {len(positions)}")
    for i, pos in enumerate(positions, 1):
        end_pos = raw.find(png_end, pos)
        if end_pos == -1:
            continue
        end_pos += len(png_end) + 4  # IEND+CRC
        chunk = raw[pos:end_pos]
        fname = outdir / (outfile % i)
        fname.write_bytes(chunk)
        print(f"{fname} ({len(chunk)/1024:,g} kiB)")


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract PNG pages from NotateIt .nat files")
    parser.add_argument("file", type=Path, help="Input .nat file")
    parser.add_argument("-f", "--force", action="store_true", help="Force processing")
    parser.add_argument("-o", "--outdir", help="Output directory")
    parser.add_argument(
        "-p",
        "--page-filename",
        help="Output page filename pattern, e.g. 'page_%%02d.png'",
        default="page_%02d.png",
    )
    args = parser.parse_args()
    extract_nat(
        args.file, force=args.force, outdir=args.outdir, outfile=args.page_filename
    )
