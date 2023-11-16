from proxymanager import ProxyManager
from config import DB_CONFIG
from databaze import Databaze
from bs4 import BeautifulSoup
import requests
import random
import re
import time

class WebScraper:
    def __init__(self, base_url, category):
        self.base_url = base_url
        self.category = category
        self.text_list = []
        if category not in WebScraper.category():
            raise ValueError("špatná kategorie")
# Nastavení databáze
# Vstup do databáze
        databaze = Databaze(DB_CONFIG['host'], DB_CONFIG['username'], DB_CONFIG['password'], DB_CONFIG['database'])
        self.databaze = databaze
        databaze.enter()
# Přijatelné kategorie
    @staticmethod
    def category():
        return ["Mléčné výrobky", "OZ", "Maso", "Chlazené", "Alkohol", "Nealko", "GR zbytek", "Mražené", "Sladké", "Pečení", "Děti", "Prádelna", "Toaletní papír", "Úklid", "Péče o tělo", "Péče o vlasy", "Péče o pleť", "Dentální hygiena", "Dámská hygiena", "Ostatní HB", "Sezóna", "Pečivo", "Mazlíčci", "Ostatní"]

# Vrátí URL na stránky v jednotlivé kategorii a zároveň URL na samotné produkty
    def get_links(self, soup, class_name):
        links = []
        page_links = soup.find_all(class_=class_name)
        for link in page_links:
            if 'href' in link.attrs:
                links.append(self.base_url + link['href'])
        return list(set(links))
# Získává chtěná data, upravý je a vrátí v seznamu
    def data(self, soup, link):
        product_info = soup.find_all(class_="row py-4 px-1 position-relative zbozi-nabidka")
        time.sleep(10)
        if len(product_info) == 0:
            time.sleep(5)
            product_info = soup.find_all(class_="row py-4 px-1 position-relative zbozi-nabidka")
        for product in product_info:
            data_bs_content = product.find(attrs={"data-bs-content": True})
            store = BeautifulSoup(data_bs_content['data-bs-content'], 'html.parser').get_text() if data_bs_content else None
            if store is None:
                store = product.find(class_="col-12 fs-18 fs-m-15 fw-bold mb-0").text
            if store == "Albert Hypermarket" or store == "Lidl":
                to_date_element = product.find("p", class_="mb-0 text-muted fs-10 mb-1", itemprop="priceValidUntil")
                date = to_date_element["content"] if to_date_element else None
                product_name_element = soup.find("h1", class_="nadpis-zbozi", itemprop="name")
                name = product_name_element.text if product_name_element else None
                product_price_element = product.find(class_="dispNone", itemprop="price")
                price = product_price_element["content"] if product_price_element else None
                product_details_element = soup.find("p", class_="p-3 border-0 rounded-16 bg-light fs-14")
                product_details = product_details_element.text if product_details_element else None
                product_picture_element = soup.find(class_="col-md-6 col-12 bg-white rounded-8 d-flex align-self-center product-detail-image").img
                picture = product_picture_element['src'] if product_picture_element and 'src' in product_picture_element.attrs else None
                ean_array = re.findall(r"\d{6,}", product_details) if product_details else ''
                ean = ean_array[0] if ean_array else ''
                etc = 'vybrané druhy' if 'vybrané druhy' in (name or '') else ''
                if etc:
                    name = name.replace('vybrané druhy', '').strip()
                product_note_element = product.find("p", class_="mb-0 text-muted fs-10 col-12")
                bonus_card = product_note_element.text if product_note_element is not None else ''

                self.text_list.append([picture, name, link, etc, price, bonus_card, date, ean, store, self.category])
    
# Spustí předešlé 2 funkce
# Vystupuje z databáze
    def scrape(self, url):
        USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/86.0.4240.93 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
    ]
        rounds = 3
        firstRequest = False
        secondRequest = 0
        thirdRequest = 0
        links1 = []
        links2 = []
        proxy_manager = ProxyManager(self.base_url)
        working_proxies = self.databaze.get_data_just_proxy()
        self.databaze.close()
        while firstRequest == False and len(links2) != secondRequest and len(links2) != secondRequest or rounds != 0:
            for proxy in working_proxies:
                try:
                    headers = {"User-Agent": random.choice(USER_AGENTS)}
                    proxy_auth = proxy_manager.get_proxy_auth(proxy)
                    if firstRequest ==  True:
                        pass
                    else:
                        response = requests.get(url, proxies=proxy_auth, timeout=25, headers=headers)
                        soup = BeautifulSoup(response.content, "html.parser")
                        error_message = soup.find("p", class_="col-12 alert alert-danger")
                        if error_message:
                            continue
                        if 'Non-compliance ICP Filing' in soup.text:
                            continue
                        links1 = self.get_links(soup, "fs-18 fs-m-15 fw-bold mb-1")
                        if links1 == []:
                            continue
                        links2 = self.get_links(soup, "page-link")
                        firstRequest = True
                except requests.exceptions.RequestException as ex:
                    if firstRequest:
                        pass
                    continue

                try:
                    if len(links2) == secondRequest:
                        pass
                    else:
                        for link in links2:
                            headers = {"User-Agent": random.choice(USER_AGENTS)}
                            response = requests.get(link, proxies=proxy_auth, timeout=25, headers=headers)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, "html.parser")
                                links1.extend(self.get_links(soup, "fs-18 fs-m-15 fw-bold mb-1")) 
                                secondRequest += 1
                except requests.exceptions.RequestException:
                    continue
                if len(links2) == secondRequest:
                    try:
                        for link in links1:
                            headers = {"User-Agent": random.choice(USER_AGENTS)}
                            response = requests.get(link, proxies=proxy_auth, timeout=25, headers=headers)
                            soup = BeautifulSoup(response.content, "html.parser")
                            self.data(soup, link)
                            thirdRequest += 1
                            if thirdRequest == len(set(links1)):
                                return self.text_list
                    except requests.exceptions.RequestException:
                        if thirdRequest == len(set(links1)):
                            return self.text_list
                        continue
            rounds -= 1
        return self.text_list
