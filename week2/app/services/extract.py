from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

try:
    from ollama import chat
except ImportError:  # pragma: no cover - exercised indirectly in environments without Ollama.
    chat = None

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"


class ExtractionServiceError(RuntimeError):
    pass


class ActionItemListResponse(BaseModel):
    items: list[str] = Field(..., description="Extracted action items.")


def get_ollama_model() -> str:
    configured_model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip()
    return configured_model or DEFAULT_OLLAMA_MODEL


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def normalize_action_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(cleaned)
    return normalized


def extract_action_items(text: str) -> list[str]:
    lines = text.splitlines()
    extracted: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    return normalize_action_items(extracted)


def extract_action_items_llm(text: str, model: str | None = None) -> list[str]:
    cleaned_text = text.strip()
    if not cleaned_text:
        return []
    if chat is None:
        raise ExtractionServiceError(
            "The ollama package is not installed. Install dependencies before using LLM extraction."
        )
    resolved_model = model or get_ollama_model()

    try:
        response = chat(
            model=resolved_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract only actionable tasks from the user's notes. "
                        "Return JSON with an 'items' field containing an array of concise strings. "
                        "Do not include commentary or non-actionable context."
                    ),
                },
                {
                    "role": "user",
                    "content": cleaned_text,
                },
            ],
            format=ActionItemListResponse.model_json_schema(),
            options={"temperature": 0},
        )
    except Exception as exc:
        raise ExtractionServiceError(
            f"Ollama request failed for model '{resolved_model}': {exc}"
        ) from exc

    try:
        payload = ActionItemListResponse.model_validate_json(response.message.content)
    except ValidationError as exc:
        raise ExtractionServiceError(
            f"Ollama returned an invalid structured response for model '{resolved_model}'."
        ) from exc

    return normalize_action_items(payload.items)


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
