# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-23

### Added
- `iter_names`, `read_names` and `format_names` for reading names from CSV paths or file objects.
- `Name` dataclass with `first`, `last`, `full`, `row` and `format()`.
- `CsvNamesError` and `MissingColumnError` exceptions.
- `csv-names` command-line tool (also runnable as `python -m csv_names`).
- Type information (`py.typed`).

[Unreleased]: https://github.com/akuwarrior1/basic1/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/akuwarrior1/basic1/releases/tag/v0.1.0
