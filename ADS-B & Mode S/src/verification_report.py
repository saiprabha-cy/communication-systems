from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys


REPORT_PATH = Path("reports/verification_report.md")


def run_unit_tests() -> tuple[bool, str]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []

    records = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def main() -> None:
    test_passed, test_output = run_unit_tests()
    records = load_jsonl(Path("reports/decoded_frames.jsonl"))

    total = len(records)
    crc_valid = sum(bool(item.get("crc_valid")) for item in records)
    crc_failed = sum(
        item.get("status") == "crc_failed" for item in records
    )
    truncated = sum(
        item.get("error") == "Truncated payload" for item in records
    )

    status = "PASS" if test_passed else "FAIL"
    now = datetime.now(timezone.utc).isoformat()

    report = f"""# ADS-B / Mode S Decoder Verification Report

- Generated UTC: {now}
- Unit test result: **{status}**
- Candidate records: {total}
- CRC-valid DF17 records: {crc_valid}
- CRC-failed records: {crc_failed}
- Truncated payloads: {truncated}

## Scope

This report summarizes the local software test run. Synthetic IQ samples
are not real aircraft observations. A candidate count is not a count of
unique aircraft, and a CRC result does not independently establish aircraft
identity or field correctness.

## Test output

```text
DIL2