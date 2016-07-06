import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

if __name__ == '__main__':
    from modules.crawler import Crawler

    c = Crawler('http://s7.zetaboards.com/Nuzlocke_Forum/')
    print(c.crawl())