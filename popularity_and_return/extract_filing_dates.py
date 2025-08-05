"""
Extract filing dates and metadata from SEC filings.
This script extracts publication dates and company info from SEC 10-K and 20-F filings.
"""

import json
import re
from pathlib import Path
from typing import Dict
from config import COMPANIES, SAVING_PATH


class FilingDateExtractor:
    """Extract dates and metadata from SEC filings."""
    
    def __init__(self):
        """Initialize with company data."""
        self.companies = COMPANIES
        self.data_path = Path(SAVING_PATH) / "sec-edgar-filings"
        
    def extract_filing_year(self, accession_number: str) -> int:
        """Extract year from accession number (format: XXXXXXXXXX-YY-XXXXXX)."""
        year_part = accession_number.split('-')[1]
        year = int(f"20{year_part}")
        return year
    
    def extract_filing_date(self, file_path: Path) -> Dict[str, str]:
        """Extract key dates from SEC filing header."""
        dates = {
            'filed_date': None,
            'period_end': None,
            'acceptance_datetime': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read only the header section (first 5000 characters should be enough)
                header_content = f.read(5000)
            
            # Extract FILED AS OF DATE
            filed_match = re.search(r'FILED AS OF DATE:\s+(\d{8})', header_content)
            if filed_match:
                date_str = filed_match.group(1)
                # Convert YYYYMMDD to YYYY-MM-DD
                dates['filed_date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            # Extract CONFORMED PERIOD OF REPORT
            period_match = re.search(r'CONFORMED PERIOD OF REPORT:\s+(\d{8})', header_content)
            if period_match:
                date_str = period_match.group(1)
                dates['period_end'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            # Extract ACCEPTANCE-DATETIME
            acceptance_match = re.search(r'<ACCEPTANCE-DATETIME>(\d{14})', header_content)
            if acceptance_match:
                datetime_str = acceptance_match.group(1)
                # Convert YYYYMMDDHHMMSS to YYYY-MM-DD HH:MM:SS
                dates['acceptance_datetime'] = f"{datetime_str[:4]}-{datetime_str[4:6]}-{datetime_str[6:8]} {datetime_str[8:10]}:{datetime_str[10:12]}:{datetime_str[12:14]}"
            
        except Exception as e:
            print(f"Error extracting dates from {file_path}: {e}")
        
        return dates
    
    def extract_company_info(self, file_path: Path) -> Dict[str, str]:
        """Extract company information from SEC filing header."""
        company_info = {
            'company_name': None,
            'cik': None,
            'sic_code': None,
            'state_incorporation': None,
            'fiscal_year_end': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                header_content = f.read(5000)
            
            # Extract company name
            name_match = re.search(r'COMPANY CONFORMED NAME:\s+(.+)', header_content)
            if name_match:
                company_info['company_name'] = name_match.group(1).strip()
            
            # Extract CIK
            cik_match = re.search(r'CENTRAL INDEX KEY:\s+(\d+)', header_content)
            if cik_match:
                company_info['cik'] = cik_match.group(1)
            
            # Extract SIC code
            sic_match = re.search(r'STANDARD INDUSTRIAL CLASSIFICATION:\s+(.+?)\s+\[(\d+)\]', header_content)
            if sic_match:
                company_info['sic_code'] = sic_match.group(2)
            
            # Extract state of incorporation
            state_match = re.search(r'STATE OF INCORPORATION:\s+(\w+)', header_content)
            if state_match:
                company_info['state_incorporation'] = state_match.group(1)
            
            # Extract fiscal year end
            fiscal_match = re.search(r'FISCAL YEAR END:\s+(\d+)', header_content)
            if fiscal_match:
                company_info['fiscal_year_end'] = fiscal_match.group(1)
                
        except Exception as e:
            print(f"Error extracting company info from {file_path}: {e}")
        
        return company_info
    
    def process_company_filings(self, ticker: str) -> Dict[int, Dict]:
        """Process all filings for a single company to extract dates."""
        company_path = self.data_path / ticker
        results = {}
        
        if not company_path.exists():
            print(f"No filings found for {ticker}")
            return results
        
        # Determine filing type (10-K or 20-F)
        filing_types = [d for d in company_path.iterdir() if d.is_dir()]
        
        for filing_type_dir in filing_types:
            print(f"Processing {ticker} {filing_type_dir.name} filings...")
            
            for accession_dir in filing_type_dir.iterdir():
                if accession_dir.is_dir():
                    filing_file = accession_dir / "full-submission.txt"
                    
                    if filing_file.exists():
                        # Extract year from accession number
                        year = self.extract_filing_year(accession_dir.name)
                        
                        print(f"  Processing {ticker} {year} filing...")
                        
                        # Extract dates and company info
                        dates = self.extract_filing_date(filing_file)
                        company_info = self.extract_company_info(filing_file)
                        
                        # Store filing metadata
                        results[year] = {
                            'accession_number': accession_dir.name,
                            'filing_type': filing_type_dir.name,
                            'dates': dates,
                            'company_info': company_info
                        }
                        
                        print(f"    Filed: {dates['filed_date']}, Period End: {dates['period_end']}")
        
        return results
    
    def extract_all_dates(self) -> Dict[str, Dict[int, Dict]]:
        """Extract dates for all companies and return structured results."""
        all_results = {}
        
        for ticker in self.companies.keys():
            print(f"\n=== Processing {ticker} ===")
            company_results = self.process_company_filings(ticker)
            if company_results:
                all_results[ticker] = company_results
        
        return all_results
    
    def save_results(self, results: Dict, output_file: str = "filing_dates.json"):
        """Save results to JSON file."""
        output_path = Path(SAVING_PATH) / output_file
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, sort_keys=True)
        
        print(f"\nResults saved to: {output_path}")
        return output_path


def main():
    """Main execution function."""
    # Initialize extractor
    extractor = FilingDateExtractor()
    
    # Extract dates from all filings
    print("Starting filing date extraction...")
    results = extractor.extract_all_dates()
    
    # Save results
    output_file = extractor.save_results(results)
    
    # Print summary
    print(f"\n=== EXTRACTION COMPLETE ===")
    print(f"Results saved to: {output_file}")
    print(f"Total companies processed: {len(results)}")
    
    for company, years_data in results.items():
        print(f"{company}: {len(years_data)} years of filings")


if __name__ == "__main__":
    main()