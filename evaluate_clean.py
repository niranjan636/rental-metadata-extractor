
from pathlib import Path

import pandas as pd

from src.document_processor import extract_document

FIELDS = [
    "Aggrement Value",
    "Aggrement Start Date",
    "Aggrement End Date",
    "Renewal Notice (Days)",
    "Party One",
    "Party Two",
]

EXCLUDED = {
    "54770958-Rental-Agreement",
    "54945838-Rental-Agreement",
}


def main():
    labels = pd.read_csv("data/train.csv", dtype=str).fillna("")

    if "File Name" not in labels.columns:
        raise ValueError("data/train.csv must contain a 'File Name' column")

    label_map = labels.set_index("File Name").to_dict("index")

    correct = dict.fromkeys(FIELDS, 0)
    total = dict.fromkeys(FIELDS, 0)

    data_dir = Path("data/train")
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Training directory not found: {data_dir}")

    files = sorted(
        p for p in data_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".docx", ".png"}
    )

    for path in files:
        name = path.stem

        if name in EXCLUDED:
            print(f"Excluded known label mismatch: {name}")
            continue

        if name not in label_map:
            print(f"Skipped: no training label for {name}")
            continue

        print(f"Evaluating: {path.name}")

        try:
            prediction = extract_document(path)
        except Exception as exc:
            print(f"Extraction error: {exc}")
            prediction = {}

        for field in FIELDS:
            expected = str(label_map[name].get(field, "") or "").strip()

            # Missing ground truth is not an evaluable example.
            if not expected:
                continue

            actual = str(prediction.get(field, "") or "").strip()
            total[field] += 1

            if actual == expected:
                correct[field] += 1
            else:
                print(
                    f"  {field}: expected={expected!r}, "
                    f"predicted={actual!r}"
                )

    print("\nExact-match recall (cleaned subset):")

    for field in FIELDS:
        n = total[field]
        score = correct[field] / n if n else 0.0
        print(f"{field}: {correct[field]}/{n} = {score:.1%}")

    print(
        "\nNote: known label/content mismatches were excluded. "
        "Scores are preliminary because the evaluation set is small "
        "and extraction results may vary between model runs."
    )


if __name__ == "__main__":
    main()
