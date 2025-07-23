import os
import pandas as pd

input_folder = "Master_Data"  # <-- change this
output_file = "combined_circulating_supply.csv"  # output file

combined_df = None

for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        token_name = os.path.splitext(filename)[0].lower()  # use filename (without .csv) as column name
        file_path = os.path.join(input_folder, filename)

        # Load and clean data
        df = pd.read_csv(file_path)
        df["snapped_at"] = pd.to_datetime(df["snapped_at"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce").fillna(0)

        # Calculate circulating_supply
        df["circulating_supply"] = df["market_cap"] / df["price"]

        # Keep only timestamp and supply
        df = df[["snapped_at", "circulating_supply"]]
        df = df.rename(columns={"circulating_supply": token_name})

        # Merge into the combined dataframe
        if combined_df is None:
            combined_df = df
        else:
            combined_df = pd.merge(combined_df, df, on="snapped_at", how="outer")

# Sort by timestamp and save
combined_df = combined_df.sort_values("snapped_at")
combined_df.to_csv(output_file, index=False)

print(f"Combined circulating supply CSV saved to {output_file}")
