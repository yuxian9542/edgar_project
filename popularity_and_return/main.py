import click
import config
from collect_data import download_filings, download_filings_helper_, download_stock_data


@click.command()
@click.option('--download', is_flag=True, help='Download SEC filings for the specified company and year')
@click.option('--company', type=str, help='Company ticker symbol', default=None)
@click.option('--year', type=int, help='Year to download filings for', default=None)


def main(download, company, year):
    """
    Main function to download SEC filings for specified companies and years.
    
    :param company: Company ticker symbol (optional, if not provided, all companies will be processed).
    :param year: Year to download filings for (optional, if not provided, all years will be processed).
    """
    if download:
        if company and year:
            download_filings_helper_(company, year)
            download_stock_data(company, f'{year}-01-01', f'{year}-12-31')
        else:
            download_filings(config.COMPANIES)
            download_stock_data(config.COMPANIES)


if __name__ == '__main__':
    main()