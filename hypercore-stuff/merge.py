import pandas as pd

# Load the CSV files
df1 = pd.read_csv('100_wallets.csv')
df2 = pd.read_csv('100_transactional_summary.csv')

# Rename 'Wallet_address' in df1 to match 'Wallet' in df2
df1.rename(columns={'Wallet_address': 'Wallet'}, inplace=True)

# Perform full outer join on 'Wallet'
merged = pd.merge(df1, df2, on='Wallet', how='outer', suffixes=('_file1', '_file2'))

# Combine Rank and Alias, preferring file1 values
merged['Rank'] = merged['Rank_file1'].combine_first(merged['Rank_file2'])
merged['Alias'] = merged['Alias_file1'].combine_first(merged['Alias_file2'])

# Drop duplicate Rank/Alias columns
merged.drop(columns=['Rank_file1', 'Rank_file2', 'Alias_file1', 'Alias_file2'], inplace=True)

# Convert Rank to numeric, errors='coerce' turns non-numeric into NaN
merged['Rank'] = pd.to_numeric(merged['Rank'], errors='coerce')

# Sort by Rank, NaNs last
merged.sort_values(by='Rank', inplace=True, na_position='last')

# Reorder columns: Rank, Alias, Wallet first
cols = ['Rank', 'Alias', 'Wallet'] + [col for col in merged.columns if col not in ['Rank', 'Alias', 'Wallet']]
merged = merged[cols]

# Save to CSV
merged.to_csv('merged_output.csv', index=False)

print("✅ Merge and sort complete. Output saved to 'merged_output.csv'.")
