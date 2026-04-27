import re


def extract_action_items(text: str) -> list[str]:
    # Match markdown tasks like "- [ ] Task" or "- [x] Task"
    markdown_tasks = re.findall(r"^\s*-\s*\[[ xX]?\]\s+(.+)$", text, re.MULTILINE)

    # Legacy logic: lines ending with ! or starting with todo:
    legacy_tasks: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        normalized = stripped.removeprefix("-").strip()
        if normalized.endswith("!") or normalized.lower().startswith("todo:"):
            legacy_tasks.append(normalized)

    # Combine and remove duplicates
    all_tasks = list(dict.fromkeys(markdown_tasks + legacy_tasks))
    return all_tasks


def extract_hashtags(text: str) -> list[str]:
    # Match words starting with # followed by alphanumeric characters
    tags = re.findall(r"#(\w+)", text)
    # Remove duplicates and normalize to lowercase
    return list(dict.fromkeys(tag.lower() for tag in tags))
