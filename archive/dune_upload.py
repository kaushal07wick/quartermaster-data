import os
from dune_client.client import DuneClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Dune client
dune = DuneClient.from_env()

# Name of the CSV file to upload (in current directory)
target_file = "weekly_aggregation_formatted.csv"

# Check if the file exists in the current directory
if not os.path.isfile(target_file):
    print(f"❌ File not found: {target_file}")
    exit(1)

# Get table name from file name
table_name = os.path.splitext(target_file)[0]

# Try uploading
try:
    with open(target_file, 'r', encoding='utf-8') as f:
        data = f.read()

    dune.upload_csv(
        data=data,
        table_name=table_name,
        description=f"CSV upload from {target_file}"
    )
    print(f"✅ Uploaded: {target_file} → table: {table_name}")

except Exception as e:
    print(f"❌ Failed to upload {target_file}: {e}")
