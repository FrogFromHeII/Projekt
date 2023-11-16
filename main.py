from flask import Flask, render_template
from databaze import Databaze
from webscraper import WebScraper
from proxymanager import ProxyManager
from config import DB_CONFIG
from multiprocessing import Process
import time
import urllib3

app = Flask(__name__)
databaze = Databaze(DB_CONFIG['host'], DB_CONFIG['username'], DB_CONFIG['password'], DB_CONFIG['database'])
# Web
@app.route("/")
@app.route("/uvod")
def uvodniStranka():
    databaze.enter()
    databaze.remove_old_data()
    produkty = databaze.get_data()
    databaze.close()
    kategorie = WebScraper.category()
    return render_template("index.html", produkty=produkty, kategorie=kategorie)
# Procesy
def process_url(category_url):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    category, url_list = category_url
    for url in url_list:
        scraper = WebScraper("http://www.akcniceny.cz", category)
        data = scraper.scrape(url)
        if data is not None:
            databaze.enter()
            for d in data: 
                databaze.add_data(d)
            databaze.close()
# Hlavní funkce mainu
def job():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    start_time = time.time()
    urls = [
["Mléčné výrobky", [###"]
]
    processes = []
    delay = 0
    for category_url in urls:
        p = Process(target=process_url, args=(category_url,))
        p.start()
        processes.append(p)
        time.sleep(delay)
        delay += 1

    for p in processes:
        p.join()
    end_time = time.time()
    celkem = end_time - start_time
    print(celkem)

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    proxy_manager = ProxyManager("http://www.akcniceny.cz")
    working_proxies = proxy_manager.working_proxy()
    Process(target=job).start()
    app.run()
