# Snitch Price Intelligence

A Python automation project that extracts publicly exposed product and variant data from the Snitch storefront, cleans it with **pandas**, and publishes a formatted snapshot to **Google Sheets**.

> **Scope:** This is a scheduled catalogue snapshot, not continuous monitoring or historical price tracking. The current URL requests one page of up to 250 products. Each run replaces the first worksheet's contents.

## What it does

- Fetches product JSON from the configured storefront URL.
- Flattens product variants into rows with pandas.
- Selects product/variant fields such as title, options, SKU, price, weight, vendor, category, and handle.
- Adds a Google Sheets `IMAGE()` formula for the first product image when available.
- Derives an **In Stock / Out of Stock** label.
- Writes the latest snapshot to the configured Google spreadsheet and adjusts data row heights.

## Repository structure

```text
Snitch-Price-Intelligence/
├── .github/workflows/daily-scrape.yml  # Daily scheduled run
├── main.py                             # Extract, transform, and sync
├── requirements.txt                    # Python dependencies
├── README.md
└── .gitignore                          # Excludes local credentials/data
```

## Automated daily run (GitHub Actions)

The workflow at `.github/workflows/daily-scrape.yml` is scheduled for **9:00 AM India Standard Time (IST, UTC+05:30) every day**. It uses GitHub Actions' UTC cron value `30 3 * * *`. It also supports manual runs.

### 1. Configure the service-account secret

In the repository, open **Settings → Secrets and variables → Actions → New repository secret**.

Recommended secret name:

```text
GOOGLE_CREDENTIALS_JSON
```

Its **value must be the complete contents of a newly generated Google service-account JSON key**, not a file path, email address, or key ID. Paste the JSON itself into the secret field. The workflow writes it to `credentials.json` only on the temporary GitHub Actions runner so the Python script can authenticate; it does not commit that file.

For convenience, the workflow also recognizes these alternative secret names if one already exists: `GOOGLE_CREDENTIALS`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SERVICE_ACCOUNT_KEY`, or `GCP_SA_KEY`. If more than one exists, the workflow uses the first non-empty name in the YAML expression.

**Security:** this repository previously contained a service-account JSON file. Delete/revoke that exposed key in Google Cloud and create a new key before adding it to GitHub Actions. Deleting the file from the repository does not revoke the credential or remove it from Git history.

### 2. Configure repository variables (optional)

Go to **Settings → Secrets and variables → Actions → Variables**. These exact names are supported:

| Variable | Default | Purpose |
|---|---|---|
| `TARGET_BRAND` | `Snitch` | Brand label written to the sheet |
| `TARGET_URL` | `https://www.snitch.co.in/products.json?limit=250&page=1` | Public product JSON endpoint |
| `SPREADSHEET_NAME` | `Snitch_Price_Intelligence` | Exact Google spreadsheet name |

The workflow also accepts `BRAND_NAME` as a fallback for `TARGET_BRAND` and `SNITCH_URL` as a fallback for `TARGET_URL`. Defaults work for this repository if those variables are not set.

### 3. Check the first run

1. Open the repository's **Actions** tab.
2. Select **Daily Snitch Price Intelligence**.
3. Choose **Run workflow** → **Run workflow** to test it immediately.
4. Open the new run and inspect each step's logs. The run should finish successfully and update the first worksheet in `Snitch_Price_Intelligence`.

The workflow runs on the repository's default branch. Scheduled runs can sometimes start a little later than the exact scheduled time because GitHub Actions scheduling is not a guaranteed real-time service.

## Run locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install packages and run:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

For local runs, place your valid service-account key in `credentials.json` in the project directory. It is excluded by `.gitignore`; **never push it to GitHub**.

## Google setup requirements

- Enable **Google Sheets API** and **Google Drive API** in the Google Cloud project.
- Use a Google service account with the access it needs.
- Share the destination spreadsheet with the service account email address.
- Ensure the spreadsheet name matches `SPREADSHEET_NAME` (default: `Snitch_Price_Intelligence`).

## Data written to the spreadsheet

| Column | Description |
|---|---|
| Product Preview | Image formula using the first product image, when available |
| Title | Variant title |
| option_1 / option_2 | Variant option values |
| SKU Code | Variant SKU |
| Price | Variant price returned by the endpoint |
| Product Weight | Weight in grams |
| Availability Status | In Stock / Out of Stock label |
| Product Title | Parent product title |
| Product Vendor | Product vendor |
| Category | Product type |
| Handle | Product handle |
| Brand | Configured brand label |

Actual values depend on the fields returned by the storefront endpoint.

## Important implementation notes

- **Single page only:** the default URL requests page 1 with `limit=250`; the script does not paginate through the full catalogue.
- **Snapshot, not history:** each run clears and replaces the first worksheet's contents. Do not keep unrelated information in that worksheet.
- **Network checks:** the script sets a request timeout and raises an error for unsuccessful HTTP status codes. It does not yet implement automatic retries.
- **Schema assumptions:** required JSON fields are assumed to exist; a storefront response change may require code updates.
- **Image preview:** Google Sheets must be able to access the image URL for the `IMAGE()` formula to render.
- **Schedule reliability:** GitHub Actions is suitable for a daily automation, but the start time is not guaranteed to be exact to the minute.

## Responsible use and security

- Revoke any service-account key that has ever been exposed in a public repository; create a replacement key before configuring the secret.
- Give the service account only the access required to update the intended spreadsheet.
- Keep credential files, access tokens, and private keys out of GitHub.
- Respect the website's terms, applicable laws, and reasonable rate limits. Use only public, permitted data.

## Possible next improvements

- [ ] Add pagination to retrieve the full catalogue.
- [ ] Add retry/backoff and clear error handling.
- [ ] Validate required JSON fields and handle partial/malformed responses.
- [ ] Save timestamped snapshots to compare price and availability changes.
- [ ] Add tests for data transformation and API failures.

---

**Author:** Neeraj Kumar  
**Source code:** [`main.py`](main.py)  
**Scheduled workflow:** [`daily-scrape.yml`](.github/workflows/daily-scrape.yml)  
**Repository:** [Snitch-Price-Intelligence](https://github.com/Neerajkumar1272/Snitch-Price-Intelligence)
