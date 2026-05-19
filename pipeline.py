# pipeline.py
# Full autonomous pipeline: fetch -> normalize -> evaluate -> scan -> filter -> report

from system_fixer.program_fetcher import fetch_all_programs
from eligibility_engine import eligible
from findings_normalizer import normalize_program
from system_fixer.money_filter import apply_money_filter
from system_fixer.report_generator import generate_reports


def scan_program(program):
    """
    Placeholder for your actual scanning logic.
    This function should return a list of findings.
    """
    # TODO: integrate your scanner here
    return []


def run_pipeline():
    print("[pipeline] Fetching programs...")
    programs = fetch_all_programs()

    print(f"[pipeline] {len(programs)} programs fetched.")
    print("[pipeline] Normalizing scope...")

    normalized = [normalize_program(p) if isinstance(p, dict) else {"name": p, "normalized_scope": [p]} for p in programs]

    print("[pipeline] Evaluating eligibility...")
    eligible_programs = [p for p in normalized if eligible(p)]

    print(f"[pipeline] {len(eligible_programs)} programs eligible for scanning.")

    all_money_findings = []

    for program in eligible_programs:
        name = program.get("name", "Unknown Program")
        print(f"\n[pipeline] Scanning: {name}")

        findings = scan_program(program)

        if not findings:
            print(f"[pipeline] No findings for {name}.")
            continue

        print(f"[pipeline] {len(findings)} findings detected. Applying money filter...")

        money_findings = apply_money_filter(findings)

        if not money_findings:
            print(f"[pipeline] No payout-worthy findings for {name}.")
            continue

        print(f"[pipeline] {len(money_findings)} payout-worthy findings. Generating report...")
        all_money_findings.extend(money_findings)

    if all_money_findings:
        generate_reports(all_money_findings)

    print("\n[pipeline] Completed.")
