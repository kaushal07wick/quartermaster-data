from dune_client.client import DuneClient
from dotenv import load_dotenv

load_dotenv()
dune = DuneClient.from_env()

# Your CSV file
csv_file = 'cumulative_volume_chart.csv'
table_name = "cumulative_volume_CEX_DEX"

try:
    with open(csv_file, 'r') as f:
        data = f.read()
    
    dune.upload_csv(data=data, table_name=table_name, description="CSV upload")
    print("✅ Done")
    
except Exception as e:
    print(f"❌ Failed: {e}")