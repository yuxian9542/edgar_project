"""
Extract company mentions from SEC filings using OpenAI API.
This script analyzes SEC 10-K and 20-F filings to count mentions of competitor companies.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from config import COMPANIES, SAVING_PATH

# Load environment variables from .env file
load_dotenv()


class CompanyMentionExtractor:
    """Extract and count company mentions from SEC filings using OpenAI API."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.companies = COMPANIES
        self.company_names = {
            "BKNG": ["Booking Holdings", "Booking.com", "Priceline", "Kayak", "Agoda", "OpenTable"],
            "EXPE": ["Expedia Group", "Expedia", "Hotels.com", "Vrbo", "Orbitz", "Travelocity", "Hotwire"],
            "TCOM": ["Trip.com", "Ctrip", "Skyscanner", "Qunar"],
            "TRIP": ["Tripadvisor", "TripAdvisor"],
            "TRVG": ["Trivago"],
            "MMYT": ["MakeMyTrip", "Goibibo"],
            "YTRA": ["Yatra", "Yatra Online"]
        }
        self.data_path = Path(SAVING_PATH) / "sec-edgar-filings"
        
    def extract_filing_year(self, accession_number: str) -> int:
        """Extract year from accession number (format: XXXXXXXXXX-YY-XXXXXX)."""
        year_part = accession_number.split('-')[1]
        year = int(f"20{year_part}")
        return year
    
    def read_filing_content(self, file_path: Path) -> str:
        """Read and extract main content from SEC filing."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract the main document content (between <DOCUMENT> tags)
            doc_start = content.find('<DOCUMENT>')
            if doc_start == -1:
                return content
            
            # Find the end of headers and start of actual content
            type_start = content.find('<TYPE>', doc_start)
            if type_start != -1:
                # Look for the actual filing content after headers
                content_start = content.find('</SEC-HEADER>', type_start)
                if content_start != -1:
                    content = content[content_start:]
            
            # Remove HTML tags and clean up
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content)
            
            return content.strip()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def count_mentions_with_openai(self, content: str, filing_company: str) -> Dict[str, int]:
        """Use OpenAI API to count company mentions in the filing content."""
        # Create list of companies to search for (excluding the filing company)
        target_companies = {k: v for k, v in self.company_names.items() if k != filing_company}
        
        # Prepare the prompt
        company_list = []
        for ticker, names in target_companies.items():
            company_list.append(f"{ticker}: {', '.join(names)}")
        
        prompt = f"""
Analyze the following SEC filing text and count how many times each of these companies is mentioned:

{chr(10).join(company_list)}

For each company, count all mentions of any of their brand names or variations. Return the results as a JSON object with ticker symbols as keys and counts as values. Only include companies that are mentioned at least once.

Here's the filing text (truncated if too long):
{content[:15000]}...
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at analyzing SEC filings. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()
            
            # Clean up the response to extract JSON
            if result_text.startswith('```json'):
                result_text = result_text[7:-3]
            elif result_text.startswith('```'):
                result_text = result_text[3:-3]
            
            try:
                mentions = json.loads(result_text)
                # Ensure all values are integers
                mentions = {k: int(v) for k, v in mentions.items() if isinstance(v, (int, str)) and str(v).isdigit()}
                return mentions
            except json.JSONDecodeError:
                print(f"Failed to parse JSON response: {result_text}")
                return {}
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {}
    
    def process_company_filings(self, ticker: str) -> Dict[int, Dict[str, int]]:
        """Process all filings for a single company."""
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
                        
                        # Read and analyze filing
                        content = self.read_filing_content(filing_file)
                        if content:
                            mentions = self.count_mentions_with_openai(content, ticker)
                            if mentions:
                                results[year] = mentions
                                print(f"    Found mentions: {mentions}")
                            else:
                                results[year] = {}
        
        return results
    
    def extract_all_mentions(self) -> Dict[str, Dict[int, Dict[str, int]]]:
        """Extract mentions for all companies and return structured results."""
        all_results = {}
        
        for ticker in self.companies.keys():
            print(f"\n=== Processing {ticker} ===")
            company_results = self.process_company_filings(ticker)
            if company_results:
                all_results[ticker] = company_results
        
        return all_results
    
    def save_results(self, results: Dict, output_file: str = "company_mentions.json"):
        """Save results to JSON file."""
        output_path = Path(SAVING_PATH) / output_file
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, sort_keys=True)
        
        print(f"\nResults saved to: {output_path}")
        return output_path


def main():
    """Main execution function."""
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize extractor
    extractor = CompanyMentionExtractor(api_key)
    
    # Extract mentions from all filings
    print("Starting company mention extraction...")
    results = extractor.extract_all_mentions()
    
    # Save results
    output_file = extractor.save_results(results)
    
    # Print summary
    print(f"\n=== EXTRACTION COMPLETE ===")
    print(f"Results saved to: {output_file}")
    print(f"Total companies processed: {len(results)}")
    
    # Print brief summary
    for company, years_data in results.items():
        total_mentions = sum(sum(year_mentions.values()) for year_mentions in years_data.values())
        print(f"{company}: {len(years_data)} years, {total_mentions} total mentions")


if __name__ == "__main__":
    main()