# Edgar Project - SEC Filing Analysis

A financial research tool that analyzes SEC filings and stock data to study the relationship between company mentions and stock returns in the travel/hospitality industry.

## Overview

This project downloads SEC 10-K and 20-F filings for major travel companies, extracts competitor mentions using OpenAI's API, and performs statistical analysis to determine if company mentions correlate with stock performance.

## Companies Analyzed

- **BKNG** - Booking Holdings Inc. (Booking.com, Priceline, Kayak, Agoda)
- **EXPE** - Expedia Group Inc. (Expedia, Hotels.com, Vrbo, Orbitz)
- **TCOM** - Trip.com Group Ltd. (Trip.com, Ctrip, Skyscanner)
- **TRIP** - TripAdvisor Inc.
- **TRVG** - Trivago N.V.
- **MMYT** - MakeMyTrip Ltd.
- **YTRA** - Yatra Online Inc.

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirement.txt

# Set OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Run Complete Analysis
```bash
cd popularity_and_return
python main.py --full-pipeline
```

This will:
1. Download SEC filings and stock data
2. Extract filing dates and company mentions
3. Process data and calculate annual returns
4. Run regression analysis

## Manual Steps

Run individual pipeline steps:

```bash
# Download data only
python main.py --download

# Extract company mentions (requires OpenAI API)
python main.py --extract-mentions

# Run statistical analysis
python main.py --analyze
```

## Key Files

- `main.py` - Main pipeline orchestrator
- `collect_data.py` - Downloads SEC filings and stock data  
- `extract_company_mentions.py` - Uses OpenAI to extract competitor mentions
- `analyze_mention.py` - Statistical regression analysis
- `config.py` - Company configuration and settings

## Output Files

Results are saved to `popularity_and_return/data/`:

- `filing_dates.json` - SEC filing publication dates and metadata
- `company_mentions.json` - Competitor mentions extracted from filings
- `annual_stock_return.csv` - Calculated annual stock returns
- `regression_results.csv` - Statistical analysis results

## Requirements

- Python 3.8+
- OpenAI API key (for mention extraction)
- Internet connection (for downloading SEC filings and stock data)

## Research Foundation

Based on academic research using LLMs to analyze company similarity through SEC filing business descriptions. The project examines whether mentions of competitors in annual reports correlate with stock performance.

## Cost Estimate

- OpenAI API usage: ~$2-10 for complete analysis
- Uses GPT-3.5-turbo for cost efficiency
- Processes ~42 filings (7 companies × 6 years)
