import os
import json
from typing import Optional, Dict, Any


def _safe_json_extract(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract a JSON object from arbitrary text."""
    try:
        text = text.strip()
        # Strip code fences if any
        if text.startswith("`"):
            text = text.strip("`\n ")
            if text.lower().startswith("json"):
                text = text[4:].lstrip()
        # Direct parse
        return json.loads(text)
    except Exception:
        # Fallback: try to find outermost braces
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


class OllamaClient:
    """Simple local client for Ollama (http://localhost:11434). No external APIs.
    Env:
      - OLLAMA_HOST (default http://127.0.0.1:11434)
      - DQ_LLM_MODEL (e.g., "llama3.1:8b-instruct" or "mistral:7b-instruct")
    """

    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.model = os.getenv("DQ_LLM_MODEL", "llama3.1:8b-instruct")

    def ask_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        import urllib.request
        import urllib.error
        import ssl

        prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nReturn ONLY valid JSON."
        data = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            # Some environments need a permissive SSL context for localhost
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
                body = resp.read().decode("utf-8")
                obj = json.loads(body)
                out = obj.get("response", "")
                return _safe_json_extract(out)
        except Exception:
            return None


class LlamaCppClient:
    """Local llama.cpp runner via llama-cpp-python, given a GGUF model path.
    Env:
      - DQ_LLM_MODEL_PATH (absolute/relative path to .gguf file)
    """

    def __init__(self) -> None:
        self.path = os.getenv("DQ_LLM_MODEL_PATH")
        self._llm = None
        try:
            if self.path:
                from llama_cpp import Llama  # type: ignore
                self._llm = Llama(model_path=self.path, n_ctx=2048)
        except Exception:
            self._llm = None

    def ask_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        if not self._llm:
            return None
        prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nReturn ONLY valid JSON."
        try:
            out = self._llm(prompt, temperature=0.0, max_tokens=512)
            text = out["choices"][0]["text"] if out and "choices" in out else ""
            return _safe_json_extract(text)
        except Exception:
            return None


def local_intent(text: str, intents: list[str]) -> Optional[Dict[str, Any]]:
    """Try Ollama first (if reachable), then llama.cpp. Return dict or None."""
    system = (
        "You classify a user question into one of the allowed intents. "
        "Respond with strict JSON: {\n  \"intent\": string, \n  \"params\": object\n}. "
        "Never include commentary. If unsure, choose 'overall_quality_score'."
    )
    schema = {"intents": intents, "params": {"filter_by_expiration_window": ["days"]}}
    user = f"Question: {text}\nSchema: {json.dumps(schema)}"

    # Try Ollama
    try:
        ans = OllamaClient().ask_json(system, user)
        if ans:
            return ans
    except Exception:
        pass

    # Try llama.cpp
    try:
        ans = LlamaCppClient().ask_json(system, user)
        if ans:
            return ans
    except Exception:
        pass

    return None
