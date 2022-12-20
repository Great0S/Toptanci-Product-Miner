import re
from bs4 import BeautifulSoup
from progressbar import progressbar
import requests


requests.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'

page = requests.get('https://toptanci.com/')
print(
    f'New page request has been made | Response: {page.status_code}')
soup = BeautifulSoup(page.content, "html.parser")
result = soup.find(id='main_nav')
page_element = result.find_all("li", recursive=False, limit=6)
print(f'Categories found: {len(page_element)}')
for element in progressbar(page_element):
    # Category's Title and ID
    element_title = re.sub(
        r'\W\d+', '', element.find("a", target="_self").text)
    
    print(element_title)