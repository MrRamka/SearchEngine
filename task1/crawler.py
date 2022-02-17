from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import os


class Crawler:

    def __init__(self, urls: list, blacklist: list, url_count_limit=150, file_name="index.json"):
        self.blacklist = blacklist
        self.visited_urls = []
        self.urls_to_visit = urls
        self.url_count_limit = url_count_limit
        self.file_name = file_name
        self.file_name_prefix = "source_"
        self.file_name_suffix = ".html"
        self.pages = []
        self.pages_dir = "\\task1\\pages\\"
        Path("task1/pages").mkdir(parents=True, exist_ok=True)
        os.chdir(os.getcwd() + self.pages_dir)

    @staticmethod
    def download_url(url):
        return requests.get(url).text

    @staticmethod
    def get_linked_urls(url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url: str, index):
        if url is not None and not any(url.startswith(x) for x in self.blacklist):
            try:
                html = self.download_url(url)
                for url in self.get_linked_urls(url, html):
                    self.add_url_to_visit(url)
                filename = f'{self.file_name_prefix}{index}{self.file_name_suffix}'
                file_info = {"url": url, "file_name": filename}
                self.pages.append(file_info)
                self.create_source_file(filename, html)
                self.site_index += 1
            except Exception:
                pass

    @staticmethod
    def create_source_file(filename, html):
        file = open(filename, 'wb')
        file.write(html.encode("utf-8", "replace"))
        file.close()

    def run(self):
        self.site_index = 1
        while self.urls_to_visit and self.site_index < self.url_count_limit:
            url = self.urls_to_visit.pop(0)
            print(f'Crawling: {url}')
            self.crawl(url, self.site_index)
            self.visited_urls.append(url)

        os.chdir("../")
        with open(self.file_name, 'w') as file:
            file.write(json.dumps(self.pages))
