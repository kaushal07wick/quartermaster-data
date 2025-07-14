import requests
import csv
import time
from config import ETHERSCAN_API_KEY  # This imports ETHERSCAN_API_KEY from config.py

API_URL = 'https://api.etherscan.io/v2/api'

# Input and output files
input_file = 'contract.csv'
output_file = 'token_supplies.csv'

# Read contracts from CSV
with open(input_file, 'r') as infile:
    reader = csv.reader(infile)
    tokens = [(row[0], row[1]) for row in reader if row]

# Write the output
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Token Name', 'Contract Address', 'Total Supply'])

    for name, address in tokens:
        params = {
            'chainid': 999,
            'module': 'stats',
            'action': 'tokensupply',
            'contractaddress': address,
            'apikey': ETHERSCAN_API_KEY
        }

        try:
            response = requests.get(API_URL, params=params)
            data = response.json()

            if data.get('status') == '1':
                total_supply = data['result']
                writer.writerow([name, address, total_supply])
            else:
                writer.writerow([name, address, ''])

        except Exception as e:
            writer.writerow([name, address, ''])
