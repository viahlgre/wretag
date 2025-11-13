import argparse
import tempfile
import shutil
import subprocess
import pathlib
import re
import sys

def retag_wheel(wheel_path: str, local_tag: str, delete: bool = False, quiet: bool = False) -> pathlib.Path:
    wheel = pathlib.Path(wheel_path).resolve()
    if not wheel.is_file() or not wheel.name.endswith(".whl"):
        raise ValueError(f"Invalid wheel path: {wheel_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        stdout_redir = subprocess.DEVNULL if quiet else None

        subprocess.run(
            [sys.executable, "-m", "wheel", "unpack", str(wheel), "-d", str(tmpdir)],
            check=True,
            stdout = stdout_redir
        )

        wheel_dir = next(tmpdir.iterdir())
        dist_info = next(p for p in wheel_dir.iterdir() if p.name.endswith(".dist-info"))

        metadata = dist_info / "METADATA"
        content = metadata.read_text()
        version_match = re.search(r"^Version: (.+)$", content, re.MULTILINE)
        if not version_match:
            raise ValueError("Version not found in METADATA")

        old_version = version_match.group(1)
        base_version = old_version.split("+")[0]
        new_version = f"{base_version}+{local_tag}"

        content = re.sub(r"^Version: .+$", f"Version: {new_version}", content, flags=re.MULTILINE)
        metadata.write_text(content)

        # Rename dist-info dir
        new_dist_info = dist_info.parent / dist_info.name.replace(old_version, new_version)
        dist_info.rename(new_dist_info)

        subprocess.run(
            [sys.executable, "-m", "wheel", "pack", str(wheel_dir), "-d", str(wheel.parent)],
            check=True,
            stdout = stdout_redir
        )

        new_wheel = next(wheel.parent.glob(f"*{new_version}*.whl"))

        if delete:
            wheel.unlink()

        if not quiet:
            print(f"Retagged: {new_wheel}")

        return new_wheel

def main():
    parser = argparse.ArgumentParser(
        description="Add a local version tag to one or more .whl files."
    )
    parser.add_argument("tag", help="Local version tag to append (after +)")
    parser.add_argument("wheels", nargs="+", help="Path(s) to .whl file(s)")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete the original wheel files after retagging")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output (prints only the new wheel paths)")
    args = parser.parse_args()

    success = True
    for wheel in args.wheels:
        try:
            new_path = retag_wheel(wheel, args.tag, args.delete, args.quiet)
            if args.quiet:
                print(new_path)
        except Exception as e:
            success = False
            if not args.quiet:
                print(f"Failed to retag {wheel}: {e}", file=sys.stderr)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

