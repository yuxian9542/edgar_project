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
                'accession_number': filing_info.get('accession_number'),
                'filing_type': filing_info.get('filing_type'),
                'filed_date': filing_info.get('dates', {}).get('filed_date'),
                'period_end': filing_info.get('dates', {}).get('period_end'),
                'acceptance_datetime': filing_info.get('dates', {}).get('acceptance_datetime'),
                'company_name': filing_info.get('company_info', {}).get('company_name'),
                'cik': filing_info.get('company_info', {}).get('cik'),
                'state_incorporation': filing_info.get('company_info', {}).get('state_incorporation')
            }
            rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Convert date columns
    if not df.empty:
        df['filed_date'] = pd.to_datetime(df['filed_date'])
        df['period_end'] = pd.to_datetime(df['period_end'])
        df['acceptance_datetime'] = pd.to_datetime(df['acceptance_datetime'])
    
    return df


def create_mentions_df(mentions_data):
    """Create a DataFrame of competitor mentions."""
    rows = []
    
    for filing_ticker, years_data in mentions_data.items():
        for year, filing_info in years_data.items():
            mentions = filing_info.get('competitor_mentions', {})
            
            for mentioned_ticker, count in mentions.items():
                row = {
                    'filing_ticker': filing_ticker,
                    'year': int(year),
                    'mentioned_ticker': mentioned_ticker,
                    'mention_count': count,
                    'filed_date': filing_info.get('dates', {}).get('filed_date'),
                    'period_end': filing_info.get('dates', {}).get('period_end'),
                    'accession_number': filing_info.get('accession_number')
                }
                rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Convert date columns
    if not df.empty:
        df['filed_date'] = pd.to_datetime(df['filed_date'])
        df['period_end'] = pd.to_datetime(df['period_end'])
    
    return df


# Load data
dates_data, mentions_data = load_filing_data()

# Create DataFrames
df_filings = create_filing_summary_df(dates_data)
df_mentions = create_mentions_df(mentions_data)

print(f"\nFiling Summary DataFrame: {df_filings.shape}")
if not df_filings.empty:
    print(df_filings.head())

print(f"\nMentions DataFrame: {df_mentions.shape}")
if not df_mentions.empty:
    print(df_mentions.head())