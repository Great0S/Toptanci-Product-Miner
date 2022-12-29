import json
import logging
import os
import re
from logging import config

import requests
from bs4 import BeautifulSoup
from rich.progress import Progress

from config.logger import log_config
from app.tasks import create_product, ts


config.dictConfig(log_config)
logger = logging.getLogger('mainLog')

products_link = {"Bijouterie": [], "Accessory": [], "Cosmetic": [], "Souvenir": [], "party material": [
], "Textile": [], "Natural Stone & Jewelry Materials": [], "Packaging & Showcase Aks.": []}
products = {"Bijouterie": [], "Accessory": [], "Cosmetic": [], "Souvenir": [], "party material": [
], "Textile": [], "Natural Stone & Jewelry Materials": [], "Packaging & Showcase Aks.": []}
URL = 'https://toptanci.com/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
json_data = None

def toptanciScraper():
    try:
        with Progress() as progress:

            task1 = progress.add_task("[red]Categories")
            task2 = progress.add_task("[green]Sub-Categories")
            task3 = progress.add_task("[cyan]Pages")

            session = requests.Session()
            session.headers = headers
            page = session.get(URL, headers=headers)
            logger.info(
                f'New page request has been made | Response: {page.status_code}')
            soup = BeautifulSoup(page.content, "html.parser")
            result = soup.find('body')
            navBar = result.find(class_="navbar-nav")
            page_element = navBar.find_all("li", class_='darken-onshow')
            page_element_count = len(page_element)
            logger.info(f'Categories found count: {len(page_element)}')
            main_count = 0
            
            for element in progress.track(page_element, task_id=0, total=page_element_count):
                
                if os.path.exists('dumps/unprocessed.json'):
                    break
                
                # Category's Title and ID
                main_element = element.find('a', class_='nav-link')
                element_title = ts.translate((main_element.text).strip())
                sub_element = element.find('div', class_='list-group')
                sub_categories = sub_element.find_all('a')
                sub_categories_count = len(sub_categories)

                logger.info(f'Category being processed: {element_title}')
                logger.info(f'Pulling products links')
                sub_data = []

                for sub in progress.track(sub_categories, task_id=1, total=sub_categories_count):
                    sub_link = URL+sub.attrs['href']
                    sub_name = ts.translate((sub.text).strip())
                    ListResponse = session.get(sub_link, headers=headers)
                    sub_soup = BeautifulSoup(
                        ListResponse.content, "html.parser")
                    sub_result = sub_soup.find('body')
                    elemen_page_nav_count = int(sub_result.find(
                        'div', class_='paging').attrs['data-pagecount'])
                    links = []

                    for offset in progress.track(range(1, elemen_page_nav_count+1, 1), task_id=2, total=elemen_page_nav_count):
                        ProductListResponse = session.get(
                                f'{sub_link}?sayfa={offset}', headers=headers)
                        element_sub_soup = BeautifulSoup(
                            ProductListResponse.content, "html.parser")
                        element_sub_result = element_sub_soup.find('body')
                        element_sub = element_sub_result.find(
                            class_='col-md-10 col-12')
                        element_sub_links = element_sub.contents[7].find_all(
                            "div", class_='productCard')
                        element_sub_links_count = len(element_sub_links)

                        for sub_links in element_sub_links:
                            sub_links = URL + \
                                re.sub(
                                    '/', '', sub_links.contents[1].attrs['href'])
                            links.append(sub_links)
                    sub_data.append({f"{sub_name}": links})

                products_link[element_title].append(sub_data)
                save_data(products_link, element_title, 'unprocessed')
            
            open_json = open('dumps/unprocessed.json', 'r',encoding='utf-8')
            js_data = json.load(open_json) 
            for size in js_data.values():
                for sub_size in size:
                    for sub_size_sub in sub_size:
                        for sub_sub in sub_size_sub.values():
                            main_count += len(sub_sub)
                    
            logger.info(f'Pulled products links total: {main_count}')
            logger.info(f'Processing products start')

            task4 = progress.add_task("[purple]Scraping categories")
            task5 = progress.add_task("[pink]Scraping sub-categories")
            task6 = progress.add_task("[blue]Scraping Items...")

            for product in progress.track(js_data, task_id=3, total=len(products_link)):
                for dum, link in enumerate(js_data[product]):
                    for item in progress.track(link, task_id=4, total=len(link)):
                        for item_name in item:
                            for item_link in progress.track(item[item_name], task_id=5, total=main_count):
                                try:
                                    product_link = session.get(item_link)
                                    product_soup = BeautifulSoup(
                                        product_link.content, "html.parser")

                                    select_sub = product_soup.select(
                                        'ol.breadcrumb.text-truncate')[0]
                                    select_sub2 = select_sub.select(
                                        'li.breadcrumb-item')
                                    if len(select_sub2) == 4:
                                        sub_main_category = ts.translate(
                                            re.sub('\n', '', select_sub2[2].text).strip())
                                    else:
                                        sub_main_category = None
                                    product_name = ts.translate(product_soup.find(
                                        'div', class_='col-10').contents[1].text)
                                    attrs_list = product_soup.select(
                                        'table.table.table-hover.table-sm')
                                    atrributes = {
                                        "color": [], "price": [], "stock": [], "code": []}
                                    for attr in attrs_list:
                                        stok_yok = attr.find('div', text=re.compile("Stok Yok"))
                                        if stok_yok:
                                            break                                    
                                        color_attr = ts.translate(attr.find(
                                            'td', attrs={'style': 'width:30%;'}).text)
                                        price_attr = re.sub(',', '.', re.sub('\₺', '', attr.find(
                                            'div', text=re.compile(r'\₺')).text).strip())
                                        stock_attr = int(
                                            attr.find('strong', text=re.compile(r'\d+')).text)
                                        code_attr = int(
                                            attr.find('td', class_="", text=re.compile(r'\s\d+\s|\d+')).text)

                                        atrributes['color'].append(color_attr)
                                        atrributes['price'].append(price_attr)
                                        atrributes['stock'].append(stock_attr)
                                        atrributes['code'].append(code_attr)

                                    product_desc = ts.translate(re.sub(r'\w+;', '', product_soup.select(
                                        'div.p-3.bg-white.border.rounded-3')[0].contents[1].contents[0].text).strip())
                                    product_images = product_soup.select(
                                        'img.img-fluid.btnVariantSmallImage')
                                    images = {"color": [], "link": []}
                                    for image in product_images:
                                        img_link = image.attrs['data-src']
                                        img_color = image.attrs['alt']

                                        images['color'].append(img_link)
                                        images['link'].append(img_color)

                                    products_update = {"sub-category": item_name, "sub-sub-category": sub_main_category,
                                                       "name": product_name, "images": images, "descr": product_desc, "attrs": atrributes}
                                    products[product].append(products_update)
                                    save_data(products, product, 'data')
                                    
                                except (Exception, IndexError) as e:
                                    logger.error(
                                        f"Product error: {e} | Status: {product_link.status_code} | Reason: {product_link.reason} | Link: {item_link}")
                                    continue
            
            logger.info("All data has been processed")
            return
    except requests.exceptions.ChunkedEncodingError:
        time.sleep(1)


def save_data(data, main, files):
    global json_data
    File_path = f'dumps/{files}.json'
    if os.path.exists(File_path):
        
        # Dumping categories into a dict var
        open_json = open(File_path, 'r',encoding='utf-8')
        json_data = json.load(open_json)  
        if len(data[main]) == len(json_data[main]):
            pass
        else:     
            json_data[main].append(data[main][0]) 
            with open(File_path, 'w', encoding='utf-8') as file:
                file.truncate()
                json.dump(data, file, ensure_ascii=False)
            file.close()   
    else:
        with open(File_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
        file.close()
        open_json = open(File_path, 'r',encoding='utf-8')
        json_data = json.load(open_json)
        
    return json_data



def main():
    global json_data
    
    from threading import Thread
    new_thread = Thread(target=toptanciScraper)
    new_thread.start()
    create_product(json_data)


# clearing the console from unnecessary
def cls(): return os.system("cls")


cls()

logger.info('New TOPTANCI session has been started')

if __name__ == '__main__':
    import time
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    logger.info("Tasks executed in {elapsed:0.2f} seconds.")
