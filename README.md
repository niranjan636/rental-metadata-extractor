# Rental Agreement Metadata Extraction

## 1. Overview

This project extracts structured metadata from rental agreements provided as DOCX documents and scanned PNG images.

It uses Google's Gemini generative AI model to interpret document text and images and extract six predefined metadata fields. The extracted information is normalized and saved in a CSV file for further use.

The implementation uses prompt-based AI extraction rather than relying primarily on fixed document templates or regular expressions.

## 2. Fields Extracted

The system extracts the following six fields:

- `Aggrement Value`
- `Aggrement Start Date`
- `Aggrement End Date`
- `Renewal Notice (Days)`
- `Party One`
- `Party Two`

The field names intentionally preserve the spelling used in the supplied dataset.

## 3. Approach

The extraction pipeline consists of the following stages:

1. **Document reading:** DOCX documents are read using `python-docx`, including paragraphs and tables.
2. **Image understanding:** Scanned PNG documents are processed using Gemini's image-understanding capabilities.
3. **AI-based extraction:** Gemini receives instructions to identify the requested metadata and return structured JSON.
4. **Normalization:** Extracted values are normalized to improve consistency in monetary values, notice periods, dates, and party names.
5. **CSV generation:** The resulting metadata is written to `predictions.csv`.

The primary extraction method is based on a generative AI model. Regular expressions and other deterministic operations are used only for limited post-processing and normalization, not as the primary metadata extraction method.

The project uses prompt-based inference with a Gemini model. It does not implement model fine-tuning or train a custom machine learning model.

## 4. Project Structure

```text
rental-metadata-extractor/
├── data/
│   ├── train/
│   ├── test/
│   ├── train.csv
│   └── test.csv
├── src/
│   ├── document_reader.py
│   ├── document_processor.py
│   ├── gemini_extractor.py
│   ├── image_reader.py
│   ├── docx_renderer.py
│   └── docx_vision_reader.py
├── predict.py
├── evaluate_clean.py
├── predictions.csv
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Main Components

- `document_reader.py`: Extracts text from DOCX paragraphs and tables.
- `gemini_extractor.py`: Uses Gemini to extract metadata from document text.
- `image_reader.py`: Uses Gemini to interpret scanned document images.
- `document_processor.py`: Coordinates document processing and normalizes extracted values.
- `docx_renderer.py`: Provides a utility for rendering DOCX documents to PDF using Microsoft Word.
- `docx_vision_reader.py`: Provides an additional DOCX-to-image extraction path.
- `predict.py`: Processes documents in the test directory and generates predictions.
- `evaluate_clean.py`: Evaluates extraction performance against available training labels, excluding known label/content mismatches.

## 5. Requirements

- Python 3.11 or a compatible Python version
- A Google Gemini API key
- Internet connectivity for Gemini API requests
- Dependencies listed in `requirements.txt`
- Microsoft Word installed on Windows for the optional DOCX-to-PDF rendering utilities

The standard DOCX extraction path uses `python-docx` and does not require Microsoft Word. Word is needed only for the rendering utilities that use Windows COM automation.

## 6. Installation and Configuration

### Step 1: Clone the repository

After the repository has been published to GitHub, run:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd rental-metadata-extractor
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual repository URL.

Alternatively, download the repository ZIP file and extract it locally.

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a local `.env` file in the project root using `.env.example` as a template.

Configure the following variables:

```text
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace the placeholder API key with your own Gemini API key.

**Security note:** Never commit `.env` or expose your API key in source code, screenshots, logs, or public repositories. The `.env` file should remain excluded through `.gitignore`.

The configured model must be available to your Google AI API account. If necessary, use a supported model name.

## 7. Generate Test Predictions

Place the test documents in `data/test/` and ensure that the corresponding filenames are represented correctly in the supplied dataset.

Run:

```powershell
python predict.py
```

The script processes supported DOCX and PNG documents in the test directory and saves the extracted metadata to:

```text
predictions.csv
```

The output includes the document filename and the six required metadata fields.

Some values may remain empty when the model cannot reliably extract them from the source document. The script reports extraction failures encountered during processing.

Review the resulting CSV to verify that the column names, filenames, and extracted values meet the assignment requirements.

## 8. Evaluate Extraction Performance

Run the cleaned-subset evaluator with:

```powershell
python evaluate_clean.py
```

The evaluator compares extracted values against the available labels in `data/train.csv`.

It reports exact-match recall separately for each field.

The calculation is:

**Exact-match recall = Number of correct exact matches / Number of non-empty ground-truth labels evaluated**

A prediction counts as correct only when its normalized output exactly matches the corresponding ground-truth value.

The evaluator:

- Skips documents without corresponding training labels.
- Excludes two known label/content mismatches.
- Skips individual fields with empty ground-truth labels.
- Reports mismatches to help identify extraction errors.

The evaluation script is intended to provide a preliminary assessment of the extraction pipeline. Its results depend on the quality of the supplied labels, the documents included in the evaluation, and the model's extraction output.

## 9. Preliminary Evaluation Results

The latest cleaned-subset evaluation produced the following results:

| Field | Exact Matches | Evaluated Labels | Exact-Match Recall |
|---|---:|---:|---:|
| Aggrement Value | 6 | 7 | 85.7% |
| Aggrement Start Date | 6 | 7 | 85.7% |
| Aggrement End Date | 3 | 7 | 42.9% |
| Renewal Notice (Days) | 1 | 6 | 16.7% |
| Party One | 4 | 7 | 57.1% |
| Party Two | 4 | 7 | 57.1% |

These scores are preliminary and are based on a small, cleaned subset of the training data. Two known label/content mismatches were excluded, and fields with missing ground-truth labels were not counted.

The results should not be interpreted as a robust estimate of generalization performance. In particular, renewal notice periods and end dates remain challenging extraction fields in the current evaluation.

## 10. Test Predictions

The latest prediction run processed four test documents and saved their extracted metadata to `predictions.csv`.

The prediction run completed without extraction exceptions. However, successful execution does not guarantee that every extracted value is correct or complete.

Test-set recall has not been reported because the current evaluation described above uses training labels. Test-set recall should only be calculated by comparing predictions with the corresponding test ground-truth labels using the assignment's evaluation rules.

## 11. Limitations

- **Document quality:** Poor scans and OCR-corrupted document text can lead to incorrect or missing values.
- **Ambiguous dates:** Rental agreements may describe dates indirectly or contain inconsistent date formats.
- **Label quality:** Some supplied ground-truth labels contain unusual or invalid dates, which can affect exact-match evaluation.
- **Name formatting:** Differences in punctuation, spacing, abbreviations, or OCR interpretation can cause exact-match failures.
- **Model variability:** Extraction results may vary between runs, and API availability or rate limits may affect execution.
- **Evaluation size:** The cleaned evaluation subset is small and may not represent performance on unseen document templates.
- **Source verification:** Extracted metadata should be checked against the original agreement when accuracy is important.
- **API dependency:** Processing requires access to a supported Gemini model and a valid API key.

## 12. REST API

A REST API was optional for the assignment and is not included in this implementation. The current workflow uses Python scripts to generate predictions and evaluate extraction performance.

## 13. Future Improvements

Potential improvements include:

- Improving extraction of renewal notice periods and indirectly stated end dates.
- Adding validation for extracted dates and monetary values.
- Improving name normalization while preserving the original meaning.
- Expanding evaluation to include more labeled documents and diverse document layouts.
- Adding structured error reporting and automated regression tests.
- Implementing a REST API for integration with other applications.

## 14. License and Usage

This project was developed as a document metadata extraction assignment.

Before publishing the repository, ensure that you have permission to distribute the supplied rental agreements and associated labels. Do not publish confidential documents, personal information, API keys, or other sensitive data.