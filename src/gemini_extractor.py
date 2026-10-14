
import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

FIELDS = [
    "Aggrement Value",
    "Aggrement Start Date",
    "Aggrement End Date",
    "Renewal Notice (Days)",
    "Party One",
    "Party Two",
]


def extract_metadata(document_text: str) -> dict:
    """Extract rental agreement metadata with retry protection."""

    prompt = f"""
You are an expert AI system for extracting metadata from rental agreements.

Return exactly these six JSON keys:
{json.dumps(FIELDS)}

All values must be strings. Return valid JSON only.

1. Aggrement Value:
Extract the agreed monthly rent, not the security deposit or advance.
Return the numeric amount without currency symbols, commas, or
unnecessary decimal zeros. Use the written amount in words to resolve
obvious OCR errors only when the amount is clear.

2. Aggrement Start Date:
Extract the rental commencement date, distinguishing it from the
signing date. Convert unambiguous dates to DD.MM.YYYY.
Do not silently correct unusual dates.

3. Aggrement End Date:
Extract an explicitly stated expiry date or tenancy date range.
If only a start date and duration are given, calculate the likely
end date only when the agreement supports an unambiguous result.
Otherwise return an empty string.

4. Renewal Notice (Days):
Extract the notice period specifically relevant to renewal or
non-renewal. Do not automatically use a general termination notice
or a notice required only after a breach.
Convert months to days using 30 days per month when appropriate.
Return the number of days as a string, or an empty string if unknown.

5. Party One and Party Two:
Identify the first and second contracting parties using the agreement
context and labels such as LESSOR, LANDLORD, OWNER, LESSEE, and TENANT.
Return complete names without addresses or role labels.
For companies, return the company name, not its signatory.
Preserve spelling and initials.

6. Read the entire document. Do not invent missing information.
Use empty strings for fields that cannot be determined.
Do not use external knowledge or training labels.

DOCUMENT:
<document>
{document_text}
</document>
"""

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
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
                f"Extraction attempt {attempt + 1}/3 failed: {exc}"
            )

            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        f"Gemini extraction failed after 3 attempts: {last_error}"
    ) from last_error
