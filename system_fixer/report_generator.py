import os
import json
from datetime import datetime

OUTPUT_DIR = "reports"


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def generate_markdown_report(finding):
    title = finding.get("title", "Untitled Finding")
    program = finding.get("program", "Unknown Program")
    target = finding.get("target", "Unknown Target")
    severity = finding.get("severity", "Unrated")
    engine = finding.get("engine", "unknown_engine")
    fingerprint = finding.get("fingerprint", "no-fingerprint")
    money_score = finding.get("money_score", 0)

    description = finding.get("description", "No description provided.")
    reproduction = finding.get("reproduction_steps", "No reproduction steps provided.")
    impact = finding.get("impact", "No impact information provided.")
    evidence = finding.get("evidence", "No evidence provided.")
    fix = finding.get("fix", "No fix recommendation provided.")

    md = f"""# {title}

**Program:** {program}  
**Target:** {target}  
**Severity:** {severity}  
**Engine:** {engine}  
**Money Score:** {money_score}  
**Fingerprint:** `{fingerprint}`  
**Generated:** {datetime.utcnow().isoformat()} UTC

---

## Summary
{description}

---

## Steps to Reproduce
{reproduction}

---

## Impact
{impact}

---

## Evidence
{evidence}

---

## Recommended Fix
{fix}
"""
    return md


def write_report(finding):
    ensure_output_dir()

    program = finding.get("program", "Unknown_Program").replace(" ", "_")
    date = datetime.utcnow().strftime("%Y-%m-%d")
    title_slug = finding.get("title", "untitled").replace(" ", "_").replace("/", "_")[:50]
    filename = f"{program}-{date}-{title_slug}.md"
    path = os.path.join(OUTPUT_DIR, filename)

    content = generate_markdown_report(finding)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[report_generator] Wrote report: {path}")
    except Exception as e:
        print(f"[report_generator] Error writing report {path}: {e}")

    return path


def generate_reports(findings):
    ensure_output_dir()
    paths = []
    for finding in findings:
        path = write_report(finding)
        paths.append(path)
    print(f"[report_generator] Generated {len(paths)} reports in {OUTPUT_DIR}/")
    return paths
