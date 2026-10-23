import io
import subprocess
import sys

import pytest

from csv_names import __version__
from csv_names.cli import main


@pytest.fixture
def people(tmp_path):
    p = tmp_path / "people.csv"
    p.write_text(
        "first_name,last_name,email\nAda,Lovelace,ada@example.com\n,,\nAlan,Turing,alan@example.com\n"
    )
    return p


def test_default_output(people, capsys):
    assert main([str(people)]) == 0
    assert capsys.readouterr().out == "Ada Lovelace\nAlan Turing\n"


def test_template(people, capsys):
    assert main([str(people), "-t", "{last}, {first} <{email}>"]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "Lovelace, Ada <ada@example.com>"


def test_keep_blank(people, capsys):
    assert main([str(people), "--keep-blank"]) == 0
    assert capsys.readouterr().out.splitlines() == ["Ada Lovelace", "", "Alan Turing"]


def test_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("first_name,last_name\nGrace,Hopper\n"))
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "Grace Hopper\n"


def test_missing_column(people, capsys):
    assert main([str(people), "--first-column", "given"]) == 1
    assert "column 'given' not found" in capsys.readouterr().err


def test_missing_file(capsys):
    assert main(["nope.csv"]) == 1
    assert "csv-names: error:" in capsys.readouterr().err


def test_unknown_template_field(people, capsys):
    assert main([str(people), "-t", "{phone}"]) == 1
    assert "unknown template field 'phone'" in capsys.readouterr().err


def test_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_python_dash_m(people):
    result = subprocess.run(
        [sys.executable, "-m", "csv_names", str(people)], capture_output=True, text=True, check=True
    )
    assert result.stdout.splitlines() == ["Ada Lovelace", "Alan Turing"]


def test_decode_error(tmp_path, capsys):
    p = tmp_path / "bad.csv"
    p.write_bytes(b"first_name,last_name\n\xff\xfe,x\n")
    assert main([str(p)]) == 1
    assert "csv-names: error:" in capsys.readouterr().err


def test_broken_pipe_exits_cleanly(tmp_path):
    p = tmp_path / "many.csv"
    p.write_text("first_name,last_name\n" + "Ada,Lovelace\n" * 100_000)
    proc = subprocess.Popen(
        [sys.executable, "-m", "csv_names", str(p)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert proc.stdout is not None
    proc.stdout.readline()
    proc.stdout.close()
    _, err = proc.communicate()
    assert proc.returncode == 0
    assert b"BrokenPipe" not in err
