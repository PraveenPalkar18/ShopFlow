import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    failures = []
    fixture_dirs = sorted(FIXTURES.glob("PR-*"))
    if len(fixture_dirs) != 12:
        failures.append(f"Expected 12 scenario directories, found {len(fixture_dirs)}")
    for fixture in fixture_dirs:
        scenario = fixture.name
        expected_files = (
            "README.md",
            "pr_description.md",
            "expected_results.json",
            "changes.patch",
            "test_expectations.md",
        )
        for filename in expected_files:
            path = fixture / filename
            if not path.is_file() or path.stat().st_size == 0:
                failures.append(f"{scenario}: missing or empty {filename}")
        expected_path = fixture / "expected_results.json"
        if not expected_path.is_file():
            continue
        try:
            data = json.loads(expected_path.read_text(encoding="utf-8"))
            for key in ("scenario_id", "labels", "risk", "affected_modules", "regression_tests"):
                if key not in data:
                    failures.append(f"{scenario}: expected_results.json missing {key}")
            branch = data.get("branch", "")
            if branch:
                git("show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
                if subprocess.run(
                    ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", "baseline", branch],
                    capture_output=True,
                ).returncode != 0:
                    failures.append(f"{scenario}: branch is not based on baseline")
                patch = (fixture / "changes.patch").read_text(encoding="utf-8")
                current_diff = subprocess.run(
                    ["git", "-C", str(ROOT), "diff", "--binary", "baseline", branch],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                if patch.strip() != current_diff.strip():
                    failures.append(f"{scenario}: changes.patch does not match its branch diff")
        except (json.JSONDecodeError, subprocess.CalledProcessError) as exc:
            failures.append(f"{scenario}: invalid JSON or missing Git branch ({exc})")
    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures))
        return 1
    print(f"Validated {len(fixture_dirs)} scenario fixtures and local branches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
