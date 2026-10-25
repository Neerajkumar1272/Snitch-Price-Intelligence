# Snitch Price Intelligence

A Python automation project that extracts publicly exposed product and variant data from the Snitch Shopify storefront, cleans it with **pandas**, and publishes a formatted snapshot to **Google Sheets**.

The goal is to turn storefront catalogue data into a spreadsheet that is easier to inspect for product prices, variants, SKU values, categories, and stock availability.

> **Important:** This repository does not provide a live monitoring service or historical price tracking. The script fetches one page of the storefront's public product endpoint when you run it. Use public data responsibly, respect the website's terms and rate limits, and do not attempt to access private or restricted information.

## What it does

- Requests product data from Snitch's public Shopify-style `/products.json` endpoint.
- Uses `pandas.json_normalize()` to flatten product variants into rows.
- Selects product and variant fields such as title, options, SKU, price, weight, vendor, category, and handle.
- Adds a product image preview using a Google Sheets `IMAGE()` formula.
- Derives an **In Stock / Out of Stock** label from each variant's `available` value.
- Adds the configured brand name to the exported records.
- Connects to Google Sheets using `gspread` and a Google Cloud service account.
- Clears and replaces the first worksheet with the latest extracted snapshot.
- Adjusts data-row heights to make image previews easier to view.

## Workflow

```text
Snitch public products endpoint
              |
              v
     Python requests + JSON
              |
              v
  pandas: flatten product variants
              |
              v
  Select fields + add image formula
              |
              v
  Google Sheets (replace worksheet data)
              |
              v
    Spreadsheet price snapshot
```

## Tech stack

| Component | Purpose |
|---|---|
| Python | Main script and workflow |
| requests | HTTP request to the public endpoint |
| pandas | Flattening, cleaning, and selecting fields |
| gspread | Google Sheets connection and worksheet updates |
| google-auth | Service-account authentication |
| Google Sheets API | Writing data and formatting row heights |

## Repository structure

```text
Snitch-Price-Intelligence/
├── main.py          # Extraction, transformation, and Sheets upload
├── README.md        # Project documentation
├── .gitignore       # Excludes local credentials and generated files
└── snitch_data.csv  # Local/exported data file (ignored by Git)
```

The CSV file may not be present in a fresh clone because it is ignored by Git.

## Requirements

- Python 3.10 or newer (Python 3.12 is also suitable).
- A Google account and a Google spreadsheet you can edit.
- A Google Cloud project with the **Google Sheets API** and **Google Drive API** enabled.
- A service account with access to the destination spreadsheet.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Neerajkumar1272/Snitch-Price-Intelligence.git
cd Snitch-Price-Intelligence
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install requests pandas gspread google-auth
```

### 4. Configure Google Sheets access

1. In Google Cloud Console, create or select a project.
2. Enable **Google Sheets API** and **Google Drive API**.
3. Create a service account and generate a JSON key **only if your organization's security policy allows key files**.
4. Save the key locally in the project folder as `credentials.json`. This file is excluded by `.gitignore`.
5. Open the destination spreadsheet and share it with the service account's email address, granting the access it needs.
6. Ensure the spreadsheet is named exactly `Snitch_Price_Intelligence`, or change the name in `main.py` to match your own spreadsheet.

**Never commit `credentials.json`, service-account keys, access tokens, or other secrets.** If a credential has ever been pushed to a repository, revoke it in Google Cloud immediately. Deleting the file from the latest commit is not a substitute for revoking the key.

### 5. Run the script

```bash
python main.py
```

The script is currently configured for the brand name `Snitch` and the URL `https://www.snitch.co.in/products.json?limit=250&page=1`. To use a different eligible storefront, update `TARGET_BRAND` and `TARGET_URL` near the bottom of `main.py`. Endpoint availability and response structure can vary by store.

## Data written to Google Sheets

The current script selects these columns:

| Column | Description |
|---|---|
| Product Preview | Image formula for the first product image, when available |
| Title | Variant title |
| option_1 / option_2 | Variant option values |
| SKU Code | Variant SKU |
| Price | Variant price returned by the endpoint |
| Product Weight | Variant weight in grams |
| Availability Status | Label derived from the variant's `available` field |
| Product Title | Parent product title |
| Product Vendor | Product vendor |
| Category | Product type |
| Handle | Product handle |
| Brand | Brand name configured in the script |

Exact values depend on the fields supplied by the endpoint. Some fields may be blank, and this script does not currently validate every field or convert prices into a separate currency format.

## Important implementation notes

- **One page only:** the configured URL requests page 1 with a limit of 250. The script does not currently loop through additional pages, so it may not collect the full catalogue.
- **Snapshot, not history:** each run replaces the existing first worksheet's contents. It does not preserve historical prices or stock changes.
- **Worksheet replacement:** `worksheet.clear()` removes existing worksheet content before the new data is uploaded. Use a dedicated output worksheet and back up important data first.
- **Network resilience:** the current request does not set a timeout or explicitly call `raise_for_status()`; production use should add both, along with error handling and retry/backoff.
- **Data integrity:** the script assumes expected keys such as `products`, `variants`, and `available` exist. Storefront response changes may require code updates.
- **Image previews:** Google Sheets must be able to access the image URL for the `IMAGE()` formula to render.
- **Google Sheets input mode:** the upload uses `USER_ENTERED`, which lets Sheets interpret formulas. Validate untrusted text before writing it to avoid unintended formula interpretation.

## Security and responsible use

- Keep credentials local and ensure `.gitignore` is active before staging files.
- Revoke exposed keys immediately; removing a file from the current branch does not erase copies from Git history, forks, or caches.
- Grant the service account only the access it needs and share the spreadsheet carefully.
- Respect website terms, applicable laws, rate limits, and data-access restrictions.
- Do not assume the public endpoint will always be available or retain the same schema.

## Potential improvements

- [ ] Add pagination and stop conditions to collect all available product pages.
- [ ] Add HTTP timeouts, status checks, retries, and clear error messages.
- [ ] Validate required JSON fields and handle missing or malformed data.
- [ ] Make the target URL, spreadsheet name, and credential path configurable through environment variables.
- [ ] Write to a dedicated output worksheet instead of clearing a worksheet that may contain other content.
- [ ] Save timestamped snapshots for historical price and availability comparisons.
- [ ] Add scheduled runs and alerts when prices or stock status change.
- [ ] Add automated tests for data transformation and API failures.

## Project value

This project demonstrates an end-to-end Python data workflow: collecting public web data, normalizing nested JSON, transforming product and variant records, authenticating with Google APIs, and publishing a spreadsheet report. It is a practical foundation for more robust catalogue and price-monitoring tools.

---

**Author:** Neeraj Kumar  
**Source code:** [`main.py`](main.py)  
**Repository:** [Snitch-Price-Intelligence](https://github.com/Neerajkumar1272/Snitch-Price-Intelligence)
