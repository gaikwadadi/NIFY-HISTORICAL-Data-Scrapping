#!/bin/bash

echo "Setting up NIFTY Historical Data Scraper..."

# Install Python dependencies
pip install -r requirements.txt

# Create config.json from example if it doesn't exist
if [ ! -f config.json ]; then
    cp config.example.json config.json
    echo "Created config.json from template"
fi

echo "Setup complete!"
echo ""
echo "Usage:"
echo "python nifty_scraper_production.py"
echo ""
echo "Make sure to run the scraper responsibly and respect the website's terms of service."
