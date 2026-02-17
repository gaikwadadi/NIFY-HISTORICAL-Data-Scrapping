"""
NIFTY Historical Data Scraper - Production Version
==================================================

A robust, production-grade scraper for fetching historical NIFTY indices data
directly from the official API. Supports multi-year data collection in a single request.

Features:
- Direct API calls (no browser automation needed)
- Multi-year data collection in single request
- Comprehensive error handling and retry logic
- Rate limiting and IP protection
- Clean CSV export with proper data validation
- Production-ready logging and monitoring

Author: Aditya Gaikwad
Version: 2.0 (Production)
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import random
import logging
from typing import Optional, Dict, Any
import sys

class NiftyDataScraper:
    """
    Production-grade NIFTY historical data scraper using direct API calls.
    
    This scraper bypasses the website's frontend 1-year limitation by calling
    the backend API directly, enabling multi-year data collection in single requests.
    """
    
    def __init__(self, timeout: int = 60, max_retries: int = 3):
        """
        Initialize the scraper with production-grade configuration.
        
        Args:
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum retry attempts for failed requests (default: 3)
        """
        self.api_url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure session with production headers
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.60 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.niftyindices.com/reports/historical-data',
            'Origin': 'https://www.niftyindices.com',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure production-grade logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('nifty_scraper.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _format_date_for_api(self, date_str: str) -> str:
        """
        Convert input date to API-required format.
        
        Args:
            date_str: Date in DD-MM-YYYY or DD-Mon-YYYY format
            
        Returns:
            Date in DD-Mon-YYYY format (e.g., "01-Jan-2023")
        """
        formats = ["%d-%m-%Y", "%d-%b-%Y", "%d-%B-%Y"]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%d-%b-%Y")
            except ValueError:
                continue
        
        raise ValueError(f"Invalid date format: {date_str}. Use DD-MM-YYYY or DD-Mon-YYYY")
    
    def _validate_date_range(self, start_date: str, end_date: str) -> None:
        """
        Validate date range for business logic constraints.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Raises:
            ValueError: If date range is invalid
        """
        start = datetime.strptime(self._format_date_for_api(start_date), "%d-%b-%Y")
        end = datetime.strptime(self._format_date_for_api(end_date), "%d-%b-%Y")
        
        if start >= end:
            raise ValueError("Start date must be before end date")
        
        if end > datetime.now():
            raise ValueError("End date cannot be in the future")
        
        # Reasonable limit check (adjust as needed)
        max_years = 25
        if (end - start).days > (max_years * 365):
            raise ValueError(f"Date range exceeds maximum limit of {max_years} years")
    
    def fetch_historical_data(self, index_name: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for specified index and date range.
        
        Args:
            index_name: Name of the index (e.g., "NIFTY 50")
            start_date: Start date in DD-MM-YYYY format
            end_date: End date in DD-MM-YYYY format
            
        Returns:
            DataFrame with historical data or None if failed
        """
        try:
            # Validate inputs
            self._validate_date_range(start_date, end_date)
            
            # Format dates for API
            api_start = self._format_date_for_api(start_date)
            api_end = self._format_date_for_api(end_date)
            
            self.logger.info(f"Fetching {index_name} data from {api_start} to {api_end}")
            
            # Attempt data retrieval with retry logic
            for attempt in range(self.max_retries):
                try:
                    df = self._make_api_request(index_name, api_start, api_end, attempt + 1)
                    
                    if df is not None and not df.empty:
                        self.logger.info(f"Successfully retrieved {len(df)} records")
                        return self._process_data(df)
                    
                    if attempt < self.max_retries - 1:
                        delay = random.uniform(5, 10)
                        self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s...")
                        time.sleep(delay)
                
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Network error on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(random.uniform(10, 15))
                
                except Exception as e:
                    self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(random.uniform(5, 10))
            
            self.logger.error("All retry attempts failed")
            return None
            
        except ValueError as e:
            self.logger.error(f"Input validation error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in fetch_historical_data: {e}")
            return None
    
    def _make_api_request(self, index_name: str, start_date: str, end_date: str, attempt: int) -> Optional[pd.DataFrame]:
        """
        Make the actual API request with proper error handling.
        
        Args:
            index_name: Index name
            start_date: Formatted start date
            end_date: Formatted end date
            attempt: Current attempt number
            
        Returns:
            DataFrame with raw data or None if failed
        """
        payload = {
            "cinfo": f"{{'name':'{index_name}','startDate':'{start_date}','endDate':'{end_date}','indexName':'{index_name}'}}"
        }
        
        self.logger.debug(f"API request attempt {attempt}: {payload}")
        
        response = self.session.post(self.api_url, json=payload, timeout=self.timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'd' in data and data['d']:
                records = json.loads(data['d'])
                
                if records:
                    return self._parse_api_response(records)
                else:
                    self.logger.warning("API returned empty data")
                    return None
            else:
                self.logger.warning("API response missing data field")
                return None
        else:
            self.logger.error(f"API error: HTTP {response.status_code}")
            return None
    
    def _parse_api_response(self, records: list) -> pd.DataFrame:
        """
        Parse API response into structured DataFrame.
        
        Args:
            records: List of data records from API
            
        Returns:
            DataFrame with parsed data
        """
        data = []
        
        for record in records:
            try:
                data.append({
                    'Date': record['HistoricalDate'],
                    'Open': float(record['OPEN']),
                    'High': float(record['HIGH']),
                    'Low': float(record['LOW']),
                    'Close': float(record['CLOSE'])
                })
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Skipping invalid record: {e}")
                continue
        
        return pd.DataFrame(data)
    
    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and validate the scraped data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Processed and validated DataFrame
        """
        if df.empty:
            return df
        
        # Sort by date (most recent first)
        df['DateSort'] = pd.to_datetime(df['Date'], format='%d %b %Y')
        df = df.sort_values('DateSort', ascending=False).drop('DateSort', axis=1)
        
        # Data validation
        numeric_cols = ['Open', 'High', 'Low', 'Close']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with invalid data
        initial_count = len(df)
        df = df.dropna(subset=numeric_cols)
        
        if len(df) < initial_count:
            self.logger.warning(f"Removed {initial_count - len(df)} rows with invalid data")
        
        # Basic data integrity checks
        invalid_rows = df[(df['High'] < df['Low']) | (df['Open'] <= 0) | (df['Close'] <= 0)]
        if not invalid_rows.empty:
            self.logger.warning(f"Found {len(invalid_rows)} rows with data integrity issues")
            df = df[~df.index.isin(invalid_rows.index)]
        
        return df.reset_index(drop=True)
    
    def save_to_csv(self, df: pd.DataFrame, index_name: str, start_date: str, end_date: str) -> str:
        """
        Save DataFrame to CSV with standardized naming.
        
        Args:
            df: DataFrame to save
            index_name: Index name
            start_date: Start date
            end_date: End date
            
        Returns:
            Filename of saved CSV
        """
        # Clean index name for filename
        clean_index = index_name.replace(' ', '_').replace('/', '_')
        clean_start = start_date.replace('-', '')
        clean_end = end_date.replace('-', '')
        
        filename = f"nifty_{clean_index}_{clean_start}_{clean_end}.csv"
        
        try:
            df.to_csv(filename, index=False)
            self.logger.info(f"Data saved to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save CSV: {e}")
            raise

def main():
    """Main function for command-line usage."""
    print("=== NIFTY HISTORICAL DATA SCRAPER (Production) ===\n")
    
    try:
        # Get user inputs
        index_name = input("Index Name (e.g., NIFTY 50): ").strip()
        start_date = input("Start Date (DD-MM-YYYY): ").strip()
        end_date = input("End Date (DD-MM-YYYY): ").strip()
        
        if not all([index_name, start_date, end_date]):
            print("❌ All fields are required")
            return
        
        print(f"\nConfiguration:")
        print(f"Index: {index_name}")
        print(f"Date Range: {start_date} to {end_date}")
        
        confirm = input("\nProceed? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled")
            return
        
        # Initialize scraper and fetch data
        scraper = NiftyDataScraper()
        df = scraper.fetch_historical_data(index_name, start_date, end_date)
        
        if df is not None and not df.empty:
            # Save results
            filename = scraper.save_to_csv(df, index_name, start_date, end_date)
            
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Records: {len(df)}")
            print(f"✅ Date range: {df['Date'].iloc[-1]} to {df['Date'].iloc[0]}")
            print(f"✅ Saved: {filename}")
            
            # Show sample data
            print(f"\n📊 Sample data:")
            print(df.head())
            
        else:
            print("\n❌ Failed to retrieve data")
            print("Check logs for detailed error information")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
