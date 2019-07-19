# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from db import Db

class Crawler:
    def __init__(self):
        pass

    def getHeaderOpera(self):
        headers_opera = {
            'Host': 'pergamum.ufsc.br',
            'Connection': 'keep-alive',
            'Content-Length': '106',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://pergamum.ufsc.br',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36 OPR/62.0.3331.72',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://pergamum.ufsc.br/pergamum/biblioteca_s/php/login_usu.php?flag=index.php',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': '_ga=GA1.2.853011463.1562811066; _gid=GA1.2.1876703702.1563160699; __utma=235133312.853011463.1562811066.1563285351.1563387230.4; __utmc=235133312; __utmz=235133312.1563002099.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PHPSESSID=7d14e33a7b4e6e0b271332e87f9ef9d6'
        }
        return headers_opera

    def getHeaderFirefox(self):
        headers_firefox = {
            'Host': 'pergamum.ufsc.br',
            'Connection': 'keep-alive',
            'Content-Length': '106',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://pergamum.ufsc.br',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://pergamum.ufsc.br/pergamum/biblioteca_s/php/login_usu.php?flag=index.php',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': '__utmt=1; __utma=235133312.539375779.1563394688.1563394688.1563394688.1; __utmb=235133312.1.10.1563394688; __utmc=235133312; __utmz=235133312.1563394688.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); PHPSESSID=b195ee14a8a4e575c266991ca05e5016; _ga=GA1.2.539375779.1563394688; _gid=GA1.2.1688960623.1563394708; _gat_gtag_UA_10538459_9=1'
        }
        return headers_firefox

    def getUrlLogin(self):
        url_login = "https://pergamum.ufsc.br/pergamum/biblioteca_s/php/login_usu.php"
        return url_login

    def getUrlIndex(self):
        url_index = "https://pergamum.ufsc.br/pergamum/biblioteca_s/meu_pergamum/index.php"
        return url_index

    def crawler(self, matricula, senha):
        __data = {
            'login':matricula,
            'password':senha,
        }

        with requests.Session() as session:
            a = session.post(self.getUrlLogin(), data=__data, headers=self.getHeaderFirefox())
            page = session.get(self.getUrlIndex())
            if page.url == "https://pergamum.ufsc.br/pergamum/biblioteca_s/php/login_usu.php?flag=index.php":
                return False #Se voltou para a pagina de login é porque não conseguiu logar

            soup = BeautifulSoup(page.text, 'html.parser')

            vector_livros = []
            vector_datas = []
            vector_renovacoes = []

            livros = soup.find_all('div', class_='c1')
            for livro in livros:
                livro2 = livro.find_all('a', class_='txt_azul')
                for a in livro2:
                    vector_livros.append(a.get_text().strip()[:50])


            datas = soup.find_all('div', class_ = 'c1')
            for data in datas:
                data2 = data.find_all('td', class_='txt_cinza_10')[3:]
                i = 0
                for a in data2:
                    if i == 0:
                        vector_datas.append(a.get_text().strip())
                    elif i == 1:
                        vector_renovacoes.append(a.get_text().replace("\xa0", "").strip())
                    else:
                        pass
                    i+=1
                    if i == 3:
                        i = 0
            
            db = Db()
            db.insertLivroCrawler(matricula, vector_livros, vector_datas, vector_renovacoes)
            
            return True