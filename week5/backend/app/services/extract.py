import re

TAG_PATTERN = re.compile(r"#([A-Za-z0-9_]+)")
CHECKBOX_PATTERN = re.compile(r"^-\s*\[\s\]\s*(.+)$")


def extract_action_items(text: str) -> list[str]:
    extracted: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        checkbox_match = CHECKBOX_PATTERN.match(line)
        if checkbox_match:
            extracted.append(checkbox_match.group(1).strip())
            continue

        normalized = line.lstrip("- ").strip()
        if normalized.endswith("!") or normalized.lower().startswith("todo:"):
            extracted.append(normalized)

    return extracted


def extract_tags(text: str) -> list[str]:
    seen: set[str] = set()
    extracted: list[str] = []
    for match in TAG_PATTERN.findall(text):
        normalized = match.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        extracted.append(normalized)
    return extracted
