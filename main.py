import os

import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


class Scraping:
    def __init__(self, brand_name, url):
        self.brand_name = brand_name
        self.url = url

    def scrape_and_sync(self):
        print(f"Fetching data for {self.brand_name}...")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(self.url, headers=headers, timeout=30)
        response.raise_for_status()
        raw_data = response.json()

        # 1. Normalize product variants
        df = pd.json_normalize(
            raw_data["products"],
            record_path=["variants"],
            meta=["title", "vendor", "product_type", "handle"],
            meta_prefix="product_",
        )

        # 2. Map images and derive stock status
        image_map = {
            product["handle"]: (
                product["images"][0]["src"] if product.get("images") else ""
            )
            for product in raw_data["products"]
        }

        df["Product_Preview"] = df["product_handle"].map(image_map).apply(
            lambda image_url: f'=IMAGE("{image_url}", 1)' if image_url else ""
        )
        df["Stock_Status"] = df["available"].apply(
            lambda available: "In Stock" if available else "Out of Stock"
        )

        # 3. Clean and select columns
        clean_df = df[
            [
                "Product_Preview",
                "title",
                "option1",
                "option2",
                "sku",
                "price",
                "grams",
                "Stock_Status",
                "product_title",
                "product_vendor",
                "product_product_type",
                "product_handle",
            ]
        ]

        clean_df = clean_df.rename(
            columns={
                "Product_Preview": "Product Preview",
                "title": "Title",
                "option1": "option_1",
                "option2": "option_2",
                "sku": "SKU Code",
                "price": "Price",
                "grams": "Product Weight",
                "Stock_Status": "Availability Status",
                "product_title": "Product Title",
                "product_vendor": "Product Vendor",
                "product_product_type": "Category",
                "product_handle": "Handle",
            }
        )
        clean_df["Brand"] = self.brand_name

        print("Data cleaned successfully! Now syncing with Google Sheets...")

        # 4. Authenticate with Google Sheets using local credentials.json
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(
            "credentials.json", scopes=scopes
        )
        client = gspread.authorize(creds)

        # 5. Replace the first worksheet with the latest snapshot
        spreadsheet_name = os.getenv(
            "SPREADSHEET_NAME", "Snitch_Price_Intelligence"
        )
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.sheet1

        clean_df = clean_df.fillna("")
        data_to_upload = [clean_df.columns.tolist()] + clean_df.values.tolist()

        worksheet.clear()
        worksheet.update(data_to_upload, value_input_option="USER_ENTERED")

        # 6. Set data row heights for image previews
        print("Setting row heights for product images...")
        body = {
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": worksheet.id,
                            "dimension": "ROWS",
                            "startIndex": 1,
                            "endIndex": len(clean_df) + 1,
                        },
                        "properties": {"pixelSize": 50},
                        "fields": "pixelSize",
                    }
                }
            ]
        }
        spreadsheet.batch_update(body)

        print(f"Total {len(clean_df)} records exported to Google Sheets.")


if __name__ == "__main__":
    target_brand = os.getenv("TARGET_BRAND", "Snitch")
    target_url = os.getenv(
        "TARGET_URL",
        "https://www.snitch.co.in/products.json?limit=250&page=1",
    )

    bot = Scraping(target_brand, target_url)
    bot.scrape_and_sync()
