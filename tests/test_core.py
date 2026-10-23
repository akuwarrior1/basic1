import io
from pathlib import Path

import pytest

import csv_names
from csv_names import CsvNamesError, MissingColumnError, Name, format_names, iter_names, read_names

EXAMPLE_CSV = Path(__file__).parent.parent / "examples" / "MOCK_DATA.csv"


def csv(text: str) -> io.StringIO:
    return io.StringIO(text)


def test_reads_example_file_from_path():
    names = read_names(EXAMPLE_CSV)
    assert len(names) == 1000
    assert names[0] == Name("Maurita", "Lockhart")
    assert names[0].row["email"] == "mlockhart0@un.org"


def test_accepts_str_path(tmp_path):
    p = tmp_path / "people.csv"
    p.write_text("first_name,last_name\nAda,Lovelace\n", encoding="utf-8")
    assert read_names(str(p)) == [Name("Ada", "Lovelace")]


def test_strips_utf8_bom(tmp_path):
    p = tmp_path / "excel.csv"
    p.write_bytes("﻿first_name,last_name\nAda,Lovelace\n".encode())
    assert read_names(p) == [Name("Ada", "Lovelace")]


def test_file_object_is_not_closed():
    f = csv("first_name,last_name\nAda,Lovelace\n")
    list(iter_names(f))
    assert not f.closed


def test_is_lazy():
    it = iter_names(csv("first_name,last_name\nA,B\nC,D\n"))
    assert next(it) == Name("A", "B")


def test_strips_whitespace():
    assert read_names(csv("first_name,last_name\n  Ada , Lovelace \n")) == [Name("Ada", "Lovelace")]


def test_skip_blank_rows_by_default():
    data = "first_name,last_name\nAda,Lovelace\n,\nAlan,Turing\n"
    assert [n.full for n in read_names(csv(data))] == ["Ada Lovelace", "Alan Turing"]
    assert len(read_names(csv(data), skip_blank=False)) == 3


def test_custom_columns():
    data = "given,family\nGrace,Hopper\n"
    assert read_names(csv(data), first_column="given", last_column="family") == [Name("Grace", "Hopper")]


def test_missing_column_error():
    with pytest.raises(MissingColumnError) as exc_info:
        read_names(csv("given,family\nGrace,Hopper\n"))
    err = exc_info.value
    assert err.column == "first_name"
    assert err.available == ["given", "family"]
    assert "available columns: given, family" in str(err)
    assert isinstance(err, CsvNamesError)
    assert isinstance(err, KeyError)


def test_missing_column_on_empty_input():
    with pytest.raises(MissingColumnError, match=r"\(none\)"):
        read_names(csv(""))


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        read_names("does-not-exist.csv")


@pytest.mark.parametrize(
    ("first", "last", "full"),
    [("Ada", "Lovelace", "Ada Lovelace"), ("Cher", "", "Cher"), ("", "Banksy", "Banksy"), ("", "", "")],
)
def test_full(first, last, full):
    assert Name(first, last).full == full
    assert str(Name(first, last)) == full


def test_format_with_row_fields():
    (name,) = read_names(csv("first_name,last_name,email\nAda,Lovelace,ada@example.com\n"))
    assert name.format("{last}, {first} <{email}>") == "Lovelace, Ada <ada@example.com>"


def test_format_unknown_field_raises_keyerror():
    with pytest.raises(KeyError):
        Name("Ada", "Lovelace").format("{nope}")


def test_equality_ignores_row():
    assert Name("Ada", "Lovelace", {"id": "1"}) == Name("Ada", "Lovelace", {"id": "2"})
    assert len({Name("Ada", "Lovelace", {"id": "1"}), Name("Ada", "Lovelace")}) == 1


def test_format_names():
    data = "first_name,last_name\nAda,Lovelace\nAlan,Turing\n"
    assert format_names(csv(data), "{first[0]}. {last}") == ["A. Lovelace", "A. Turing"]


def test_version_is_exposed():
    assert isinstance(csv_names.__version__, str)


def test_default_template_has_no_stray_spaces():
    assert Name("Cher", "").format() == "Cher"
    assert Name("", "").format() == ""
