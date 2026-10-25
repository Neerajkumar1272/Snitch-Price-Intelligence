# Snitch Price Intelligence

A Python-based e-commerce price-intelligence pipeline that collects publicly exposed product catalogue data from a Shopify storefront, normalizes it with pandas, and syncs the results to Google Sheets. The sheet is designed to act as a visual dashboard for product prices, variants, images, and stock availability.

> **Scope note:** This project is designed for publicly accessible storefront data. Shopify storefront endpoints and fields can change, and availability depends on the target store's configuration. Use it only in ways permitted by the website's terms and applicable law; respect rate limits and do not attempt to access private or restricted data.

## Features

- **Shopify catalogue extraction** — sends HTTP requests to a store's public `/products.json` endpoint using Python's `requests` library.
- **Structured data processing** — uses `pandas` to flatten product and variant information into a tabular format.
- **Price and variant tracking** — captures available product/variant fields such as titles, handles, prices, and metadata exposed by the endpoint.
- **Stock status** — derives an `In Stock` / `Out of Stock` label from the availability field returned for each variant.
- **Product image previews** — writes Google Sheets `IMAGE()` formulas so product images can be displayed directly in the sheet.
- **Google Sheets synchronization** — uses `gspread` and Google authentication to upload data in bulk.
- **Readable spreadsheet layout** — applies formatting through Google Sheets API batch requests, including row heights for image previews.
- **Credential hygiene** — keeps the service-account key out of version control through `.gitignore`.

## How the pipeline works

```text
Shopify public product endpoint
            |
            v
       Python requests
            |
            v
   JSON parsing and pandas
   flattening/normalization
            |
            v
 Product, variant, price, stock
       and image fields
            |
            v
   Google Sheets API / gspread
            |
            v
 Formatted price-intelligence sheet
```

## Tech stack

- **Language:** Python 3.12
- **Data collection:** `requests`
- **Data processing:** `pandas`
- **Google Sheets integration:** `gspread`, `google-auth`
- **Cloud APIs:** Google Sheets API and Google Drive API
- **Version control:** Git and GitHub

## Prerequisites

Before running the pipeline, make sure you have:

1. Python 3.12 installed.
2. Access to the public Shopify product endpoint for the store you intend to analyze.
3. A Google Cloud project with the **Google Sheets API** and **Google Drive API** enabled.
4. A Google Cloud service account with a JSON key stored locally.
5. A Google spreadsheet shared with the service-account email address, with the required edit permission.

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/Neerajkumar1272/Snitch-Price-Intelligence.git
   cd Snitch-Price-Intelligence
   ```

2. Create and activate a virtual environment:

   **Windows (PowerShell)**

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required libraries:

   ```bash
   pip install pandas requests gspread google-auth
   ```

4. Configure Google Cloud credentials locally. Place your service-account JSON key at the path expected by the script (for example, `credentials.json`) and configure the spreadsheet ID/name and target store URL as required by the code.

   **Never commit your service-account key, access tokens, or other secrets.** Keep the credential file in `.gitignore`.

5. Run the project's Python entry-point script:

   ```bash
   python <script_name>.py
   ```

   Replace `<script_name>.py` with the actual script filename in this repository. Check the script's configuration section for the expected store URL and spreadsheet settings.

## Google Sheets image rendering and formatting

The pipeline can write a formula such as:

```excel
=IMAGE("https://example.com/product-image.jpg", 1)
```

This allows Google Sheets to display an image from a publicly reachable image URL. Batch update requests can set row heights (for example, `pixelSize: 90`) to make image previews easier to view. Actual rendering depends on the URL being accessible to Google Sheets.

Bulk updates using `USER_ENTERED` tell Google Sheets to interpret values as if entered by a user, including formulas. Ensure source values are handled appropriately before uploading.

## Security and responsible use

- Keep `credentials.json`, service-account keys, and other secrets out of Git.
- If a key is accidentally exposed, revoke or rotate it immediately.
- Share the destination spreadsheet only with the accounts that need access.
- Use public data only and follow the target site's terms, applicable privacy rules, and rate limits.
- Do not treat a public endpoint as a guarantee of complete or uninterrupted access; endpoint availability, pagination, rate limits, and returned fields may vary.

## Current capabilities and limitations

The pipeline is intended to create a current snapshot of the fields exposed by the storefront endpoint and publish it to Google Sheets. It does **not**, by itself, create a historical price database or guarantee continuous/background updates. Data freshness depends on when the script is run and on the endpoint's response.

## Roadmap

- [ ] Archive timestamped snapshots to enable historical price comparisons.
- [ ] Schedule automatic runs with Windows Task Scheduler or Cron.
- [ ] Add change detection for price and stock status.
- [ ] Build Looker Studio dashboards for price trends and catalogue analytics.
- [ ] Add structured logging, retry/backoff handling, and validation for more reliable runs.

## Project value

This project demonstrates an end-to-end data workflow: public web data extraction, JSON normalization, product and variant analysis, cloud spreadsheet integration, and automated reporting. It can serve as a foundation for catalogue monitoring and price-intelligence workflows.

---

**Author:** Neeraj Kumar  
**Repository:** [Snitch-Price-Intelligence](https://github.com/Neerajkumar1272/Snitch-Price-Intelligence)
