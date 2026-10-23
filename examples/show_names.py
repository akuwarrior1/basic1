"""Print every name in MOCK_DATA.csv using the csv_names library.

Run from the repository root after ``pip install -e .``::

    python examples/show_names.py
"""

from pathlib import Path

from csv_names import iter_names

CSV_PATH = Path(__file__).parent / "MOCK_DATA.csv"


def main() -> None:
    for name in iter_names(CSV_PATH):
        print(name)


if __name__ == "__main__":
    main()
