from chromedriver_path import chrome_driver
Chromedriver_path = chrome_driver()

def setup_driver():
    """ 
    Setting up the driver for scraping
    """
    # Import webdriver for interactive webpages
    from selenium import webdriver

    # Initiate Selenium using the chrome browser, would be nice to have future editions include other browsers
    chromedriver = Chromedriver_path
    driver = webdriver.Chrome(executable_path=chromedriver)
    return driver


def country_list_scraper(driver):
    """ 
    The CIA Factbook holds per country a webpage with country-specific information.
    This function scrapes the url designated to each country's webpage
    And returns it as a list
    """
    # Import modules, scrapy will get the data, selenium will navigate the website
    from scrapy import Selector
    import requests

    # Selecting the CIA webpage url to navigate to countries
    driver.get('https://www.cia.gov/the-world-factbook/countries/')
    
    # The page is interactive, there are 12 countries displayed per page, clicking the next page button with selenium reveals the next 12
    page_button = driver.find_element_by_css_selector(' div.row.no-gutters > div > div > span.pagination__arrow-right > svg')

    # The max number of pages is found with scrapy
    selenium_response_text = driver.page_source
    sel = Selector(text = selenium_response_text)
    page_count = sel.css('span.label::text')[-1].extract()

    # Initiating a list to hold scraped country urls
    country_urls = []

    # Using a for loop to scrape the country urls (scrapy), click next page (selenium) and repeat until last page
    for page in range(0, int(page_count)):
        
        # load page info for scrapy
        selenium_response_text = driver.page_source
        sel = Selector(text = selenium_response_text)
        
        # Extract and append urls into a list 
        country_url = sel.css('a.inline-link::attr(href)').extract()
        country_urls.append(country_url)
        
        # click the next page button
        page_button.click()

    # Print 
    print(f'URLs from {page} pages were retrieved')

    # Flattening the resulting nested list
    country_urls = [item for sublist in country_urls for item in sublist]
    countries = [country.split('/')[3] for country in country_urls]
    return countries


def country_topic_scraper(driver, countries):
    """
    The topics per country factbook page differs   
    """
    
    # Import scrapy to select the data
    from scrapy import Selector
    
    # Initiate a list to hold topics
    all_topics = []

    # Loop over the country_urls
    for country in range(0, len(countries)):
        driver.get(f'https://www.cia.gov/the-world-factbook/countries/{countries[country]}')
        selenium_response_text = driver.page_source
        sel = Selector(text = selenium_response_text)    
        
        # Retrieving the main topics
        topics = set(sel.css('div.free-form-content__content::attr(id)').extract())
        for topic in topics:
            if topic not in all_topics:
                all_topics.append(topic)
    return all_topics


def country_data_scraper(driver, countries, topics, transpose=True, append=False, append_name='Appended'):    
    """
    Scrapes the data from the CIA Factbook country pages exported into .csv files
    The optional countries and topics parameters can accept lists to narrow the selection
    Else all countries and topics will be scraped.

    The transpose option allows the features to be exported per row

    Append allows all data to be put in one csv 
    """
    # Importing modules
    from scrapy import Selector
    import pandas as pd
    import requests
    
    driver.get('https://www.cia.gov/the-world-factbook/countries/')

    # Selecting the countries and topics were interested in
    countries_of_interest = [x.lower().strip().replace(' ','-') for x in countries] 
    print(countries_of_interest)
    topics_of_interest = [x.lower().strip().replace(' ','-') for x in topics]
    appended_results = []

    """ For future versions: if a country name has been input, that does not exist in the CIA factbook list, return an error """


    # Opening and retrieving each country's factbook page
    for country in range(0, len(countries)):

        # Selecting the page with selenium for scrapy
        driver.get(f'https://www.cia.gov/the-world-factbook/countries/{countries_of_interest[country]}')
        selenium_response_text = driver.page_source
        sel = Selector(text = selenium_response_text)
        
        # Initiating a dictionary to store scraped results
        results = {}

        # Printing country name to user
        country = sel.css('div.col-sm-12.col-md-8.hero-splash > h1.hero-title::text').extract_first()
        print("Started scraping: " + country)    

        # Include country name in the results
        results.update({'Country':[country]})

        # Fetching the sub_topics of each topic_of_interest, this varies per country
        for topic in range(0, len(topics_of_interest)):
            sub_topics = sel.css(f'div.free-form-content__content#{topics_of_interest[topic]} > div > h3 > a::text').extract()

            # Initiate a dictionary to contain key-value pairs of each sub_topic and its data
            pair = {}

            # Loop over the sub-topics
            for sub_topic in range(0, len(sub_topics)):

                # increment the item number, sub_topic, with 2 because the css selector starts at 1, not 0
                # and because there is always a h2 element before our div element, we add another 1 
                # thus we start at 1 + 1 = 2
                sub_topic += 2 

                # Scraping the data into pairs {sub_topic : data}
                data  = sel.css(f'div.free-form-content__content#{topics_of_interest[topic]} > div:nth-child({sub_topic})')
                key   = data.css('h3 > a::text').extract_first()
                value = data.css('p').extract()[0].replace('<strong>', '').replace('</strong>', '').replace('<p>', '').replace('</p>', '').split('<br><br>')

                # Adding a prefix to the key to keep record of topics
                if topics_of_interest[topic] == 'transnational-issues':
                      key   = 'iss_' + key    
                else: key   = f'{topics_of_interest[topic][:3]}_' + key
                
                # Adding pair to results
                pair = {key : value}
                results.update(pair)
        
        # Create a pandas DataFrame of the results, use orient to avoid uneven column lengths, transpose deals with empty cells
        if transpose == True:
            results = pd.DataFrame.from_dict(results, orient='index').transpose()
        else:
            results = pd.DataFrame.from_dict(results, orient='index') 
    
        # Export the results into a .csv file, seperate with semi-colon for future use, all rows include country name
        results['Country'].ffill(inplace=True)

        # Append = True
        if append == True:
            
            # Appending the results into one DataFrame
            if len(appended_results) == 0: 
                appended_results = results
            else: appended_results = appended_results.append(results, ignore_index = False)
            
            if (countries[-1].replace('-',' ') == country.lower()) and (topics_of_interest[-1] == topics_of_interest[topic]) and (sub_topics[-1] == sub_topics[sub_topic -2]):
                print('Scrape complete')
                appended_results.to_csv(f"CIA_Factbook_{append_name}.csv", sep=';', index_label='index')
        
        if append == False:
            print('Scrape complete')
            results.to_csv(f"CIA_Factbook_{country}.csv", sep=';', index_label='index')



