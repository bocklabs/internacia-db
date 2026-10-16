#!/usr/bin/env python3
"""Shared PR/release gate for high-priority data-quality findings."""
import argparse
import json
from pathlib import Path


def high_priority_issues(report: Path) -> list[dict]:
    issues = [json.loads(line) for line in report.read_text().splitlines() if line.strip()]
    return [issue for issue in issues if issue.get("priority") in {"CRITICAL", "IMPORTANT"}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    issues = high_priority_issues(args.report)
    for issue in issues[:20]:
        print(f"[{issue['priority']}] {issue['issue_type']} {issue.get('file_path')}")
    print(f"{len(issues)} CRITICAL/IMPORTANT quality issue(s)")
    raise SystemExit(1 if issues else 0)


if __name__ == "__main__":
    main()
