import time
import urllib.request

from threading import Thread
from bs4 import BeautifulSoup

from redis_scheduler import RedisScheduler
from logger import Logger

ROOT_URL = 'https://www.amazon.com/Best-Sellers/zgbs'

class Crawler:

    def __init__(self, scheduler, tag):
        self.scheduler = scheduler
        self.logger = Logger(tag)

    def start(self):
        while True:
            raw_url = self.scheduler.popURL()
            if raw_url is None:
                self.logger.log("No URL left to crawl. ")
                time.sleep(1)
                continue

            category, url = raw_url

            try:
                with urllib.request.urlopen(url) as response:
                    self.logger.log("Crawling " + url)
                    content = response.read()
                    doc = BeautifulSoup(content, 'html.parser')

                    if category == 'index':
                        self.process_index(url, doc)
                    elif category == 'leaf_index':
                        self.process_leaf_index(url, doc)
                    elif category == 'index_page':
                        self.process_index_page(url, doc)
                    elif category == 'item':
                        self.process_item(url, doc)
                    else:
                        raise RuntimeError('Unknown category: ' + category)
            except Exception as e:
                self.logger.exception(e)
                self.scheduler.pushURL(category, url)

    def process_index(self, url, doc):
        targets = doc.select('span.zg_selected')
        assert(len(targets) == 1)

        list = targets[0].parent.parent.ul
        for li in list.find_all('li'):
            self.scheduler.pushURL('leaf_index', li.a['href'])

    def process_leaf_index(self, url, doc):
        paginations = doc.select('.zg_pagination')

        if len(paginations) == 0:
            self.scheduler.pushURL('index_page', url)
        else:
            for page in paginations[0].find_all('li'):
                self.scheduler.pushURL('index_page', page.a['href'])

    def process_index_page(self, url, doc):
        results = []

        for item in doc.find_all('div', class_='zg_itemWrapper'):
            try:
                price_tags = item.select('.a-color-price')
                rating_tags = item.select('.a-icon-star')

                price_tag = None if len(price_tags) == 0 else price_tags[0]
                rating_tag = None if len(rating_tags) == 0 else rating_tags[0]

                results.append({
                    'category': doc.select('.category')[0].string,
                    'link': item.div.a['href'],
                    'title': item.div.a.div.img['alt'],
                    'image': item.div.a.div.img['src'],
                    'price': None if price_tag is None else price_tag.string,
                    'rating': None if rating_tag is None else rating_tag.span.string,
                })
            except Exception as e:
                self.logger.exception(e)

        self.scheduler.commitResults(results)


if __name__ == '__main__':
    def worker(index):
        Crawler(RedisScheduler([
            ('index', ROOT_URL)
        ], 'localhost', 6379, 0), 'WORKER ' + str(index)).start()

    threads = []

    for i in range(4):
        thread = Thread(target=worker, args=(i,))
        thread.start()
        threads.append(thread)

    for i in range(len(threads)):
        threads[i].join()
