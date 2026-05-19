import os
import sys
import json

# Ensure repo root is on sys.path for system_fixer package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system_fixer.pipeline import run_pipeline

DASHBOARD_DATA_JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.js")


def regenerate_dashboard():
    """
    Runs the full analysis pipeline and writes updated findings
    to dashboard/data.js as a JS-consumable window.FINDINGS assignment.
    """
    findings = run_pipeline()

    # Build dashboard payload
    dashboard_findings = []
    for f in findings:
        dashboard_findings.append({
            "severity": f.get("severity", "UNRATED"),
            "title": f.get("title", "Untitled"),
            "target": f.get("target", ""),
            "program": f.get("program", "Unknown"),
            "engine": f.get("engine", ""),
            "money_score": f.get("money_score", 0),
            "date": f.get("date", ""),
        })

    js_content = "window.FINDINGS = " + json.dumps(dashboard_findings, indent=2) + ";"

    with open(DASHBOARD_DATA_JS, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"[regenerator] Dashboard updated: {len(dashboard_findings)} findings written to {DASHBOARD_DATA_JS}")
    return dashboard_findings


if __name__ == "__main__":
    regenerate_dashboard()
