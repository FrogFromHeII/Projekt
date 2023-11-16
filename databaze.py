import mysql.connector as dblib
from datetime import datetime
import time

class Databaze:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
# Funkce vstupu
    def enter(self):
        self.db = dblib.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database 
        )
        self.cursor = self.db.cursor()
        return self
# Funkce výstupu
    def close(self):
        self.cursor.close()
        self.db.close()
# Přidá data do datábaze a zároveň zkontroluje duplicitu
    def add_data(self, data):
        query = "SELECT * FROM produkty WHERE name=%s AND store=%s AND price=%s AND date=%s"
        values = (data[1], data[8], data[4], data[6])
        self.cursor.execute(query, values)
        results = self.cursor.fetchall()
        if len(results) == 0:
            add_data = (f"INSERT INTO produkty (picture, name, link, etc, price, bonus_card, date, ean, store, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            self.cursor.execute(add_data, data)
            self.db.commit()
# Odstraní data z databáze se starým datem
    def remove_old_data(self):
        today = datetime.today().strftime('%Y-%m-%d')
        select_query = "SELECT * FROM produkty WHERE date < %s"
        self.cursor.execute(select_query, (today,))
        self.cursor.fetchall()
        delete_query = "DELETE FROM produkty WHERE date < %s"
        self.cursor.execute(delete_query, (today,))
        self.db.commit()
# Vrátí hodnoty z databáze v seznamu s daným pořadím a tvarem
    def get_data(self):
        query = "SELECT id, picture, name, link, etc, price, bonus_card, DATE_FORMAT(date, '%d.%m') as date, ean, store, category FROM produkty"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        data = []
        for record in records:
            data.append({
                'id' : record[0],
                'picture': record[1],
                'name': record[2],
                'link': record[3],
                'etc': record[4],
                'price': record[5],
                'bonus_card': record[6],
                'date': record[7],
                'ean': record[8],
                'store': record[9],
                'category': record[10]
            })
        return data
# Databáze Proxy 
# Přidání dat
    def add_data_proxy(self, data):
        add_data = (f"INSERT INTO proxy (proxy_address, ttl_hash) VALUES (%s, %s)")
        self.cursor.execute(add_data, data)
        self.db.commit()
# Získání dat
    def get_data_proxy(self):
        self.remove_old_proxy_data()
        query = "SELECT proxy_address, ttl_hash FROM proxy"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        data = []
        for record in records:
            data.append({
                'proxy': record[0],
                'ttl_hash': record[1]
            })
        return data
# Získání pouze proxe adresy, bez časové stopy
    def get_data_just_proxy(self):
        query = "SELECT proxy_address, ttl_hash FROM proxy"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        data = []
        for record in records:
            data.append({
                record[0],
            })
        return data
# Zkontrolování časová stopy a odstranění
    def remove_old_proxy_data(self):
        current_time = time.time()
        query = "SELECT proxy_address, ttl_hash FROM proxy"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        proxies_to_delete = []
        for record in records:
            proxy, timestamp = record
            if current_time - float(timestamp) > 24 * 60 * 60:
                proxies_to_delete.append(proxy)
        for proxy in proxies_to_delete:
            delete_query = "DELETE FROM proxy WHERE proxy_address = %s"
            self.cursor.execute(delete_query, (proxy,))
            self.db.commit()
