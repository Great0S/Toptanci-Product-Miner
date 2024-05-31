import glob
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
from rich.progress import Progress, SpinnerColumn, TextColumn
from tqdm import tqdm

from config.settings import settings
from tasks.create_products import create_product

logger = settings.logger

URL = 'https://toptanci.com/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}
LINKS_FILE = 'dumps/unprocessed.json'
DATA_FILE = 'dumps/data.json'
MEDIA_FOLDER = 'media/'

products = []
links = []

def configure_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 520])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers = HEADERS
    return session

def save_data(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_links(session, page_element):
    links = []
    main_element = page_element.find('a', class_='nav-link')
    sub_element = page_element.find('div', class_='list-group')
    sub_categories = sub_element.find_all('a')

    for sub in sub_categories:
        sub_link = URL + sub.attrs['href']
        sub_name = sub.text.strip()
        response = session.get(sub_link)
        sub_soup = BeautifulSoup(response.content, "html.parser")
        elemen_page_nav_count = int(sub_soup.find('div', class_='paging').attrs['data-pagecount'])

        for offset in range(1, elemen_page_nav_count + 1):
            response = session.get(f'{sub_link}?sayfa={offset}')
            sub_soup = BeautifulSoup(response.content, "html.parser")
            product_cards = sub_soup.select('div.productCard a')

            for product_card in product_cards:
                links.append(URL + product_card['href'])

    return links

def extract_data(session, item_link):
    product = {}
    response = session.get(item_link)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        breadcrumbs = soup.select('ol.breadcrumb.text-truncate li.breadcrumb-item')
        main_category = breadcrumbs[1].text.strip()
        sub_category = breadcrumbs[2].text.strip() if len(breadcrumbs) > 3 else None

        product_name = soup.select_one('div.col-10 h1').text
        attributes_table = soup.select('table.table-hover.table-sm')
        attributes = {"color": [], "price": [], "stock": [], "code": []}

        for attr in attributes_table:
            if attr.find(text=re.compile("Stok Yok")):
                continue
            attributes['color'].append(attr.select_one('td[style="width:30%;"]').text)
            attributes['price'].append(attr.find(text=re.compile(r'\₺')).text.strip().replace('₺', '').replace(',', '.'))
            attributes['stock'].append(int(attr.find(text=re.compile(r'\d+')).text))
            attributes['code'].append(int(attr.find(text=re.compile(r'\s\d+\s|\d+')).text))

        product_desc = soup.select_one('div.p-3.bg-white.border.rounded-3 p').text.strip()
        product_images = soup.select('img.img-fluid.btnVariantSmallImage')
        images = {"color": [img['alt'] for img in product_images], "link": [img['data-src'] for img in product_images]}

        product = {
            "link": item_link,
            "main-category": main_category,
            "sub-category": sub_category,
            "name": product_name,
            "images": images,
            "descr": product_desc,
            "attrs": attributes
        }

    except Exception as e:
        logger.error(f"Error extracting data from {item_link}: {e}")

    return product

def toptanci_scraper():
    session = configure_session()
    response = session.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    categories = soup.select('nav.navbar-nav li.darken-onshow')

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task(description="Extracting links...", total=None)

        if not os.path.exists(LINKS_FILE):
            with ThreadPoolExecutor(max_workers=100) as executor:
                links.extend(executor.map(lambda cat: extract_links(session, cat), categories))
            save_data(links, LINKS_FILE)
        else:
            with open(LINKS_FILE, 'r', encoding='utf-8') as file:
                links.extend(json.load(file))

        progress.remove_task(task)
        task = progress.add_task(description="Processing links...", total=None)

        if not os.path.exists(DATA_FILE):
            with ThreadPoolExecutor(max_workers=5) as executor:
                products.extend(executor.map(lambda link: extract_data(session, link), links))
            save_data(products, DATA_FILE)
        else:
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                products.extend(json.load(file))

        progress.remove_task(task)

def main():
    start_time = time.time()
    toptanci_scraper()
    logger.info(f"Scraped in {(time.time() - start_time):.2f} seconds")

    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    with ThreadPoolExecutor(max_workers=3) as executor:
        list(tqdm(executor.map(create_product, json_data), total=len(json_data)))

    for file in glob.glob(f'{MEDIA_FOLDER}*'):
        os.remove(file)

if __name__ == '__main__':
    logger.info('New TOPTANCI session has been started')
    main()
    logger.info('TOPTANCI session has been completed')
