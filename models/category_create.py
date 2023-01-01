import requests
from bs4 import BeautifulSoup
from progressbar import progressbar

from config.settings import settings
from models.dump_category import check_category
from tasks import category_maker

turk_translate = settings.turk_translate

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
    
    category_list = check_category()
    
    for element in progressbar(page_element):

        # Category's Title and ID
        main_element = element.find('a', class_='nav-link')
        element_title = turk_translate.translate((main_element.text).strip())
        sub_element = element.find('div', class_='list-group')
        sub_categories = sub_element.find_all('a')
        for sub in sub_categories:
            sub_page = s.get(f'https://toptanci.com/{sub.attrs["href"]}')
            print(
                f'New page request has been made | Response: {sub_page.status_code}')
            sub_main_soup = BeautifulSoup(sub_page.content, "html.parser")
            sub_main_element = sub_main_soup.select('ul.list-group.list-group-flush')[1]
            sub_main_element_link = sub_main_element.find_all('a')
            for sub_link in sub_main_element_link:                
                sub_link_title = turk_translate.translate((sub_link.text).strip())            
                category_maker(sub, sub_link_title, category_list)

              