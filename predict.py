
from pathlib import Path

import pandas as pd

from src.document_processor import extract_document

DATA_DIR = Path("data/test")
OUTPUT_FILE = Path("predictions.csv")

FIELDS = [
    "Aggrement Value",
    "Aggrement Start Date",
    "Aggrement End Date",
    "Renewal Notice (Days)",
    "Party One",
    "Party Two",
]


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Test directory not found: {DATA_DIR}")

    files = sorted(
        path for path in DATA_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".docx", ".png"}
    )

    if not files:
        raise FileNotFoundError(f"No DOCX or PNG files found in {DATA_DIR}")

    columns = ["File Name", *FIELDS]

    # Load prior predictions so failed API calls don't erase valid results.
    previous = {}

    if OUTPUT_FILE.exists():
        try:
            old_df = pd.read_csv(OUTPUT_FILE, dtype=str).fillna("")
            if "File Name" in old_df.columns:
                for _, row in old_df.iterrows():
                    previous[row["File Name"]] = {
                        field: row.get(field, "")
                        for field in FIELDS
                    }
        except Exception as exc:
            print(f"Warning: could not read previous predictions: {exc}")

    rows = []
    failed_files = []

    for path in files:
        filename = path.stem
        print(f"Processing: {path.name}")

        try:
            prediction = extract_document(path)
            row = {
                "File Name": filename,
                **{
                    field: str(prediction.get(field, "") or "").strip()
                    for field in FIELDS
                },
            }

            # If extraction succeeds but returns blanks, preserve any
            # previous non-empty values rather than discarding them.
            old = previous.get(filename, {})
            for field in FIELDS:
                if not row[field] and old.get(field, "").strip():
                    row[field] = old[field].strip()

        except Exception as exc:
            print(f"ERROR processing {path.name}: {exc}")
            failed_files.append(path.name)

            old = previous.get(filename, {})
            row = {
                "File Name": filename,
                **{field: old.get(field, "") for field in FIELDS},
            }

        rows.append(row)

    output_df = pd.DataFrame(rows, columns=columns)
    output_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved predictions to {OUTPUT_FILE.resolve()}")
    print(output_df.to_string(index=False))

    print(f"\nDocuments found: {len(files)}")
    print(f"Documents failed: {len(failed_files)}")

    if failed_files:
        print("Files needing a retry:")
        for filename in failed_files:
            print(f" - {filename}")
    else:
        print("All documents completed without an extraction exception.")


if __name__ == "__main__":
    main()
