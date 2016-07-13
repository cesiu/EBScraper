# An experiment in using BeautifulSoup to scrape selected threads from forums.
# author: Christopher (cesiu)
# version: 13 July 2016

from bs4 import BeautifulSoup
import urllib2

def main():
    page = urllib2.urlopen("http://www.eurobricks.com/forum")
    soup = BeautifulSoup(page.read(), "lxml")

    print soup.title

    for link in soup.find_all('a'):
        print link.get('href')

if __name__ == "__main__":
    main()
