from urllib.parse import urljoin
import urllib.request
from time import sleep
import pymongo
from bs4 import BeautifulSoup

url = 'https://www.avito.ru'
BASE_URL = 'https://www.avito.ru/krasnodar/kvartiry/prodam'


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def get_page_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    paggination = soup.find('div', class_='pagination-pages clearfix')
    return int(paggination.find_all('a', href=True)[-1]['href'][-3:])

# def parse_autor (html):
#     soup = BeautifulSoup(html, 'html.parser')
#     user = {
#         "URL" : urljoin(url,soup.find('div', class_='seller-info-value').find('a', href=True)['href']),
#         "Name" : soup.find('div', class_='seller-info-value').find('a', href=True).text
#              }
#     return user

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    work_item = soup.find("ul",class_ = "item-params-list").find_all("li",class_ = "item-params-list-item")
    data_page = []
    for item in work_item:
        data_page.append(item.text)
    user_desc = {
        "desc": data_page,
        "URL": urljoin(url, soup.find('div', class_='seller-info-value').find('a', href=True)['href']),
        "Name": soup.find('div', class_='seller-info-value').find('a', href=True).text
    }
    return user_desc

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    work_item = soup.find("div",class_ = "index-root-2c0gs").find_all("div",class_= "iva-item-body-NPl6W")

    data = []
    for item in work_item:
        data = {

            'Title': item.find('h3').text,
            'URL': urljoin(url,item.find('a', href=True)['href']),
            'Price': item.find('span', class_="price-text-1HrJ_ text-text-1PdBw text-size-s-1PUdo").text,
            'Adress':item.find('span',class_='geo-address-9QndR text-text-1PdBw text-size-s-1PUdo').text,
            'Desc_User': parse_page(get_html(urljoin(url,item.find('a', href=True)['href']))),
            # 'User': parse_autor(get_html(urljoin(url, item.find('a', href=True)['href'])))

        }
    return data


def save(data):
    collection = db["Avito"]
    collection.insert_one(data)

def main():
    total_pages_words = get_page_count(get_html(BASE_URL))

    print('Всего найдено %d страниц...' % total_pages_words)

    try:
        for page in range(1, total_pages_words + 1):
            print('Парсинг %d%% (%d/%d)' % (int(float(page) / float(total_pages_words) * 100), page, total_pages_words))
            projects = (parse(get_html(BASE_URL + "?p=%d" % page)))
            save(projects)
            sleep(10)
    finally:
        print('Сохранение...')

if __name__ == '__main__':
    mongo_url = "mongodb://localhost:27017"
    client = pymongo.MongoClient(mongo_url)
    db = client["gb_parse_16_04_21"]
    main()