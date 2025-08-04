from config import *
from sec_edgar_downloader import Downloader
import yfinance as yf
import datetime
import os
import requests
import json


def is_us_company(ticker):
    # SEC has "entity-info" endpoint to get registrant type
    headers = {"User-Agent": "zyuxian9542@gmail.com"}
    url = f"https://data.sec.gov/submissions/CIK{get_cik(ticker):010d}.json"
    res = requests.get(url, headers=headers)
    data = res.json()
    forms = data.get("filings", {}).get("recent", {}).get("form", [])
    
    return "10-K" in forms  # crude but generally effective


def get_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Your Name your.email@example.com"}
    r = requests.get(url, headers=headers)
    data = r.json()
    for info in data.values():
        if info["ticker"].lower() == ticker.lower():
            return int(info["cik_str"])
    raise ValueError(f"Ticker {ticker} not found.")


def download_filings_helper_(ticker, year):
    """
    Download SEC filings for specified companies and years.
    If the company is a US company, it downloads 10-K filings,
    otherwise it downloads 20-F filings.
    
    :param companies: Dictionary of company ticker symbols and their respective years.
    :param years: List of years to download filings for.
    """
    dl = Downloader(MY_COMPANY, EMAIL, SAVING_PATH)
    is_us = is_us_company(ticker)
    file_name = '10-K' if is_us else '20-F'

    try:
        dl.get(file_name, ticker, after=f'{year}-01-01')
        print(f"Downloaded {file_name} for {ticker} for the year {year}.")
    except Exception as e:
        print(f"Failed to download {file_name} for {ticker} for the year {year}: {e}")


def download_filings(companies=COMPANIES):
    """
    Download SEC filings for specified companies and years.
    
    :param companies: Dictionary of company ticker symbols and their respective years.
    """
    for ticker, year in companies.items():
        download_filings_helper_(ticker, year)


def download_stock_data_helper_(ticker, start_date, end_date):
    """
    Download stock data for a given ticker symbol between specified dates.
    
    :param ticker: Company ticker symbol.
    :param start_date: Start date for the stock data.
    :param end_date: End date for the stock data.
    """
    price_dir = f"{SAVING_PATH}/price"
    if not os.path.exists(price_dir):
        os.makedirs(price_dir)
    
    ticker = yf.Ticker(ticker)
    df = ticker.history(start=start_date, end=end_date)
    df.to_csv(f"{price_dir}/{ticker}.csv")


def download_stock_data(company=COMPANIES):
    """
    Download stock data for specified companies.
    
    :param company: Dictionary of company ticker symbols and their respective years.
    """
    for ticker, year in company.items():
        start_date = f'{year}-01-01'
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        download_stock_data_helper_(ticker, start_date, end_date)
        print(f"Downloaded stock data for {ticker} from {start_date} to {end_date}.")