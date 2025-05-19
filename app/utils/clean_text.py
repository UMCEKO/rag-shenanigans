import re


def clean_text(text: str) -> str:
    # 1. Remove dot leaders
    text = re.sub(r"\.{4,}", "", text)
    text = re.sub(r"(:?\. ){3,}", "", text)

    # 2. Remove any non-printable / control characters
    text = re.sub(r"[^\x20-\x7E\n]", "", text)

    # 3. Collapse multiple newlines or spaces
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()