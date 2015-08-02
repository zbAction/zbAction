from Queue import Empty, Queue
import re
from threading import Thread

from bs4 import BeautifulSoup
from sqlalchemy.orm.exc import NoResultFound
import traceback
import urllib2

from models.user import User

class Crawler(object):
    def __init__(self, url, board_key):
        self.url = url
        self.board_key = board_key

    def crawl(self):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        users = Queue()
        uid_regex = re.compile(r'/profile/(\d+)/$')

        page = Queue()
        page.put(1)

        def Worker():
            while True:
                to_scrape = page.get()
                page.put(to_scrape + 1)

                print '{}members/{}/?force_ads'.format(self.url, to_scrape)

                data = opener.open(
                    '{}members/{}/?force_ads'.format(self.url, to_scrape)
                ).read()

                soup = BeautifulSoup(data, 'html.parser')
                links = soup.select('#member_list_full a')

                if len(links) == 0:
                    return

                for link in links:
                    if not link.has_attr('href'):
                        continue

                    href = link['href']
                    uid = uid_regex.findall(href)

                    if len(uid):
                        uid = uid[0]
                        username = link.get_text()

                        data = {
                            'uid': uid,
                            'board_key': self.board_key
                        }

                        user = User.create_from(data)
                        user.name = username

                        users.put(user)

        workers = []

        for x in range(4):
            w = Thread(target=Worker)
            w.daemon = True

            workers.append(w)

            w.start()

        for w in workers:
            w.join()

        ret = []

        try:
            ret.append(users.get())
        except Empty:
            pass

        return ret