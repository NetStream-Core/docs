import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
FENCE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)


def diagrams():
    for path in sorted(ROOT.rglob("*.mmd")):
        yield path, path.read_text()
    for path in sorted(ROOT.rglob("*.md")):
        for index, match in enumerate(FENCE.finditer(path.read_text())):
            yield f"{path} (block {index + 1})", match.group(1)


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for label, source in diagrams():
            input_path = pathlib.Path(tmp) / "diagram.mmd"
            output_path = pathlib.Path(tmp) / "diagram.svg"
            input_path.write_text(source)
            result = subprocess.run(
                [
                    "npx", "-y", "@mermaid-js/mermaid-cli",
                    "-i", str(input_path),
                    "-o", str(output_path),
                    "-p", str(ROOT / "tools" / "puppeteer-config.json"),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                failures.append((label, result.stderr))
            else:
                print(f"OK   {label}")

    for label, stderr in failures:
        print(f"FAIL {label}")
        print(stderr, file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
