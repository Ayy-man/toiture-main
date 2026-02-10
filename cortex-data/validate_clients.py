#!/usr/bin/env python3
"""
Data Validation - Check if client_id represents true unique customers
"""

import pandas as pd
import numpy as np

DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"

print("\n" + "="*80)
print(" DATA VALIDATION - CLIENT STRUCTURE")
print("="*80)

master = pd.read_csv(f"{DATA_PATH}master_quotes_valid.csv")
master['created_at'] = pd.to_datetime(master['created_at'], errors='coerce')

print(f"\nTotal quotes: {len(master):,}")
print(f"Unique client_ids: {master['client_id'].nunique():,}")
print(f"Unique project_ids: {master['project_id'].nunique():,}")
print(f"Unique building_ids: {master['building_id'].nunique():,}")

# Check relationship between client, project, building
print("\n" + "-"*80)
print(" RELATIONSHIP ANALYSIS")
print("-"*80)

# How many projects per client?
projects_per_client = master.groupby('client_id')['project_id'].nunique()
print(f"\nProjects per client:")
print(f"  Min: {projects_per_client.min()}")
print(f"  Max: {projects_per_client.max()}")
print(f"  Mean: {projects_per_client.mean():.2f}")
print(f"  Median: {projects_per_client.median():.0f}")

# How many buildings per client?
buildings_per_client = master.groupby('client_id')['building_id'].nunique()
print(f"\nBuildings per client:")
print(f"  Min: {buildings_per_client.min()}")
print(f"  Max: {buildings_per_client.max()}")
print(f"  Mean: {buildings_per_client.mean():.2f}")
print(f"  Median: {buildings_per_client.median():.0f}")

# Top 10 clients - detailed view
print("\n" + "-"*80)
print(" TOP 10 CLIENTS - DETAILED")
print("-"*80)

client_details = master.groupby('client_id').agg({
    'quoted_total': ['sum', 'count', 'mean'],
    'project_id': 'nunique',
    'building_id': 'nunique',
    'created_at': ['min', 'max']
}).reset_index()
client_details.columns = ['client_id', 'total_rev', 'quote_count', 'avg_quote', 
                          'unique_projects', 'unique_buildings', 'first_quote', 'last_quote']
client_details['tenure_days'] = (client_details['last_quote'] - client_details['first_quote']).dt.days
client_details = client_details.sort_values('total_rev', ascending=False)

print("\n{:<12} {:>12} {:>8} {:>10} {:>8} {:>10} {:>12}".format(
    'Client ID', 'Total Rev', 'Quotes', 'Avg Quote', 'Projects', 'Buildings', 'Tenure Days'))
print("-"*80)

for _, row in client_details.head(10).iterrows():
    print("{:<12} ${:>10,.0f} {:>8} ${:>9,.0f} {:>8} {:>10} {:>12}".format(
        int(row['client_id']), row['total_rev'], int(row['quote_count']), 
        row['avg_quote'], int(row['unique_projects']), int(row['unique_buildings']),
        int(row['tenure_days']) if pd.notna(row['tenure_days']) else 0))

# Check for potential duplicates - same building, different client?
print("\n" + "-"*80)
print(" POTENTIAL DATA ISSUES")
print("-"*80)

# Buildings with multiple clients
building_clients = master.groupby('building_id')['client_id'].nunique()
multi_client_buildings = building_clients[building_clients > 1]
print(f"\nBuildings with multiple client_ids: {len(multi_client_buildings):,}")
if len(multi_client_buildings) > 0:
    print(f"  (Could indicate same property under different clients/owners)")

# Check if client_id = project_id pattern
same_client_project = (master['client_id'] == master['project_id']).sum()
print(f"\nQuotes where client_id = project_id: {same_client_project:,} ({same_client_project/len(master)*100:.1f}%)")

# Check for very high frequency clients (potential commercial accounts)
high_freq = client_details[client_details['quote_count'] > 10]
print(f"\nClients with >10 quotes: {len(high_freq):,}")
print(f"  Revenue from these: ${high_freq['total_rev'].sum()/1e6:.1f}M ({high_freq['total_rev'].sum()/master['quoted_total'].sum()*100:.1f}%)")

# These are likely property managers or commercial accounts
very_high_freq = client_details[client_details['quote_count'] > 20]
print(f"\nClients with >20 quotes: {len(very_high_freq):,}")
print(f"  Revenue from these: ${very_high_freq['total_rev'].sum()/1e6:.1f}M ({very_high_freq['total_rev'].sum()/master['quoted_total'].sum()*100:.1f}%)")

# One-time analysis - are these really one-time or just recent?
print("\n" + "-"*80)
print(" ONE-TIME CLIENT ANALYSIS")
print("-"*80)

one_time_clients = client_details[client_details['quote_count'] == 1]
print(f"\nOne-time clients: {len(one_time_clients):,}")
print(f"  Total revenue: ${one_time_clients['total_rev'].sum()/1e6:.1f}M")
print(f"  Avg quote value: ${one_time_clients['avg_quote'].mean():,.0f}")

# When did one-time clients quote?
one_time_ids = one_time_clients['client_id'].tolist()
one_time_quotes = master[master['client_id'].isin(one_time_ids)]
one_time_by_year = one_time_quotes.groupby('year')['client_id'].nunique()
print(f"\n  One-time clients by year of first contact:")
for year, count in one_time_by_year.items():
    print(f"    {year}: {count:,}")

# Recent one-timers (2024-2025) might just not have had time to repeat
recent_one_time = one_time_clients[one_time_clients['first_quote'] >= '2024-01-01']
print(f"\n  Recent one-timers (2024+): {len(recent_one_time):,} (may still become repeat)")

# True one-timers (pre-2023)
old_one_time = one_time_clients[one_time_clients['first_quote'] < '2023-01-01']
print(f"  Old one-timers (pre-2023): {len(old_one_time):,} (likely truly one-time)")

# Category distribution for one-time vs repeat
print("\n" + "-"*80)
print(" CATEGORY COMPARISON: ONE-TIME vs REPEAT")
print("-"*80)

repeat_ids = client_details[client_details['quote_count'] > 1]['client_id'].tolist()
one_time_cat = master[master['client_id'].isin(one_time_ids)]['job_category'].value_counts(normalize=True).head(5)
repeat_cat = master[master['client_id'].isin(repeat_ids)]['job_category'].value_counts(normalize=True).head(5)

print("\nTop categories - ONE-TIME clients:")
for cat, pct in one_time_cat.items():
    print(f"  {cat}: {pct*100:.1f}%")

print("\nTop categories - REPEAT clients:")
for cat, pct in repeat_cat.items():
    print(f"  {cat}: {pct*100:.1f}%")

# Revenue concentration
print("\n" + "-"*80)
print(" REVENUE CONCENTRATION (PARETO)")
print("-"*80)

client_rev_sorted = client_details.sort_values('total_rev', ascending=False)
client_rev_sorted['cumulative_rev'] = client_rev_sorted['total_rev'].cumsum()
client_rev_sorted['cumulative_pct'] = client_rev_sorted['cumulative_rev'] / client_rev_sorted['total_rev'].sum() * 100
client_rev_sorted['client_pct'] = (range(1, len(client_rev_sorted) + 1)) / len(client_rev_sorted) * 100

# Find Pareto points
top_10_pct = client_rev_sorted[client_rev_sorted['client_pct'] <= 10]['cumulative_pct'].max()
top_20_pct = client_rev_sorted[client_rev_sorted['client_pct'] <= 20]['cumulative_pct'].max()

print(f"\n  Top 10% of clients ({int(len(client_details)*0.1):,}) = {top_10_pct:.1f}% of revenue")
print(f"  Top 20% of clients ({int(len(client_details)*0.2):,}) = {top_20_pct:.1f}% of revenue")

# How many clients for 80% of revenue?
clients_for_80 = client_rev_sorted[client_rev_sorted['cumulative_pct'] <= 80]
print(f"  Clients needed for 80% of revenue: {len(clients_for_80):,} ({len(clients_for_80)/len(client_details)*100:.1f}%)")

print("\n" + "="*80)
print(" VALIDATION COMPLETE")
print("="*80)
