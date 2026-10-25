import requests
import json 
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(self.url, headers=headers)
        raw_data = response.json()
        
        # 1. Normalizing data 
        df = pd.json_normalize(
            raw_data['products'],
            record_path=["variants"],
            meta=["title", "vendor", "product_type", "handle"],
            meta_prefix="product_"
        )
        
        # 2. Image Mapping & Stock Status (Mode 1 use kiya hai taaki aspect ratio kharab na ho)
        image_map = {
            p["handle"]: p["images"][0]["src"] if p.get("images") else ""
            for p in raw_data["products"]
        }
        
        df["Product_Preview"] = df["product_handle"].map(image_map).apply(
            lambda x: f'=IMAGE("{x}", 1)' if x else ""
        )
        df["Stock_Status"] = df["available"].apply(lambda x: "In Stock" if x else "Out of Stock")

        # 3. Cleaning & Selecting Columns
        clean_df = df[[
            "Product_Preview", "title", "option1", "option2", "sku", 
            "price", "grams", "Stock_Status", "product_title", 
            "product_vendor", "product_product_type", "product_handle"
        ]]

        clean_df = clean_df.rename(columns={
            'Product_Preview': "Product Preview",
            'title': "Title",
            'option1': "option_1",
            'option2': "option_2",
            'sku': "SKU Code",
            'price': "Price",
            'grams': "Product Weight",
            'Stock_Status': "Availability Status",
            'product_title': "Product Title",
            'product_vendor': "Product Vendor",
            'product_product_type': "Category",
            'product_handle': "Handle"
        })

        clean_df["Brand"] = self.brand_name

        print("Data cleaned successfully! Now syncing with Google Sheets...")

        # 4. Google Sheets API Connection via gspread
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)

        # 5. Opening Sheet and Pushing Data
        spreadsheet = client.open("Snitch_Price_Intelligence")
        worksheet = spreadsheet.sheet1  

        clean_df = clean_df.fillna("")
        data_to_upload = [clean_df.columns.tolist()] + clean_df.values.tolist()

        worksheet.clear()
        worksheet.update(data_to_upload, value_input_option='USER_ENTERED')
        
        # 6. Automatic Row Height Adjustment (Images ko saaf aur proper dikhane ke liye)
        print("Setting row heights for perfect image display...")
        body = {
            "requests": [{
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet.id,
                        "dimension": "ROWS",
                        "startIndex": 1,  # Row 2 se start karke sabhi data rows
                        "endIndex": len(clean_df) + 1
                    },
                    "properties": {
                        "pixelSize": 50  # Har row ki height 90 pixels set ho jayegi
                    },
                    "fields": "pixelSize"
                }
            }]
        }
        spreadsheet.batch_update(body)
        
        print(f"Total {len(clean_df)} records are exported to Google Sheets") 

if __name__ == "__main__":
    TARGET_BRAND = "Snitch"
    TARGET_URL = "https://www.snitch.co.in/products.json?limit=250&page=1"
    
    bot = Scraping(TARGET_BRAND, TARGET_URL)
    bot.scrape_and_sync()
