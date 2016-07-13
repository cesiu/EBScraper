# An experiment in using BeautifulSoup to scrape selected threads from forums.
# author: Christopher (cesiu)
# version: 13 July 2016

from bs4 import BeautifulSoup
import urllib2

def main():
    base_url = "http://www.eurobricks.com/forum/index.php?showforum=86"

    for start in range(0, 30, 30): 
        page = urllib2.urlopen("%s&st=%s" % (base_url, str(start)))
        soup = BeautifulSoup(page.read(), "lxml")

        print soup.title
        
        for topic in soup.find_all(class_="col_f_content"):
            print "\n-----\n"
            print topic.find(itemprop="name").string
            print topic.find(class_="topic_title")["href"]

if __name__ == "__main__":
    main()
