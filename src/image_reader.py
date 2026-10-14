
import json
import time
from pathlib import Path

from google.genai import types

from src.gemini_extractor import client, MODEL_NAME, FIELDS


def extract_from_image(file_path: str | Path) -> dict:
    """Extract rental agreement metadata from a scanned image."""

    path = Path(file_path)
    image_bytes = path.read_bytes()

    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(suffix)

    if not mime_type:
        raise ValueError(f"Unsupported image format: {suffix}")

    prompt = f"""
You are an expert AI system extracting metadata from rental agreements.

Extract exactly these fields:
{json.dumps(FIELDS)}

Return a JSON object only. Every value must be a string.

INSTRUCTIONS:

1. Aggrement Value:
Extract the agreed monthly rent, not a security deposit or advance.
Return the numeric amount without currency symbols, commas, or
unnecessary decimal zeros. Do not guess when the image is unreadable.

2. Aggrement Start Date:
Identify the actual commencement date. Distinguish it from the
signing date. Format unambiguous dates as DD.MM.YYYY.

3. Aggrement End Date:
Find an explicitly stated expiry date or tenancy date range.
Do not calculate an end date from a duration.
Return an empty string if no end date is explicitly stated.

4. Renewal Notice (Days):
Extract the notice period relevant to renewal or non-renewal.
Do not automatically substitute a general termination notice.
Convert months to days using 30 days per month when appropriate.
Return an empty string if the relevant period is unclear.

5. Party One and Party Two:
Identify the first and second contracting parties using labels
such as LESSOR, LANDLORD, OWNER, LESSEE, and TENANT.
Return their complete names without addresses or role labels.
For companies, return the company name rather than its signatory.

6. Inspect the entire image, including small print and clauses.
Preserve names and initials as legible.
Do not invent missing values or silently correct unusual dates.
Use empty strings when information cannot be determined.

Return exactly the requested six keys.
"""

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            field: {"type": "STRING"}
                            for field in FIELDS
                        },
                        "required": FIELDS,
                    },
                    temperature=0,
                ),
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response")

            result = json.loads(response.text)

            if not isinstance(result, dict):
                raise ValueError("Gemini response is not a JSON object")

            return {
                field: str(result.get(field, "") or "").strip()
                for field in FIELDS
            }

        except Exception as exc:
            last_error = exc
            print(
                f"Image extraction attempt {attempt + 1}/3 failed: {exc}"
            )

            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        f"Image extraction failed after 3 attempts: {last_error}"
    ) from last_error
