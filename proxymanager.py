from config import DB_CONFIG
from databaze import Databaze
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from threading import Lock
import random
import requests
import time

class ProxyManager:
    def __init__(self, base_url, proxies_file='http.txt'):
        self.base_url = base_url
        self.proxies_file = proxies_file
        self.stop_testing = False
        self.lock = Lock()
        self.successful_tests = 0
# Nastavení databáze
# Vstup do databáze
        databaze = Databaze(DB_CONFIG['host'], DB_CONFIG['username'], DB_CONFIG['password'], DB_CONFIG['database'])
        self.databaze = databaze
        databaze.enter()
# Proxy adresy z http
        with open(self.proxies_file, 'r') as f:
            self.proxies = [line.strip() for line in f]
        self.cache = self.load_cache()
# Hlavní funkce ProxyManager, zjsítí jestli existují a je v databázi dost proxy, když ne, získá nové
# Vystupuje z databáze
    def working_proxy(self):
        data = self.load_cache()
        if len(data) != 0:
            if len(data) < 50:
                working_proxies = []
                with ThreadPoolExecutor(max_workers=80) as executor:
                    results = executor.map(self.test_proxy_with_lock, self.proxies)
                for proxy, result in zip(self.proxies, results):
                    if result:
                        working_proxies.append(proxy)
                self.save_cache()
                self.databaze.close()
                return working_proxies
            else:
                self.databaze.close()
                return data
        else:
            print('working proxy')
            working_proxies = []
            with ThreadPoolExecutor(max_workers=80) as executor:
                results = executor.map(self.test_proxy_with_lock, self.proxies)
            for proxy, result in zip(self.proxies, results):
                if result:
                    working_proxies.append(proxy)
            self.save_cache()
            self.databaze.close()
            return working_proxies
# Získání proxy
    def load_cache(self):
        return {row['proxy']: row['ttl_hash'] for row in self.databaze.get_data_proxy()}
# Uloží proxy
    def save_cache(self):
        for proxy, ttl_hash in self.cache.items():
            self.databaze.add_data_proxy((proxy, ttl_hash))
# Rozebere proxy
    def get_proxy_auth(self, proxy):
        proxy_parts = list(proxy)[0].split(':')
        if len(proxy_parts) == 4:
            ip, port, username, password = proxy_parts
            return {
                'http': f'http://{username}:{password}@{ip}:{port}',
            }
        elif len(proxy_parts) == 2:
            ip, port = proxy_parts
            return {
                'http': f'http://{ip}:{port}',
            }
# Lock pro vlákna
    def test_proxy_with_lock(self, proxy):
        return self.test_proxy(proxy, ttl_hash=self.get_ttl_hash())
# Časová značka
    def get_ttl_hash(self):
        return round(time.time())
# Testování odpovědi proxy adres
    @lru_cache(None)
    def test_proxy(self, proxy, ttl_hash=None, max_working_proxies=180):
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
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        if proxy in self.cache and self.cache[proxy] == ttl_hash:
            return True
        url = self.base_url
        try:
            if self.stop_testing:
                return False
            proxy_auth = self.get_proxy_auth(proxy)
            response = requests.get(url, proxies=proxy_auth, timeout=25, headers=headers)
            success = 200 <= response.status_code < 300
            if success:
                with self.lock:
                    self.successful_tests += 1
                    if self.successful_tests >= max_working_proxies:
                        self.stop_testing = True
                self.cache[proxy] = ttl_hash
            return success
        except requests.exceptions.RequestException as ex:
            return False