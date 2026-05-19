from system_fixer.severity_scoring import score_severity
from system_fixer.intelligence_enricher import enrich_findings
from system_fixer.rules_engine import apply_rules_to_all

SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

# Minimum severity thresholds per program (default: MEDIUM)
DEFAULT_MIN_SEVERITY = "MEDIUM"


def meets_severity_threshold(program_key, severity, min_severity=None):
    """
    Returns True if the given severity meets or exceeds the threshold
    for the specified program.
    """
    threshold = min_severity or DEFAULT_MIN_SEVERITY
    sev_val = SEVERITY_ORDER.get(severity.upper(), 0)
    threshold_val = SEVERITY_ORDER.get(threshold.upper(), 2)
    return sev_val >= threshold_val


def run_severity_engine(findings):
    print("[severity_engine] Starting severity engine...")

    # Step 1 - Normalize severity labels
    findings = score_severity(findings)
    print("[severity_engine] Severity normalized")

    # Step 2 - Add intelligence metadata
    findings = enrich_findings(findings)
    print("[severity_engine] Intelligence enriched")

    # Step 3 - Apply program-specific rules
    findings = apply_rules_to_all(findings)
    print("[severity_engine] Program rules applied")

    print("[severity_engine] Severity engine complete")
    return findings
