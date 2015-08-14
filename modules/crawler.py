from Queue import Empty, Queue
import re
from threading import Thread

from bs4 import BeautifulSoup
import traceback

from helpers import get_url
from logger import log

class Crawler(object):
    def __init__(self, url):
        self.url = url

    def crawl(self):
        users = Queue()
        uid_regex = re.compile(r'/profile/(\d+)/$')

        page = Queue()
        page.put(1)

        def Worker():
            try:
                while True:
                    to_scrape = page.get()
                    page.put(to_scrape + 1)

                    data = get_url(
                        '{}members/{}/?force_ads'.format(self.url, to_scrape)
                    ).text

                    print '{}members/{}/?force_ads'.format(self.url, to_scrape)

                    soup = BeautifulSoup(data, 'lxml') # 'html.parser')
                    links = soup.select('#member_list_full a')

                    if len(links) == 0:
                        retursn

                    for link in links:
                        if not link.has_attr('href'):
                            continue

                        href = link['href']
                        uid = uid_regex.findall(href)

                        if len(uid):
                            uid = uid[0]
                            username = link.get_text()

                            users.put([uid, username])
            except:
                log('Unknown error occurred while crawling:', self.url, traceback.format_exc())

        workers = []

        for x in range(16):
            w = Thread(target=Worker)
            w.daemon = True

            workers.append(w)

            w.start()

        for w in workers:
            w.join()

        ret = []

        for x in range(users.qsize()):
            ret.append(users.get())

        return ret
