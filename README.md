Hi and welcome to: 
# CIA Factbook Webscraper | Part of the market research web dashboard

# What this does:

This repository includes the following to scrape the data at www.cia.gov/factbook:
- Scraper_CIA_functions --> A Python (.py) file that contains all the scraping functions
- Scraper_CIA_retrieval --> A Jupyter Notebook (.ipynb) to execute the scraping functions in


# Packages and installs required to use this:

Packages:
- Pandas
- Selenium to navigate dynamic websites 
- Scrapy to scrape site data using css or xpath selectors
- Requests to fetch HTML

Installs:
- Chromedriver to use Google Chrome through Python


# Notes

To use the webscraper yourself, you need to provide pathing to your browser driver (chrome, IE, etc.) to the `driver_setup()` function.
Currently only Chromedriver is supported in the driver_setup() function, however it can be tweaked to use FireFox with Firebug.

Have fun!

Warner