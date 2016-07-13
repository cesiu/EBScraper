# Renders a pickled index.
# author: Christopher (cesiu)
# version: 13 July 2016

from bs4 import BeautifulSoup
import urllib2
import string
import pickle
import os
from eb_scraper import IndexEntry

def main():
    if "indexed.p" in os.listdir(os.getcwd()):
        entries = pickle.load(open("indexed.p", "rb"))
        base_url = "http://www.eurobricks.com/forum/index.php?showtopic="

        for key, entry in entries.iteritems():
            print "[url=\"%s%s\"][img]%s[/img][/url] [url=\"%s%s\"][i]%s[/i][/url], by %s" \
                  % (base_url, entry.topic_id, entry.img_url, base_url, entry.topic_id, entry.title, entry.author)

if __name__ == "__main__":
    main()
