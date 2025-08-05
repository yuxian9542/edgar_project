import click
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from collect_data import download_filings, download_filings_helper_, download_stock_data


@click.command()
@click.option('--download', is_flag=True, help='Download SEC filings and stock data')
@click.option('--extract-dates', is_flag=True, help='Extract filing dates from downloaded SEC filings')
@click.option('--extract-mentions', is_flag=True, help='Extract company mentions using OpenAI API')
@click.option('--process-filings', is_flag=True, help='Process filing data and create analysis DataFrames')
@click.option('--process-stock', is_flag=True, help='Process stock data and calculate annual returns')
@click.option('--analyze', is_flag=True, help='Run regression analysis on mentions vs returns')
@click.option('--full-pipeline', is_flag=True, help='Run the complete pipeline from data collection to analysis')
@click.option('--all', is_flag=True, help='Run the complete pipeline from data collection to analysis (same as --full-pipeline)')
@click.option('--company', type=str, help='Company ticker symbol (for download only)', default=None)
@click.option('--year', type=int, help='Year to download filings for (for download only)', default=None)


def main(download, extract_dates, extract_mentions, process_filings, process_stock, analyze, full_pipeline, all, company, year):
    """
    Edgar Project - SEC Filing Analysis Pipeline
    
    This tool processes SEC filings and stock data to analyze the relationship 
    between company mentions and stock returns.
    
    PIPELINE STEPS:
    1. --download: Download SEC filings and stock data
    2. --extract-dates: Extract publication dates from filings  
    3. --extract-mentions: Extract company mentions using OpenAI
    4. --process-filings: Process and merge filing data
    5. --process-stock: Calculate annual stock returns
    6. --analyze: Run regression analysis
    
    Use --full-pipeline to run all steps in sequence.
    """
    
    print("🏢 Edgar Project - SEC Filing Analysis Pipeline")
    print("=" * 50)
    
    # Track which steps to run
    steps_run = []
    
    try:
        # Step 1: Download data
        if download or full_pipeline:
            print("\n📥 STEP 1: Downloading data...")
            run_download_step(company, year)
            steps_run.append("Download")
        
        # Step 2: Extract filing dates
        if extract_dates or full_pipeline:
            print("\n📅 STEP 2: Extracting filing dates...")
            run_extract_dates_step()
            steps_run.append("Extract Dates")
        
        # Step 3: Extract company mentions
        if extract_mentions or full_pipeline:
            print("\n🔍 STEP 3: Extracting company mentions...")
            run_extract_mentions_step()
            steps_run.append("Extract Mentions")
        
        # Step 4: Process filing data
        if process_filings or full_pipeline:
            print("\n📊 STEP 4: Processing filing data...")
            run_process_filings_step()
            steps_run.append("Process Filings")
        
        # Step 5: Process stock data
        if process_stock or full_pipeline:
            print("\n📈 STEP 5: Processing stock data...")
            run_process_stock_step()
            steps_run.append("Process Stock")
        
        # Step 6: Run analysis
        if analyze or full_pipeline:
            print("\n📊 STEP 6: Running regression analysis...")
            run_analysis_step()
            steps_run.append("Analysis")
        
        # Summary
        print("\n" + "=" * 50)
        print("✅ PIPELINE COMPLETE")
        print(f"📋 Steps completed: {', '.join(steps_run)}")
        print(f"📁 Results saved to: {config.SAVING_PATH}")
        
        if not any([download, extract_dates, extract_mentions, process_filings, process_stock, analyze, full_pipeline]):
            print("\n⚠️  No options selected. Use --help to see available commands.")
            print("💡 Try: python main.py --full-pipeline")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("🔧 Please check your setup and try again.")
        sys.exit(1)


def run_download_step(company, year):
    """Run data download step."""
    if company and year:
        print(f"   Downloading {company} data for {year}...")
        download_filings_helper_(company, year)
        download_stock_data(company, f'{year}-01-01', f'{year}-12-31')
    else:
        print("   Downloading all companies data...")
        download_filings(config.COMPANIES)
        download_stock_data(config.COMPANIES)
    print("   ✅ Download complete")


def run_extract_dates_step():
    """Run filing dates extraction step."""
    try:
        from extract_filing_dates import main as extract_dates_main
        extract_dates_main()
        print("   ✅ Filing dates extracted")
    except ImportError:
        print("   ❌ extract_filing_dates.py not found")
        raise
    except Exception as e:
        print(f"   ❌ Error extracting dates: {e}")
        raise


def run_extract_mentions_step():
    """Run company mentions extraction step."""
    try:
        from extract_company_mentions import main as extract_mentions_main
        extract_mentions_main()
        print("   ✅ Company mentions extracted")
    except ImportError:
        print("   ❌ extract_company_mentions.py not found")
        raise
    except Exception as e:
        print(f"   ❌ Error extracting mentions: {e}")
        raise


def run_process_filings_step():
    """Run filing data processing step."""
    try:
        from mention_to_csv import process_and_save_data
        process_and_save_data()
        print("   ✅ Filing data processed")
    except ImportError:
        print("   ❌ mention_to_csv.py not found")
        raise
    except Exception as e:
        print(f"   ❌ Error processing filings: {e}")
        raise


def run_process_stock_step():
    """Run stock data processing step."""
    try:
        # Check if we have the analyze_mention.py file with stock processing
        analyze_mention_file = Path(__file__).parent / "analyze_mention.py"
        if analyze_mention_file.exists():
            # Try to import the stock processing functions if they exist
            try:
                from analyze_mention import process_stock_data
                process_stock_data()
            except ImportError:
                # If process_stock_data doesn't exist, call the main function
                print("   Running analyze_mention.py to process stock data...")
                import subprocess
                result = subprocess.run([sys.executable, "analyze_mention.py"], 
                                      capture_output=True, text=True, cwd=Path(__file__).parent)
                if result.returncode != 0:
                    print(f"   Error output: {result.stderr}")
                    raise Exception("Stock processing failed")
        else:
            raise FileNotFoundError("analyze_mention.py not found")
        print("   ✅ Stock data processed")
    except Exception as e:
        print(f"   ❌ Error processing stock data: {e}")
        raise


def run_analysis_step():
    """Run regression analysis step."""
    try:
        # Call the existing analyze_mention.py main function
        import analyze_mention
        
        # Check if it has the functions we need
        if hasattr(analyze_mention, 'read_data') and hasattr(analyze_mention, 'run_regression_analysis'):
            df_input = analyze_mention.read_data()
            model = analyze_mention.run_regression_analysis(df_input)
            if hasattr(analyze_mention, 'save_regression_results'):
                analyze_mention.save_regression_results(model, df_input)
        else:
            # Run the entire analyze_mention.py script
            print("   Running complete analyze_mention.py script...")
            import subprocess
            result = subprocess.run([sys.executable, "analyze_mention.py"], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent)
            if result.returncode != 0:
                print(f"   Error output: {result.stderr}")
                raise Exception("Analysis failed")
            else:
                print(f"   Output: {result.stdout}")
        
        print("   ✅ Regression analysis complete")
    except ImportError:
        print("   ❌ analyze_mention.py not found")
        raise
    except Exception as e:
        print(f"   ❌ Error running analysis: {e}")
        raise


if __name__ == '__main__':
    main()