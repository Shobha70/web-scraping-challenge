from splinter import browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

def init_browser():
    
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = browser('chrome', **executable_path, headless=False)

def scrape():

    browser = init_browser()
    collection.drop()

    # NASA Mars News Webpage
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)   

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    nt = soup.find('div', class_='list_text')
    np = soup.find('div', class_='article_teaser_body')
    news_title = nt.a.text
    news_p = np.text

    # JPL Mars Space Webpage
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    image_url = soup.find('img', class_='headerimage fade-in')['src']
    featured_image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/' + image_url
    

    # Mars facts URL
    url = 'https://space-facts.com/mars/'

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')

    df = pd.DataFrame(columns=['Feature','Value'])
    for row in soup.findAll('table')[0].tbody.findAll('tr'):
        first_column = row.findAll('td')[0].text.strip(": ")
        second_column = row.findAll('td')[1].text

        df = df.append({'Feature' : first_column,
                    'Value': second_column}, ignore_index=True)

    df.to_html('mars_table.html')

    # Mars hemispheres title and image
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    hemisphere_image_urls = []
    for table in soup.findAll('div', class_='accordian'):    
        for list in soup.findAll('div', class_='item'):
            title_img_dict = {}
            url = 'https://astrogeology.usgs.gov/' + list.a.get('href')
            response = requests.get(url)
            # Create BeautifulSoup object; parse with 'html.parser'
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h2', class_='title')
            title_img_dict["title"] = title.text
        
        
            image = soup.find('div', class_='downloads')
        
        
            title_img_dict["img_url"] = image.a['href']
        
            hemisphere_image_urls.append(title_img_dict)


    # Close the browser after scraping
    browser.quit()            

    # Creates a dict and collection in the database
    mars_data ={
		'news_title' : news_title,
		'summary': news_p,
        'featured_image': featured_image_url,
		'fact_table': '',
		'hemisphere_image_urls': hemisphere_image_urls        
        }

    collection.insert(mars_data)    

