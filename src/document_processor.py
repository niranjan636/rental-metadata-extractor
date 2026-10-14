
import re
from pathlib import Path

from src.document_reader import read_docx
from src.gemini_extractor import extract_metadata
from src.image_reader import extract_from_image


FIELDS = [
    "Aggrement Value",
    "Aggrement Start Date",
    "Aggrement End Date",
    "Renewal Notice (Days)",
    "Party One",
    "Party Two",
]


def normalize_metadata(data: dict) -> dict:
    """Normalize extracted metadata while preserving meaningful content."""

    result = {
        field: str(data.get(field, "") or "").strip()
        for field in FIELDS
    }

    # Normalize monetary values without joining unrelated digits.
    amount = result["Aggrement Value"]

    amount_match = re.fullmatch(
        r"(?:Rs\.?|INR|₹)?\s*([\d,]+)(?:\.(\d+))?\s*/?-?",
        amount,
        flags=re.IGNORECASE,
    )

    if amount_match:
        whole = amount_match.group(1).replace(",", "")
        decimals = amount_match.group(2)

        if not decimals or set(decimals) == {"0"}:
            result["Aggrement Value"] = whole
        else:
            result["Aggrement Value"] = f"{whole}.{decimals}"

    # Convert notice periods to days when a number and unit are given.
    notice = result["Renewal Notice (Days)"].lower().strip()

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    match = re.search(r"\d+(?:\.\d+)?", notice)
    number = float(match.group()) if match else None

    if number is None:
        for word, value in number_words.items():
            if re.search(rf"\b{word}\b", notice):
                number = value
                break

    if number is not None:
        if "month" in notice:
            number *= 30

        result["Renewal Notice (Days)"] = str(int(number))

    # Normalize honorifics and whitespace in party names.
    for field in ("Party One", "Party Two"):
        name = result[field]

        name = re.sub(
            r"^(?:(?:Mr|Mrs|Ms|Sri|Smt)\.?\s+)+",
            "",
            name,
            flags=re.IGNORECASE,
        )

        # Normalize repeated whitespace.
        name = re.sub(r"\s+", " ", name).strip()

        # Remove trailing punctuation without changing internal initials.
        name = name.rstrip(" .,")

        result[field] = name

    return result


def extract_document(file_path: str | Path) -> dict:
    """Extract and normalize metadata from a DOCX or PNG agreement."""

    path = Path(file_path)

    if path.suffix.lower() == ".docx":
        data = extract_metadata(read_docx(path))
    elif path.suffix.lower() == ".png":
        data = extract_from_image(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    return normalize_metadata(data)
 