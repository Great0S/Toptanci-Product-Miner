from bs4 import BeautifulSoup
from progressbar import progressbar
import requests
from deep_translator import GoogleTranslator
from app.tasks import category_maker

ts = GoogleTranslator(source="tr", target="en")

with requests.Session() as s:
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    page = s.get('https://toptanci.com/')
    print(
        f'New page request has been made | Response: {page.status_code}')
    soup = BeautifulSoup(page.content, "html.parser")
    result = soup.find('body')
    navBar = result.find(class_="navbar-nav")
    page_element = navBar.find_all("li", class_='darken-onshow')
    print(f'Categories found: {len(page_element)}')
    for element in progressbar(page_element):
        
        # Category's Title and ID
        main_element = element.find('a', class_='nav-link')
        element_title = ts.translate((main_element.text).strip())
        sub_element = element.find('div', class_='list-group')
        sub_categories = sub_element.find_all('a')
        for sub in sub_categories:
            category_maker(element_title, sub)

        print(element_title)
