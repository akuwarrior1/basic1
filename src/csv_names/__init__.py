"""Read and format people's names from CSV files.

Quick start::

    >>> import io, csv_names
    >>> data = io.StringIO("first_name,last_name\\nAda,Lovelace\\n")
    >>> [str(n) for n in csv_names.iter_names(data)]
    ['Ada Lovelace']

See :func:`iter_names` for the full set of options.
"""

from .core import (
    DEFAULT_FIRST_COLUMN,
    DEFAULT_LAST_COLUMN,
    DEFAULT_TEMPLATE,
    CsvNamesError,
    MissingColumnError,
    Name,
    format_names,
    iter_names,
    read_names,
)

__version__ = "0.1.0"

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
    "__version__",
]
