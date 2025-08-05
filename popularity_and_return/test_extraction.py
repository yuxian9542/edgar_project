"""
Test script for company mention extraction.
This script tests the extraction functionality on a small sample.
"""

import os
from dotenv import load_dotenv
from extract_company_mentions import CompanyMentionExtractor

# Load environment variables from .env file
load_dotenv()


def test_single_filing():
    """Test extraction on a single filing."""
    print("Testing company mention extraction...")
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Initialize extractor
    extractor = CompanyMentionExtractor(api_key)
    
    # Test on one company's recent filing (BKNG 2024)
    print("Testing on BKNG 2024 filing...")
    results = extractor.process_company_filings("BKNG")
    
    if results:
        print("Test successful! Sample results:")
        for year, mentions in results.items():
            print(f"  {year}: {mentions}")
        return True
    else:
        print("Test failed - no results returned")
        return False


if __name__ == "__main__":
    success = test_single_filing()
    if success:
        print("\n✓ Test passed! You can now run the full extraction with:")
        print("python extract_company_mentions.py")
    else:
        print("\n✗ Test failed. Please check your setup.")