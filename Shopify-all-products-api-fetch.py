import os
import requests
import json
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the headers
headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token': os.getenv('SHOPIFY_ACCESS_TOKEN')
}

url = 'https://professor-color.myshopify.com/admin/api/2022-01/products.json?limit=250'

# Send the request to the Shopify server
response = requests.get(url, headers=headers)

# Open (or create) a .csv file to write the data
with open('shopify_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # Initialize a CSV writer
    writer = csv.writer(csvfile)

    # Write the header row to the CSV file
    writer.writerow(['Title', 'ID', 'SKU'])

    # Ensure the request was successful
    if response.status_code == 200:
        # Load the JSON data from the response
        data = json.loads(response.text)

        # Iterate through each product
        for product in data['products']:
            # Iterate through each variant of the product
            for variant in product['variants']:
                # Write the product title, ID, and variant SKU to the CSV file
                writer.writerow([product["title"], product["id"], variant["sku"]])
    else:
        print(f'Request failed with status code {response.status_code}')
