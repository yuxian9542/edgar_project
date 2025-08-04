from config import *
from sec_edgar_downloader import Downloader


def download_filings_helper_(ticker, year):
    """
    Download SEC filings for specified companies and years.
    
    :param companies: Dictionary of company ticker symbols and their respective years.
    :param years: List of years to download filings for.
    """
    dl = Downloader(MY_COMPANY, EMAIL, SAVING_PATH)

    try:
        dl.get("10-K", ticker, after=f'{year}-01-01')
        print(f"Downloaded 10-K for {ticker} for the year {year}.")
    except Exception as e:
        print(f"Failed to download 10-K for {ticker} for the year {year}: {e}")


def download_filings(companies=COMPANIES):
    """
    Download SEC filings for specified companies and years.
    
    :param companies: Dictionary of company ticker symbols and their respective years.
    """
    for ticker, years in companies.items():
        for year in years:
            download_filings_helper_(ticker, year)