# csv-names

[![CI](https://github.com/akuwarrior1/basic1/actions/workflows/ci.yml/badge.svg)](https://github.com/akuwarrior1/basic1/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/csv-names.svg)](https://pypi.org/project/csv-names/)
[![Python versions](https://img.shields.io/pypi/pyversions/csv-names.svg)](https://pypi.org/project/csv-names/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Read and format people's names from CSV files. `csv-names` is a small, fully typed Python library and command-line tool with **no dependencies**.

```python
>>> from csv_names import format_names
>>> format_names("people.csv", "{last}, {first} <{email}>")
['Lockhart, Maurita <mlockhart0@un.org>', 'Lachaize, Blinny <blachaize1@dailymail.co.uk>', ...]
```

```console
$ csv-names people.csv --template "{first[0]}. {last}"
M. Lockhart
B. Lachaize
```

## Contents

- [Features](#features)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Library guide](#library-guide)
- [Command-line usage](#command-line-usage)
- [API reference](#api-reference)
- [Error handling](#error-handling)
- [Recipes](#recipes)
- [FAQ](#faq)
- [Development](#development)
- [License](#license)

## Features

- **Streaming.** `iter_names` reads one row at a time, so files larger than memory work fine.
- **Flexible input.** Accepts a `str` path, a `pathlib.Path`, or any open text file object, including `io.StringIO` and `sys.stdin`.
- **Templates.** Format names with ordinary `str.format` syntax. Every CSV column is available as a field, so `{email}` and `{id}` work.
- **Excel-friendly.** The UTF-8 byte-order mark that Excel writes is removed automatically.
- **Clear errors.** A missing column raises `MissingColumnError`, and the message lists the columns the file actually has.
- **Typed.** Ships `py.typed` and passes `mypy --strict`.
- **No dependencies.** Uses only the standard library and supports Python 3.10 and newer.

## Installation

From PyPI:

```bash
pip install csv-names
```

Directly from GitHub, before a PyPI release or to get the latest commit:

```bash
pip install "git+https://github.com/akuwarrior1/basic1.git"
# a specific tagged release:
pip install "git+https://github.com/akuwarrior1/basic1.git@v0.1.0"
```

With other package managers:

```bash
uv add csv-names
poetry add csv-names
pipx install csv-names        # installs the CLI only, isolated from your other packages
```

To pin it in `requirements.txt`:

```text
csv-names>=0.1,<0.2
```

## Quick start

Given a file `people.csv`:

```csv
id,first_name,last_name,email
1,Ada,Lovelace,ada@example.com
2,Alan,Turing,alan@example.com
```

```python
from csv_names import iter_names

for name in iter_names("people.csv"):
    print(name)  # Ada Lovelace
    print(name.first, name.last)  # Ada Lovelace
    print(name.row["email"])  # ada@example.com
    print(name.format("{last}, {first}"))  # Lovelace, Ada
```

## Library guide

### Choosing a reading function

| Function | Returns | Use when |
|---|---|---|
| `iter_names(source, ...)` | `Iterator[Name]` | The file is large, or you want to process rows as they are read |
| `read_names(source, ...)` | `List[Name]` | You want every name in a list |
| `format_names(source, template, ...)` | `List[str]` | You only need the formatted strings |

All three take the same keyword arguments: `first_column`, `last_column`, `skip_blank` and `encoding`.

### Sources

```python
from pathlib import Path
import io, sys
from csv_names import read_names

read_names("people.csv")  # str path
read_names(Path("data") / "people.csv")  # pathlib.Path
read_names(io.StringIO("first_name,last_name\nAda,Lovelace\n"))  # in-memory text
read_names(sys.stdin)  # a stream

with open("people.csv", newline="", encoding="latin-1") as f:
    read_names(f)  # a file object you opened yourself
```

When you pass a file object, `csv-names` does **not** close it, so closing it is up to you. When you pass a path, the library opens and closes the file itself.

### Custom column names

The defaults are `first_name` and `last_name`. If your file uses different headers, pass them in:

```python
read_names("staff.csv", first_column="GivenName", last_column="Surname")
```

### Blank rows

Rows where **both** name columns are empty are skipped by default. Pass `skip_blank=False` to keep them:

```python
read_names("people.csv", skip_blank=False)
```

### Encodings

Paths are opened with `utf-8-sig` by default, which reads plain UTF-8 and also removes Excel's byte-order mark. You can pass any other Python codec:

```python
read_names("legacy.csv", encoding="cp1252")
```

The `encoding` argument only applies when `source` is a path. If you pass a file object, set the encoding when you call `open()`.

### The `Name` object

`Name` is a frozen (immutable) dataclass:

```python
from csv_names import Name

n = Name("Ada", "Lovelace", row={"email": "ada@example.com"})
n.first  # 'Ada'
n.last  # 'Lovelace'
n.full  # 'Ada Lovelace'
str(n)  # 'Ada Lovelace'
n.row  # {'email': 'ada@example.com'}  (every column from the CSV row)
n.format("{first} <{email}>")  # 'Ada <ada@example.com>'
```

- Leading and trailing whitespace is removed from `first` and `last`.
- `full` collapses cleanly when one part is empty: `Name("Cher", "").full == "Cher"`.
- Equality and hashing use only `first` and `last`; `row` is ignored. Two rows with the same name compare equal, so `set(read_names(...))` removes duplicate names.

### Templates

Templates use [`str.format`](https://docs.python.org/3/library/string.html#format-string-syntax) syntax. The available fields are:

| Field | Value |
|---|---|
| `{first}` | First name, stripped |
| `{last}` | Last name, stripped |
| `{full}` | `"first last"`, without stray spaces |
| `{<any column>}` | The raw value of that CSV column, e.g. `{email}` or `{id}` |

Format specs and indexing also work:

```python
n.format("{first[0]}. {last}")  # 'A. Lovelace'
n.format("{last:>15}|")  # '       Lovelace|'
n.format("{full!r}")  # "'Ada Lovelace'"
```

If a column header is not a valid Python identifier (for example `"E-mail"` or `"first name"`), it cannot be used as a template field. Read it from `name.row["E-mail"]` instead.

## Command-line usage

Installing the package adds a `csv-names` command. You can also run it as `python -m csv_names`.

```text
usage: csv-names [-h] [-t TEMPLATE] [--first-column FIRST_COLUMN] [--last-column LAST_COLUMN]
                 [--keep-blank] [--encoding ENCODING] [-V]
                 file

Print one formatted name per row of a CSV file.

positional arguments:
  file                  path to a CSV file, or '-' to read from stdin

options:
  -h, --help            show this help message and exit
  -t, --template TEMPLATE
                        str.format template; fields: {first} {last} {full} plus any CSV column
                        (default: '{full}')
  --first-column FIRST_COLUMN
                        header of the first-name column (default: first_name)
  --last-column LAST_COLUMN
                        header of the last-name column (default: last_name)
  --keep-blank          also print rows where both name columns are empty
  --encoding ENCODING   file encoding (default: utf-8-sig)
  -V, --version         show program's version number and exit

Example: csv-names people.csv --template "{last}, {first} <{email}>"
```

Examples:

```bash
csv-names people.csv
csv-names people.csv -t "{last}, {first} <{email}>"
csv-names staff.csv --first-column GivenName --last-column Surname
cat people.csv | csv-names -
csv-names people.csv | sort | uniq -d     # find duplicate names
```

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Success, including when output is piped into a command such as `head` that closes early |
| `1` | Error: missing file, missing column, unknown template field, decode error, or malformed CSV. A message is printed to stderr |
| `2` | Invalid command-line arguments (reported by argparse) |

## API reference

Everything listed here can be imported from the top-level `csv_names` package.

### `iter_names(source, *, first_column="first_name", last_column="last_name", skip_blank=True, encoding="utf-8-sig") -> Iterator[Name]`

Lazily yields one `Name` per data row, in file order.

- **source**: a `str` path, an `os.PathLike`, or an open text file object.
- **first_column** / **last_column**: the header names to read.
- **skip_blank**: skip rows where both name columns are empty.
- **encoding**: the codec used when `source` is a path.
- **Raises**: `FileNotFoundError`, `MissingColumnError`, `UnicodeDecodeError`, `csv.Error`.

Errors are raised when iteration starts, not when `iter_names()` is called, because it is a generator.

### `read_names(source, **kwargs) -> List[Name]`

Same as `list(iter_names(source, **kwargs))`.

### `format_names(source, template="{full}", **kwargs) -> List[str]`

Same as `[n.format(template) for n in iter_names(source, **kwargs)]`.

### `class Name(first: str, last: str, row: Mapping[str, str] = {})`

Frozen dataclass.

- **`.full -> str`**: the first and last names joined with a space; empty parts are left out.
- **`.format(template="{full}") -> str`**: renders the template. Raises `KeyError` for an unknown field.
- **`str(name)`**: the same as `.full`.

### Exceptions

- **`CsvNamesError(Exception)`**: the base class for every error this library raises.
- **`MissingColumnError(CsvNamesError, KeyError)`**: has the attributes `.column` (the column that was requested) and `.available` (a list of the columns that exist).

### Constants

`DEFAULT_FIRST_COLUMN = "first_name"`, `DEFAULT_LAST_COLUMN = "last_name"`, `DEFAULT_TEMPLATE = "{full}"`, `__version__`.

## Error handling

```python
from csv_names import read_names, MissingColumnError, CsvNamesError

try:
    names = read_names(path)
except MissingColumnError as e:
    print(f"Expected column {e.column!r}; file has {e.available}")
except FileNotFoundError:
    print("No such file")
except CsvNamesError:
    print("Some other csv-names problem")
```

`MissingColumnError` also inherits from `KeyError`, so existing `except KeyError` handlers still catch it.

## Recipes

**Use with pandas**

```python
import pandas as pd
from csv_names import iter_names

df = pd.DataFrame({"name": n.full, "email": n.row["email"]} for n in iter_names("people.csv"))
```

**Remove duplicate names, keeping file order**

```python
unique = list(dict.fromkeys(read_names("people.csv")))
```

**Serve names from a web API (FastAPI)**

```python
from fastapi import FastAPI, UploadFile
import io
from csv_names import format_names

app = FastAPI()


@app.post("/names")
async def names(file: UploadFile):
    text = io.StringIO((await file.read()).decode("utf-8-sig"))
    return format_names(text, "{full}")
```

**Write formatted names to a new CSV**

```python
import csv
from csv_names import iter_names

with open("out.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["display_name", "email"])
    for n in iter_names("people.csv"):
        w.writerow([n.format("{last}, {first}"), n.row.get("email", "")])
```

A runnable example is in [`examples/show_names.py`](examples/show_names.py), with 1,000 rows of sample data in [`examples/MOCK_DATA.csv`](examples/MOCK_DATA.csv).

## FAQ

**Does it handle quoted fields, embedded commas, or newlines in a field?**
Yes. Parsing is done by Python's standard `csv` module.

**What about tab-separated or semicolon-separated files?**
The library currently expects comma-delimited files. If you need other delimiters, please open an issue.

**Is it thread-safe?**
Each call to `iter_names` uses its own reader, and `Name` is immutable, so separate calls can run in separate threads. Do not share one open file object between threads.

**Which Python versions are supported?**
CPython 3.10 through 3.13. Every version is tested in CI on Linux, macOS and Windows.

## Development

```bash
git clone https://github.com/akuwarrior1/basic1.git
cd basic1
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest --cov=csv_names     # tests, including the doctests in the source
mypy                       # strict type check
ruff check . && ruff format --check .
python -m build            # build the sdist and wheel into dist/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and [CHANGELOG.md](CHANGELOG.md) for the release history.

## License

[MIT](LICENSE) © Akashdeep Gopinath
