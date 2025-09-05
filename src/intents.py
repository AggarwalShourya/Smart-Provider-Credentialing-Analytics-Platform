from typing import Dict, List, Pattern
import re

# Simple rule-based patterns for hackathon-level NLU
INTENT_PATTERNS: Dict[str, List[Pattern]] = {
    "expired_license_count": [
        re.compile(r"\bhow many\b.*\bexpired license", re.I),
        re.compile(r"\bexpired licenses\b.*\bcount\b", re.I),
    ],
    "phone_format_issues": [
        re.compile(r"\bphone\b.*(format|invalid|issue|problem)", re.I),
    ],
    "missing_npi": [
        re.compile(r"\bmissing\b.*\bnpi\b", re.I),
        re.compile(r"\bwhich\b.*\bnpi\b.*\bmissing\b", re.I),
    ],
    "duplicate_records": [
        re.compile(r"\bduplicate\b.*(record|provider)", re.I),
        re.compile(r"\bpotential duplicate", re.I),
    ],
    "overall_quality_score": [
        re.compile(r"\boverall\b.*\bquality score\b", re.I),
        re.compile(r"\bdata quality score\b", re.I),
    ],
    "specialties_with_most_issues": [
        re.compile(r"\bspecialt(y|ies)\b.*\bmost\b.*(issue|problem)", re.I),
    ],
    "state_issue_summary": [
        re.compile(r"\bsummary\b.*\b(state|by state)\b", re.I),
    ],
    "compliance_report_expired": [
        re.compile(r"\bcompliance report\b.*\bexpired\b", re.I),
    ],
    "filter_by_expiration_window": [
        re.compile(r"\bfilter\b.*\bexpiration\b.*\b(\d+)\s*days\b", re.I),
        re.compile(r"\bexpire(s|d)?\b.*\bnext\b.*\b(\d+)\b\s*days", re.I),
    ],
    "multi_state_single_license": [
        re.compile(r"\bmultiple states\b.*single license\b", re.I),
    ],
    "export_update_list": [
        re.compile(r"\bexport\b.*(update|credential) ", re.I),
    ],
}

def extract_params(intent: str, text: str):
    # Only one param used in this demo: days window for expiration
    if intent == "filter_by_expiration_window":
        m = re.search(r"(\d+)\s*days", text, re.I)
        if m:
            return {"days": int(m.group(1))}
        return {"days": 90}
    return {}