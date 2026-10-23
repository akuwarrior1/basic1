"""Command-line interface: ``csv-names FILE [options]``."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import List, Optional

from . import __version__
from .core import DEFAULT_FIRST_COLUMN, DEFAULT_LAST_COLUMN, DEFAULT_TEMPLATE, CsvNamesError, iter_names

__all__ = ["main", "build_parser"]


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser used by :func:`main`."""
    parser = argparse.ArgumentParser(
        prog="csv-names",
        description="Print one formatted name per row of a CSV file.",
        epilog='Example: csv-names people.csv --template "{last}, {first} <{email}>"',
    )
    parser.add_argument("file", help="path to a CSV file, or '-' to read from stdin")
    parser.add_argument(
        "-t",
        "--template",
        default=DEFAULT_TEMPLATE,
        help="str.format template; fields: {first} {last} {full} plus any CSV column "
        f"(default: {DEFAULT_TEMPLATE!r})",
    )
    parser.add_argument(
        "--first-column",
        default=DEFAULT_FIRST_COLUMN,
        help=f"header of the first-name column (default: {DEFAULT_FIRST_COLUMN})",
    )
    parser.add_argument(
        "--last-column",
        default=DEFAULT_LAST_COLUMN,
        help=f"header of the last-name column (default: {DEFAULT_LAST_COLUMN})",
    )
    parser.add_argument(
        "--keep-blank", action="store_true", help="also print rows where both name columns are empty"
    )
    parser.add_argument("--encoding", default="utf-8-sig", help="file encoding (default: utf-8-sig)")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CLI and return a process exit code (0 on success, 1 on error)."""
    args = build_parser().parse_args(argv)
    source = sys.stdin if args.file == "-" else args.file
    try:
        for name in iter_names(
            source,
            first_column=args.first_column,
            last_column=args.last_column,
            skip_blank=not args.keep_blank,
            encoding=args.encoding,
        ):
            print(name.format(args.template))
    except BrokenPipeError:  # e.g. `csv-names big.csv | head`; must precede OSError
        # Point stdout at devnull so the interpreter's final flush doesn't raise again.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    except (CsvNamesError, OSError, UnicodeDecodeError, csv.Error) as exc:
        print(f"csv-names: error: {exc}", file=sys.stderr)
        return 1
    except KeyError as exc:
        print(f"csv-names: error: unknown template field {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
