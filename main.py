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
    ["Mléčné výrobky", ["http://www.akcniceny.cz/zbozi/albert+lidl/mlecne-vyrobky/"]],
    ["OZ", ["http://www.akcniceny.cz/zbozi/albert+lidl/ovoce/", "http://www.akcniceny.cz/zbozi/albert+lidl/zelenina/"]],
    ["Maso", ["http://www.akcniceny.cz/zbozi/albert+lidl/maso/"]],
    ["Chlazené", ["http://www.akcniceny.cz/zbozi/albert+lidl/uzeniny-lahudky/", "http://www.akcniceny.cz/zbozi/albert+lidl/ostatni-chlazene/"]],
    ["Alkohol", ["http://www.akcniceny.cz/zbozi/albert+lidl/napoje-alkoholicke/"]],
    ["Nealko", ["http://www.akcniceny.cz/zbozi/albert+lidl/napoje-nealkoholicke/", "http://www.akcniceny.cz/zbozi/albert+lidl/teple-napoje/"]],
    ["Pečivo", ["http://www.akcniceny.cz/zbozi/albert+lidl/pecivo/"]],
    ["GR zbytek", ["http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/testoviny/", 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/ryze/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/lusteniny/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/konzervy-instatni-jidla/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/sterilizovane-ovoce-a-zelenina/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/musli-kase-cerealie/']],
    ["Sladké", ["http://www.akcniceny.cz/zbozi/albert+lidl/cukrovinky-pochutiny/"]],
    ["Mražené", ["http://www.akcniceny.cz/zbozi/albert+lidl/mrazene-zbozi/"]],
    ["Pečení", ["http://www.akcniceny.cz/zbozi/albert+lidl/dochucovadla/", 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/mouka/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/cukr/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/olej/', 'http://www.akcniceny.cz/zbozi/albert+lidl/trvanlive/sul/']],
    ["Děti", ["http://www.akcniceny.cz/zbozi/albert+lidl/detska-vyziva/", "http://www.akcniceny.cz/zbozi/albert+lidl/plenky/"]],
    ["Ostatní", ["http://www.akcniceny.cz/zbozi/albert+lidl/ostatni-potraviny/", "http://www.akcniceny.cz/zbozi/albert+lidl/ostatni-ostatni/"]],
    ["Prádelna", ["http://www.akcniceny.cz/zbozi/albert+lidl/praci-prostredky/"]],
    ["Toaletní papír", ["http://www.akcniceny.cz/zbozi/albert+lidl/toaletni-papir-kapesniky/"]],
    ["Úklid", ["http://www.akcniceny.cz/zbozi/albert+lidl/cistici-prostredky/", "http://www.akcniceny.cz/zbozi/albert+lidl/myti-nadobi/"]],
    ["Péče o tělo", ["http://www.akcniceny.cz/zbozi/albert+lidl/pece-o-telo/"]],
    ["Péče o vlasy", ["http://www.akcniceny.cz/zbozi/albert+lidl/pece-o-vlasy/"]],
    ["Péče o pleť", ["http://www.akcniceny.cz/zbozi/albert+lidl/pece-o-plet/"]],
    ["Dentální hygiena", ["http://www.akcniceny.cz/zbozi/albert+lidl/pece-o-zuby/"]],
    ["Dámská hygiena", ["http://www.akcniceny.cz/zbozi/albert+lidl/damska-hygiena/"]],
    ["Ostatní HB", ["http://www.akcniceny.cz/zbozi/albert+lidl/ostatni-drogerie/"]],
    ["Sezóna", ["http://www.akcniceny.cz/zbozi/albert+lidl/sezona/"]],
    ["Mazlíčci", ["http://www.akcniceny.cz/zbozi/albert+lidl/domaci-mazlicci/"]]
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
