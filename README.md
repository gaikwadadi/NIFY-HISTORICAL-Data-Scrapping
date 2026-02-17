# NIFTY Historical Data Reports Scraping

A production-grade Python scraper for fetching historical NIFTY indices data directly from the official NSE India website. This tool bypasses the website's frontend 1-year limitation by making direct API calls, enabling multi-year data collection in a single request.

## Features

- ✅ **Multi-Year Data Collection** - Fetch up to 25 years of data in a single request
- ✅ **Direct API Calls** - No browser automation or Selenium required
- ✅ **Production-Ready** - Comprehensive error handling and retry logic
- ✅ **Data Validation** - Automatic data integrity checks and cleaning
- ✅ **Rate Limiting** - Built-in IP protection with smart delays
- ✅ **Clean CSV Export** - Standardized output format
- ✅ **Professional Logging** - Console and file-based logging

## Requirements

- Python 3.7+
- Internet connection

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd test-data-scrapping
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

Or manually install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example configuration file:
```bash
cp config.example.json config.json
```

2. (Optional) Modify `config.json` to customize delays and other settings.

## Usage

Run the scraper:
```bash
python nifty_scraper_production.py
```

You'll be prompted to enter:
- **Index Name** (e.g., `NIFTY 50`, `NIFTY BANK`, `NIFTY IT`)
- **Start Date** (format: `DD-MM-YYYY`)
- **End Date** (format: `DD-MM-YYYY`)

### Example

```
=== NIFTY HISTORICAL DATA SCRAPER (Production) ===

Index Name (e.g., NIFTY 50): NIFTY 50
Start Date (DD-MM-YYYY): 01-01-2015
End Date (DD-MM-YYYY): 01-01-2025

Configuration:
Index: NIFTY 50
Date Range: 01-01-2015 to 01-01-2025

Proceed? (y/n): y

🎉 SUCCESS!
✅ Records: 2,456
✅ Date range: 01 Jan 2015 to 01 Jan 2025
✅ Saved: nifty_NIFTY_50_01012015_01012025.csv
```

## Output

The scraper generates CSV files with the following format:
- **Filename**: `nifty_{INDEX_NAME}_{START_DATE}_{END_DATE}.csv`
- **Columns**: Date, Open, High, Low, Close

Example output:
```csv
Date,Open,High,Low,Close
01 Jan 2025,23644.80,23782.30,23501.85,23742.90
31 Dec 2024,23587.50,23667.10,23502.05,23644.80
```

## Common Indices

- NIFTY 50
- NIFTY BANK
- NIFTY IT
- NIFTY AUTO
- NIFTY PHARMA
- NIFTY FMCG
- NIFTY METAL
- NIFTY REALTY
- NIFTY 500
- NIFTY MIDCAP 100

## Technical Details

### API Endpoint
```
https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString
```

### Data Source
Official NSE India NIFTY Indices website: https://www.niftyindices.com/reports/historical-data

### Key Features

**Multi-Year Support**: Unlike the website's frontend which limits requests to 1 year, this scraper directly calls the backend API which supports multi-year ranges (tested up to 25 years).

**Retry Logic**: Automatically retries failed requests up to 3 times with exponential backoff.

**Data Validation**: 
- Removes rows with missing or invalid data
- Validates data integrity (High >= Low, positive prices)
- Converts all numeric fields to proper types

**Rate Limiting**: Random delays (5-10 seconds) between requests to avoid overwhelming the server.

## Troubleshooting

### No data returned
- Verify the index name is correct (case-sensitive)
- Check date format is DD-MM-YYYY
- Ensure end date is not in the future
- Check internet connection

### Timeout errors
- The scraper will automatically retry (up to 3 attempts)
- Check `nifty_scraper.log` for detailed error information

### Invalid data
- Some historical dates may have no trading data (holidays, weekends)
- The scraper automatically filters out invalid records

## Logs

Logs are saved to `nifty_scraper.log` in the same directory. Check this file for detailed execution information and error messages.

## Disclaimer

This tool is for educational and research purposes only. Please respect the website's terms of service and use responsibly. Do not make excessive requests that could overload the server.

## Author

**Aditya Gaikwad**

## Version

2.0 (Production)
