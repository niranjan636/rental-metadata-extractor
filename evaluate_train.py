
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
    label_map = labels.set_index("File Name").to_dict("index")

    correct = dict.fromkeys(FIELDS, 0)
    total = dict.fromkeys(FIELDS, 0)

    files = sorted(
        p for p in Path("data/train").iterdir()
        if p.suffix.lower() in {".docx", ".png"}
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
            expected = label_map[name].get(field, "")
            actual = str(prediction.get(field, "") or "")

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
        score = correct[field] / n if n else 0
        print(f"{field}: {correct[field]}/{n} = {score:.1%}")


if __name__ == "__main__":
    main()
