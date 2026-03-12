from __future__ import annotations

from types import SimpleNamespace

import pytest

from week2.app.services import extract as extract_service
from week2.app.services.extract import (
    ExtractionServiceError,
    extract_action_items,
    extract_action_items_llm,
)


def make_chat_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(message=SimpleNamespace(content=content))


def test_extract_bullets_and_checkboxes() -> None:
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert items == [
        "Set up database",
        "implement API extract endpoint",
        "Write tests",
    ]


def test_extract_action_items_llm_returns_structured_items(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_chat(**_: object) -> SimpleNamespace:
        return make_chat_response('{"items":["Set up database","Write tests"]}')

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    items = extract_action_items_llm("- [ ] Set up database\n- [ ] Write tests")

    assert items == ["Set up database", "Write tests"]


def test_extract_action_items_llm_deduplicates_keyword_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat(**_: object) -> SimpleNamespace:
        return make_chat_response(
            '{"items":["TODO: email the client","email the client","Next: prepare demo"]}'
        )

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    items = extract_action_items_llm("TODO: email the client\nNext: prepare demo")

    assert items == ["TODO: email the client", "email the client", "Next: prepare demo"]


def test_extract_action_items_llm_skips_chat_for_empty_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(**_: object) -> SimpleNamespace:
        raise AssertionError("chat should not be called for blank input")

    monkeypatch.setattr(extract_service, "chat", fail_if_called)

    assert extract_action_items_llm("   \n  ") == []


def test_extract_action_items_llm_raises_on_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_chat(**_: object) -> SimpleNamespace:
        return make_chat_response('{"wrong_key":["Set up database"]}')

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    with pytest.raises(ExtractionServiceError, match="invalid structured response"):
        extract_action_items_llm("Set up database")
