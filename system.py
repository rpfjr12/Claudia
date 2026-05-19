import json
import subprocess
import os
from datetime import datetime

# === PATHS ===
PROGRAMS_FILE = "programs.json"
SCANNER_SCRIPT = "scanner/scan.py"
DASHBOARD_REGEN = "dashboard/regenerator.py"
DATA_DIR = "data"
REPORTS_DIR = "reports"


def load_programs():
    if not os.path.exists(PROGRAMS_FILE):
        print(f"[system] Warning: {PROGRAMS_FILE} not found. Run fetch_programs workflow first.")
        return []
    with open(PROGRAMS_FILE, "r") as f:
        data = json.load(f)
    return data.get("programs", [])


def run_scanner():
    print("[1] Running scanner...")
    subprocess.run(["python3", SCANNER_SCRIPT], check=True)


def run_analysis_pipeline():
    print("[2] Running analysis pipeline...")
    subprocess.run(["python3", "-m", "system_fixer.pipeline"], check=True)


def generate_reports():
    print("[3] Generating Markdown reports...")
    subprocess.run(["python3", "-c",
        "import sys; sys.path.insert(0,'.'); "
        "from system_fixer.report_generator_integration import run_report_generation; "
        "from system_fixer.output_writer import write_output; "
        "import json, os; "
        "findings = json.load(open('output/final_findings.json')) if os.path.exists('output/final_findings.json') else []; "
        "run_report_generation(findings)"
    ], check=True)


def update_dashboard():
    print("[4] Updating dashboard...")
    subprocess.run(["python3", DASHBOARD_REGEN], check=True)


def commit_results():
    print("[5] Committing results to GitHub...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Automated scan results {datetime.now()}"], check=False)
    subprocess.run(["git", "push"], check=False)


def main():
    print("=== Autonomous Bug Bounty System ===")

    programs = load_programs()
    print(f"Loaded {len(programs)} programs.")

    run_scanner()
    run_analysis_pipeline()
    generate_reports()
    update_dashboard()
    commit_results()

    print("=== System run complete ===")


if __name__ == "__main__":
    main()
