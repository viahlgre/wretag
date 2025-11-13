# Wretag

`wretag` is a minimal CLI utility for retagging Python wheel files with a custom
[PEP 440](https://peps.python.org/pep-0440/#local-version-identifiers) local version identifier.
This can be useful for marking locally built packages during development or in CI/CD pipelines.

## Features
- Adds or modifies a `+<tag>` to the existing version in `.whl` files
- Supports retagging multiple wheels with the same tag at once 
- Optionally deletes the original wheels (`-d` or `--delete-original`)
- Quiet mode prints only the new wheel path(s) (`-q` or `--quiet`)

## Installation

git clone https://github.com/viahlgre/wretag.git
cd wretag
pip install .

## Usage
wretag [-d] [-q] <tag> <wheel1> [<wheel2> ...]

## Example
wretag -q -d devtag dist/*.whl

**Output:**
dist/mypackage-1.0.0+devtag-py3-none-any.whl

## License
[MIT License](LICENSE)
