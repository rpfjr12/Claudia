# scanner/scan.py
# High-value automated scanner for normalized targets.

import json
import os
import sys
from datetime import datetime

# Ensure the repo root is on sys.path so engine imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# HIGH-VALUE ENGINES ONLY - import using their actual public function names
import idor_engine
import ssrf_engine
import auth_bypass_engine
import rate_limit_engine
import sensitive_data_engine
import jwt_engine

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "scan_results.json")


def scan_target(url):
    """Run only payout-worthy checks on a single target."""
    findings = []

    # Each engine exposes a `scan(target, http_client)` or `analyze(target, records)`.
    # We call them with a None http_client / empty records; engines return [] when
    # they have nothing actionable, which is safe for a static/offline run.
    engine_calls = [
        (ssrf_engine,          lambda: ssrf_engine.scan(url, None)),
        (auth_bypass_engine,   lambda: auth_bypass_engine.scan(url, None)),
        (rate_limit_engine,    lambda: rate_limit_engine.scan(url, None)),
        (sensitive_data_engine, lambda: sensitive_data_engine.scan(url, None)),
        (jwt_engine,           lambda: jwt_engine.scan(url, None)),
        (idor_engine,          lambda: idor_engine.analyze(url, [])),
    ]

    for engine_mod, call in engine_calls:
        try:
            results = call()
            if results:
                for r in results:
                    r.setdefault("engine", engine_mod.__name__)
                findings.extend(results)
        except Exception as e:
            print(f"[scanner] Engine {engine_mod.__name__} error on {url}: {e}")

    return findings


def save_findings(program, findings):
    """Save findings for a program into a clean JSON file."""
    if not findings:
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date = datetime.utcnow().strftime("%Y-%m-%d")

    program_id = program.get("id", program.get("name", "unknown")).replace(" ", "_")
    filename = f"{program_id}-{date}.json"
    path = os.path.join(OUTPUT_DIR, filename)

    output = []
    for f in findings:
        output.append({
            "severity": f.get("severity", "HIGH"),
            "title": f.get("title", "Unknown finding"),
            "target": f.get("target"),
            "program": program.get("name", "Unknown Program"),
            "date": date,
            "details": f.get("details", {}),
        })

    with open(path, "w") as fp:
        json.dump(output, fp, indent=4)

    print(f"[scanner] Saved: {path}")


def scan_program(program):
    """Scan all normalized targets for a single program."""
    targets = program.get("normalized_scope", [])
    all_findings = []

    for target in targets:
        print(f"[scanner] Scanning target: {target}")
        findings = scan_target(target)

        for f in findings:
            f["target"] = target

        all_findings.extend(findings)

    return all_findings


def main():
    """Entry point: load programs.json, scan each program, write scan_results.json."""
    # Paths relative to repo root regardless of cwd
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    programs_file = os.path.join(root, "programs.json")
    output_path = os.path.join(root, OUTPUT_FILE)

    os.makedirs(os.path.join(root, OUTPUT_DIR), exist_ok=True)

    if not os.path.exists(programs_file):
        print(f"[scanner] No programs.json found at {programs_file}, writing empty scan_results.json")
        scan_results = []
    else:
        with open(programs_file, "r") as f:
            data = json.load(f)
        programs = data.get("programs", [])
        print(f"[scanner] Loaded {len(programs)} programs")

        scan_results = []
        for program in programs:
            if isinstance(program, str):
                program = {"name": program, "normalized_scope": [program]}
            findings = scan_program(program)
            scan_results.extend(findings)

    with open(output_path, "w") as f:
        json.dump(scan_results, f, indent=4)

    print(f"[scanner] Wrote {len(scan_results)} findings to {output_path}")


if __name__ == "__main__":
    main()
