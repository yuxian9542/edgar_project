import pandas as pd
import re
from pathlib import Path
from config import SAVING_PATH
import warnings
warnings.filterwarnings('ignore')


def read_stock_data():
    """Read all CSV files in data/price folder and calculate annual returns."""
    price_folder = Path(SAVING_PATH) / "price"
    
    if not price_folder.exists():
        print(f"Price folder not found: {price_folder}")
        return pd.DataFrame()
    
    print(f"Reading stock data from: {price_folder}")
    
    all_stock_data = []
    annual_returns = []
    
    # Get all CSV files in the price folder
    csv_files = list(price_folder.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files:
        # Extract ticker from filename using regex to find text between < >
        filename = csv_file.name
        ticker_match = re.search(r'<([^>]+)>', filename)
        
        if not ticker_match:
            print(f"Warning: Could not extract ticker from filename: {filename}")
            continue
            
        ticker = ticker_match.group(1)
        print(f"Processing {ticker} from {filename}")
        
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Add ticker column
        df['ticker'] = ticker
        
        # Convert Date column to datetime and remove timezone info
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_convert('America/New_York')
        df = df.sort_values('Date')
        
        # Store the stock data
        all_stock_data.append(df)
        
        # Calculate annual returns
        annual_return_data = calculate_annual_returns(df, ticker)
        annual_returns.extend(annual_return_data)
    
    # Combine all stock data
    if all_stock_data:
        combined_stock_data = pd.concat(all_stock_data, ignore_index=True)
        print(f"Combined stock data shape: {combined_stock_data.shape}")
    else:
        combined_stock_data = pd.DataFrame()
    
    # Create annual returns DataFrame
    if annual_returns:
        annual_returns_df = pd.DataFrame(annual_returns)
        print(f"Annual returns data shape: {annual_returns_df.shape}")
    else:
        annual_returns_df = pd.DataFrame()
    
    return combined_stock_data, annual_returns_df


def calculate_annual_returns(df, ticker):
    """Calculate annual returns for a ticker."""
    annual_returns = []
    
    # Get unique years from the data
    df['year'] = df['Date'].dt.year
    years = sorted(df['year'].unique())
    
    for i in range(len(years) - 1):
        current_year = years[i]
        next_year = years[i + 1]
        
        # Get first trading day of current year
        current_year_data = df[df['year'] == current_year].sort_values('Date')
        if current_year_data.empty:
            continue
        first_day_current = current_year_data.iloc[0]
        
        # Get first trading day of next year
        next_year_data = df[df['year'] == next_year].sort_values('Date')
        if next_year_data.empty:
            continue
        first_day_next = next_year_data.iloc[0]
        
        # Calculate annual return
        if first_day_current['Close'] != 0:
            annual_return = ((first_day_next['Close'] - first_day_current['Close']) / 
                           first_day_current['Close']) * 100
            
            annual_returns.append({
                'ticker': ticker,
                'year': current_year,
                'start_date': first_day_current['Date'],
                'end_date': first_day_next['Date'],
                'start_price': first_day_current['Close'],
                'end_price': first_day_next['Close'],
                'annual_return_pct': annual_return
            })
            
            print(f"  {ticker} {current_year}: {annual_return:.2f}%")
    
    return annual_returns


def save_annual_returns(annual_returns_df):
    """Save annual returns to CSV file."""
    if annual_returns_df.empty:
        print("No annual returns data to save")
        return
    
    save_path = Path(SAVING_PATH)
    save_path.mkdir(exist_ok=True)
    
    output_file = save_path / "annual_stock_return.csv"
    
    # Sort by ticker and year for better organization
    annual_returns_df = annual_returns_df.sort_values(['ticker', 'year'])
    
    # Save to CSV
    annual_returns_df.to_csv(output_file, index=False)
    
    print(f"✓ Saved annual returns to: {output_file}")
    print(f"  Rows: {len(annual_returns_df)}")
    print(f"  Tickers: {annual_returns_df['ticker'].nunique()}")
    print(f"  Years: {annual_returns_df['year'].nunique()}")
    
    # Display sample data
    print("\nSample of annual returns data:")
    print(annual_returns_df.head(10))
    
    return output_file


def process_stock_data():
    """Main function to process stock data and calculate annual returns."""
    print("Starting stock data processing...")
    
    # Read stock data and calculate returns
    combined_stock_data, annual_returns_df = read_stock_data()
    
    if annual_returns_df.empty:
        print("No annual returns calculated. Check if price data files exist.")
        return None, None
    
    # Save annual returns
    output_file = save_annual_returns(annual_returns_df)
    
    print("\n=== PROCESSING COMPLETE ===")
    return combined_stock_data, annual_returns_df


if __name__ == "__main__":
    combined_stock_data, annual_returns_df = process_stock_data()