import pandas as pd
import json
from pathlib import Path


def load_filing_data():
    """Load and process SEC filing data."""
    # Load the JSON files
    dates_file = Path('data/filing_dates.json')
    mentions_file = Path('data/company_mentions.json')
    
    # Check if files exist
    if dates_file.exists():
        with open(dates_file, 'r') as f:
            dates_data = json.load(f)
        print(f"Loaded filing dates for {len(dates_data)} companies")
    else:
        print("Filing dates file not found. Run extract_filing_dates.py first.")
        dates_data = {}
    
    if mentions_file.exists():
        with open(mentions_file, 'r') as f:
            mentions_data = json.load(f)
        print(f"Loaded company mentions for {len(mentions_data)} companies")
    else:
        print("Company mentions file not found. Run extract_company_mentions.py first.")
        mentions_data = {}
    
    return dates_data, mentions_data


def create_filing_summary_df(dates_data):
    """Create a DataFrame summary of all filings with dates."""
    rows = []
    
    for ticker, years_data in dates_data.items():
        for year, filing_info in years_data.items():
            row = {
                'ticker': ticker,
                'year': int(year),
                'filed_date': filing_info.get('dates', {}).get('filed_date')
            }
            rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Convert date column
    if not df.empty:
        df['filed_date'] = pd.to_datetime(df['filed_date'])
    
    return df


def create_mentions_df(mentions_data, dates_data):
    """Create a DataFrame of competitor mentions with mention counts."""
    rows = []
    
    for filing_ticker, years_data in mentions_data.items():
        for year, mentions in years_data.items():
            # Handle both data structures:
            # 1. New structure: mentions_data[ticker][year] = {'competitor_mentions': {...}, 'dates': {...}}
            # 2. Old structure: mentions_data[ticker][year] = {mentioned_ticker: count, ...}
            
            if isinstance(mentions, dict) and 'competitor_mentions' in mentions:
                # New structure with full filing info
                competitor_mentions = mentions.get('competitor_mentions', {})
            else:
                # Old structure - mentions is directly the company counts
                competitor_mentions = mentions
            
            # Create rows for each mentioned company (excluding zero counts)
            for mentioned_ticker, count in competitor_mentions.items():
                if count > 0:  # Only include non-zero mentions
                    row = {
                        'ticker': filing_ticker,
                        'year': int(year),
                        'mentioned_company': mentioned_ticker,
                        'time': count  # time = number of times mentioned
                    }
                    rows.append(row)
    
    df = pd.DataFrame(rows)
    
    return df


# Load data
dates_data, mentions_data = load_filing_data()

# Create DataFrames
df_filings = create_filing_summary_df(dates_data)
df_mentions = create_mentions_df(mentions_data, dates_data)

