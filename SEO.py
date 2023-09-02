import os
import csv
import openai
import time
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Existing categories
categories = {
    "Phaser Series": ["Phaser 6510", "Phaser 6515", "Phaser 3260", "Phaser 3610", "Phaser 6600", "Phaser 6022", "Phaser 7800", "Phaser 7500", "Phaser 3330", "Phaser 3320", "Phaser 3325", "Phaser 3635", "Phaser 3655", "Phaser 8560", "Phaser 8560MFP", "Phaser 3600", "Phaser 4600"],
    "VersaLink Series": ["VersaLink C400", "VersaLink C405", "VersaLink B400", "VersaLink B405", "VersaLink C500", "VersaLink C505", "VersaLink C600", "VersaLink C605", "VersaLink 8600", "VersaLink 8605", "VersaLink 8610", "VersaLink 8615", "VersaLink B600", "VersaLink B7025", "VersaLink 87020", "VersaLink 87025", "VersaLink 87030", "VersaLink C7020", "VersaLink C7025", "VersaLink C7030"],
    "WorkCentre Series": ["WorkCentre 6515", "WorkCentre 6605", "WorkCentre 3215", "WorkCentre 3225", "WorkCentre 3335", "WorkCentre 3345", "WorkCentre 6027", "WorkCentre 7220", "WorkCentre 7225", "WorkCentre 7830", "WorkCentre 7835", "WorkCentre 7845", "WorkCentre 5325", "WorkCentre 7855", "WorkCentre 7970", "WorkCentre 3315", "WorkCentre 6655", "WorkCentre 7120", "WorkCentre 7125", "WorkCentre 7525", "WorkCentre 7530", "WorkCentre 7535", "WorkCentre 7545", "WorkCentre 7556"],
    "AltaLink Series": ["AltaLink C8030", "AltaLink C8035", "AltaLink C8055", "AltaLink C8070", "AltaLink C8130"],
    "ColorQube Series": ["ColorQube 8570", "ColorQube 8580", "ColorQube 8870", "ColorQube 8880", "ColorQube 8900", "ColorQube 9301", "ColorQube 9302", "ColorQube 9303", "ColorQube 8700"],
    "DocuColor Series": ["DocuColor 240", "DocuColor 242", "DocuColor 250", "DocuColor 252", "DocuColor 260"],
    "Xerox D Series": ["D95", "D110", "D125", "D136"],
    "ColorQube": ["8700", "8570"],
    "Others": []
}
colors = ["black", "magenta", "cyan", "yellow"]
capacities = ["standard", "high", "extra high"]


def categorize_product(product_name):
    if '8700' in product_name or '8570' in product_name:
        return "ColorQube Series"
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in product_name.lower():
                return category
    return "Others"

def get_product_type(product_name):
    if "toner" in product_name.lower():
        return "Toner"
    elif "ink" in product_name.lower():
        return "Ink Cubes"
    elif "drum" in product_name.lower():
        return "Drums"
    else:
        return " "

def generate_product_title(product_name):
    try:
        time.sleep(5)
        # Updated prompt
        prompt = f"""
        I need a product title for '{product_name}'. The available colors are {', '.join(colors)}, and the available capacities are {', '.join(capacities)}. 

        The format should be: [Product Number / SKU] [Product capacity] - [color]
        Examples:
        106R03480 - Black Toner
        106R03394 High Yield - Black Toner
        106R03866-106R03869 Extra High Yield - 6 Pack Multicolor Bundle
        108R00993 - 2 Pack Black Ink Bundle

        If there is no capacity, omit it. Do not make up information or extrapolate information. Do not put "standard". 

        !IMPORTANT You must follow these rules:
        1. Omit all single and double quotes, '' or "".
        2. Omit the machine type, which is a grouping of 4 characters, from the title.
        3. Do not include the words 'Professor Color' or any shortened version like 'proco' in the title.
        4. Omit the word 'toner' even if it is part of the original product name.
        5. Do not include page count in the title.
        6. Omit all periods.
        7. Do not infer what the capacity is, if there is no capacity listed in the title, then omit any capacity.

        Given these rules, if the original product name is 'Professor Color Bypass Key Bundle Includes 8570 or 8580 Inks Replacing 108R00926 108R00927 108R00928 108R00929 (4 Repackaged Inks)', the new product title should be '108R00926-108R00929 Bundle - Extra High Capacity Bundle'. 

        Similarly, if the original product name is 'Professor Color Bypass Key Bundle Includes 8570 or 8580 Inks Replacing 108R00928 (2 Repackaged Yellow Inks)', the new product title should be '108R00928 - Extra High Capacity 2 Pack Yellow Ink Bundle'. 

        Please generate a single product title for '{product_name}'.
        """
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.2,
        )
        return completion.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating product title for {product_name}: {e}")
        return product_name


def extract_machine_type(product_name):
    # Special case for 8700 and 8570
    if '8700' in product_name:
        return 'ColorQube 8700'
    if '8570' in product_name:
        return 'ColorQube 8570'
    # Check if any of the machine types in 'categories' is a substring of 'product_name'
    for category, machine_types in categories.items():
        for machine_type in machine_types:
            if machine_type.lower() in product_name.lower():
                return machine_type
    return " "

def extract_sku(product_name):
    # Define a regular expression pattern for SKUs (alphanumeric codes of length 6 to 11)
    pattern = re.compile(r'\b\d{3}R\d{5}|\d{3}R\d{5}(?: \d{3}R\d{5}){1,6}\b')
    # Find all SKUs in the product name
    skus = re.findall(pattern, product_name)
    # Return SKUs as a single string separated by spaces
    return ' '.join(skus)

def categorize_csv(input_file, output_file, reference_file):
    # Read reference.csv into a dictionary
    reference_dict = {}
    with open(reference_file, 'r') as ref_csv:
        reader = csv.reader(ref_csv)
        next(reader)  # skip header
        for row in reader:
            part_number, _, ref_capacity = row
            reference_dict[part_number] = ref_capacity

    with open(input_file, 'r') as csv_input:
        with open(output_file, 'w', newline='') as csv_output:
            reader = csv.reader(csv_input)
            writer = csv.writer(csv_output)

            header = next(reader)
            if header[0] != "Product Title":
                print("Error: The header of the CSV should be 'Product Title'.")
                return

            # Write new header to the output
            writer.writerow(["Product Name", "Product Title", "Product Type", "Category", "Collections", "SKU", "Color", "Capacity", "Reference Capacity", "Tags", "SEO Page Title", "Description"])

            for row in reader:
                product_name = row[0]
                print(f"Processing: {product_name}")
                product_title = generate_product_title(product_name).replace('"', '').replace("'", "")
                print(product_title)
                category = categorize_product(product_name)
                product_type = get_product_type(product_name)
                collections = extract_machine_type(product_name)
                sku = extract_sku(product_name)

                # Extract yield from product name
                capacity = ""
                for cap in ["extra high", "high"]:
                    if cap in product_name.lower():
                        capacity = cap.capitalize()
                        break

                # Extract color from product name
                color = ""
                for col in colors:
                    if col in product_name.lower():
                        color = col.capitalize()
                        break
                
                # If no color found, set color based on SKU count
                if not color:
                    sku_count = len(sku.split())
                    if sku_count == 3:
                        color = "Cyan, Magenta, Yellow"
                    elif sku_count == 4:
                        color = "Black, Cyan, Magenta, Yellow"

                tags = ", ".join(filter(None, [sku, color, capacity, collections]))
                tags = tags.rstrip(', ')

                # Generate SEO Page Title
                seo_page_title = f"{collections} {sku} {product_type} - {capacity} {color} | Professor Color".strip()

                # Generate Description
                quality_descriptor = "Premium"
                benefit_statement = "Trust Professor Color for unmatched quality."
                description = f"{quality_descriptor} {product_type} for {collections}. {sku} {color} {product_type} designed for Xerox. Delivers vibrant prints with a yield of 8,000 pages. {benefit_statement}"


                # Check capacity against reference.csv
                reference_capacity = reference_dict.get(sku, "")
                if capacity != reference_capacity:
                    reference_capacity = reference_dict.get(sku, "")

                writer.writerow([product_name, product_title, product_type, category, collections, sku, color, capacity, reference_capacity, tags, seo_page_title, description])

if __name__ == "__main__":
    input_csv = 'input.csv'
    output_csv = 'categorized_output.csv'
    reference_csv = 'reference.csv'
    categorize_csv(input_csv, output_csv, reference_csv)
    print(f"Processed CSV saved to {output_csv}")