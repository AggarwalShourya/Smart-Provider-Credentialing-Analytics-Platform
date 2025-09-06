from typing import Tuple, Dict
import os
from .intents import INTENT_PATTERNS, extract_params
from .local_llm import local_intent

_LAST_NLU_INFO: Dict = {}

def get_last_nlu_info() -> Dict:
    return dict(_LAST_NLU_INFO)
def parse_intent(text: str) -> Tuple[str, Dict]:
    # Optional: use a local LLM (Ollama/llama.cpp) if enabled
    if os.getenv("DQ_USE_LOCAL_LLM", "false").lower() in ("1", "true", "yes"):
        try:
            ans = local_intent(text, list(INTENT_PATTERNS.keys()))
            if isinstance(ans, dict) and ans.get("intent") in INTENT_PATTERNS:
                intent = ans["intent"]
                params = ans.get("params", {}) or {}
                _LAST_NLU_INFO.update({
                    "method": "local_llm",
                    "enabled": True,
                    "intent": intent,
                    "params": params,
                    "raw": text,
                })
                return intent, params
        except Exception:
            pass

    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if p.search(text):
                params = extract_params(intent, text)
                _LAST_NLU_INFO.update({
                    "method": "regex",
                    "enabled": os.getenv("DQ_USE_LOCAL_LLM", "false").lower() in ("1", "true", "yes"),
                    "intent": intent,
                    "params": params,
                    "matched_pattern": getattr(p, "pattern", str(p)),
                    "raw": text,
                })
                return intent, params
    # Fallbacks: simple keywords
    t = text.lower()
    if "expired" in t and "license" in t and "how many" in t:
        intent, params = "expired_license_count", {}
    elif "duplicate" in t:
        intent, params = "duplicate_records", {}
    elif "quality score" in t:
        intent, params = "overall_quality_score", {}
    elif "phone" in t and ("issue" in t or "format" in t):
        intent, params = "phone_format_issues", {}
    else:
        intent, params = "overall_quality_score", {}
    _LAST_NLU_INFO.update({
        "method": "keyword_fallback",
        "enabled": os.getenv("DQ_USE_LOCAL_LLM", "false").lower() in ("1", "true", "yes"),
        "intent": intent,
        "params": params,
        "raw": text,
    })
    return intent, params