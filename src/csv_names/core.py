"""Core reading and formatting logic for :mod:`csv_names`."""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Iterator, List, Mapping, Union

__all__ = [
    "Name",
    "CsvNamesError",
    "MissingColumnError",
    "iter_names",
    "read_names",
    "format_names",
    "DEFAULT_FIRST_COLUMN",
    "DEFAULT_LAST_COLUMN",
    "DEFAULT_TEMPLATE",
]

#: Column read for the first name when none is given.
DEFAULT_FIRST_COLUMN = "first_name"
#: Column read for the last name when none is given.
DEFAULT_LAST_COLUMN = "last_name"
#: Template used by :meth:`Name.format` when none is given.
DEFAULT_TEMPLATE = "{full}"

#: Anything :func:`iter_names` accepts as a source.
Source = Union[str, "os.PathLike[str]", IO[str]]


class CsvNamesError(Exception):
    """Base class for every error raised by this package.

    Catch this if you want to handle all ``csv_names`` failures in one place.
    """


class MissingColumnError(CsvNamesError, KeyError):
    """Raised when the CSV header lacks a required column.

    Attributes:
        column: The column that was requested.
        available: The columns the CSV header actually contains.
    """

    def __init__(self, column: str, available: List[str]) -> None:
        self.column = column
        self.available = available
        super().__init__(
            f"column {column!r} not found in CSV header; "
            f"available columns: {', '.join(available) or '(none)'}"
        )

    def __str__(self) -> str:  # KeyError would otherwise repr() the message
        return str(self.args[0])


@dataclass(frozen=True)
class Name:
    """A single person's name read from one CSV row.

    Attributes:
        first: The first (given) name, stripped of surrounding whitespace.
        last: The last (family) name, stripped of surrounding whitespace.
        row: Every column of the source row, so callers can reach other
            fields (``email``, ``id``, ...) without re-reading the file.
            Excluded from equality and hashing.
    """

    first: str
    last: str
    row: Mapping[str, str] = field(default_factory=dict, compare=False, repr=False)

    @property
    def full(self) -> str:
        """``"First Last"``, collapsing gracefully if either part is empty."""
        return " ".join(part for part in (self.first, self.last) if part)

    def format(self, template: str = DEFAULT_TEMPLATE) -> str:
        """Render the name with a :meth:`str.format` template.

        Available fields are ``{first}``, ``{last}`` and ``{full}``, plus
        every column of the source row (e.g. ``{email}``).

        >>> Name("Ada", "Lovelace").format("{last}, {first}")
        'Lovelace, Ada'
        """
        return template.format(**{**self.row, "first": self.first, "last": self.last, "full": self.full})

    def __str__(self) -> str:
        return self.full


def iter_names(
    source: Source,
    *,
    first_column: str = DEFAULT_FIRST_COLUMN,
    last_column: str = DEFAULT_LAST_COLUMN,
    skip_blank: bool = True,
    encoding: str = "utf-8-sig",
) -> Iterator[Name]:
    """Lazily yield a :class:`Name` for each row of a CSV file.

    Rows are streamed, so this is safe to use on files that do not fit in
    memory.

    Args:
        source: A filesystem path, or an already-open text file object
            (including :class:`io.StringIO`). File objects are not closed.
        first_column: Header of the column holding first names.
        last_column: Header of the column holding last names.
        skip_blank: Skip rows where both name columns are empty.
        encoding: Encoding used when ``source`` is a path. The default,
            ``utf-8-sig``, transparently strips a leading byte-order mark
            as written by Excel.

    Yields:
        One :class:`Name` per data row, in file order.

    Raises:
        FileNotFoundError: If ``source`` is a path that does not exist.
        MissingColumnError: If either column is absent from the header.
    """
    if isinstance(source, (str, os.PathLike)):
        with open(Path(source), newline="", encoding=encoding) as f:
            yield from _iter_rows(f, first_column, last_column, skip_blank)
    else:
        yield from _iter_rows(source, first_column, last_column, skip_blank)


def read_names(source: Source, **kwargs: object) -> List[Name]:
    """Read every name into a list.

    Convenience wrapper around :func:`iter_names`; accepts the same
    arguments.
    """
    return list(iter_names(source, **kwargs))  # type: ignore[arg-type]


def format_names(source: Source, template: str = DEFAULT_TEMPLATE, **kwargs: object) -> List[str]:
    """Read every name and render it with ``template``.

    >>> import io
    >>> format_names(io.StringIO("first_name,last_name\\nAda,Lovelace\\n"))
    ['Ada Lovelace']
    """
    return [name.format(template) for name in iter_names(source, **kwargs)]  # type: ignore[arg-type]


def _iter_rows(f: IO[str], first_column: str, last_column: str, skip_blank: bool) -> Iterator[Name]:
    reader = csv.DictReader(f)
    header = reader.fieldnames or []
    for column in (first_column, last_column):
        if column not in header:
            raise MissingColumnError(column, list(header))

    for row in reader:
        first = (row.get(first_column) or "").strip()
        last = (row.get(last_column) or "").strip()
        if skip_blank and not first and not last:
            continue
        yield Name(first, last, row)


# Keep ``io`` imported for the doctest examples above.
_ = io
