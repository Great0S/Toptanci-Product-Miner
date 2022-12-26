


import re
from bs4 import BeautifulSoup
import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

try:
    product_link = requests.get('https://toptanci.com/tuylu-kikirdak-kupe-u-223347', headers=headers)
    product_soup = BeautifulSoup(product_link.content, "html.parser")
except Exception as e:
    print(
        f"Product link error: {e} | Status: {product_link.status_code} | Reason: {product_link.reason}")
    
select_sub = product_soup.select('ol.breadcrumb.text-truncate')[0]
select_sub2 = select_sub.select('li.breadcrumb-item')
if len(select_sub2) == 4:
    sub_main_category = re.sub('\n','',select_sub2[2].text).strip()
else:
    sub_main_category = None
product_name = product_soup.find('div', class_='col-10').contents[1].text
attrs_list = product_soup.select('table.table.table-hover.table-sm')
atrributes = {"color": [], "price": [], "stock": [], "code": []}
for attr in attrs_list:
    color_attr = attr.contents[1].contents[1].contents[3].text
    price_attr = re.sub(',','.',re.sub('\₺','',attr.contents[3].contents[1].contents[5].contents[0].text).strip())
    stock_attr = int(attr.contents[3].contents[1].contents[7].contents[0].text)
    code_attr = int(re.sub('\n','',attr.contents[3].contents[1].contents[1].contents[0].text))
    
    atrributes['color'].append(color_attr)
    atrributes['price'].append(price_attr)
    atrributes['stock'].append(stock_attr)
    atrributes['code'].append(code_attr)
    
product_desc = re.sub(r'\w+;','',product_soup.select('div.p-3.bg-white.border.rounded-3')[0].contents[1].contents[0].text).strip()
select3 = product_soup.body.main.select('div.row')
product_images = product_soup.find_all('img', class_="img-fluid")
images = {"color": [], "link": []}
for image in product_images:
    img_link = image.attrs['data-src']
    img_color = image.attrs['alt']
    
    images['color'].append(img_link)
    images['link'].append(img_color)
print('s')