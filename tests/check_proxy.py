import traceback
from fake_useragent import UserAgent
import requests

proxies = {'http': 'http://192.168.0.113:11221', 'https': 'http://192.168.0.113:11221'}


import cloudscraper

scraper = cloudscraper.create_scraper()  # returns a requests.Session object
url = "https://www.medchemexpress.com/peptides.html"
response = scraper.get(url)
print(response.url)
# print(response.text)