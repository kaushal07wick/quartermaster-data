import csv

def sum_mint_quantity(csv_file_path):
    total_minted = 0.0

    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            method = row["Method"].strip().lower()
            if method == "mint":
                try:
                    quantity = float(row["Quantity"].replace(",", ""))
                    total_minted += quantity
                except ValueError:
                    print(f"⚠️ Could not parse quantity: {row['Quantity']}")

    print(f"🔢 Total Quantity Minted: {total_minted}")

# Example usage
sum_mint_quantity("export-token-0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1.csv")
