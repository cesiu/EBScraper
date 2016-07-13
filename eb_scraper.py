# An experiment in using BeautifulSoup to scrape selected threads from forums.
# author: Christopher (cesiu)
# version: 13 July 2016

from bs4 import BeautifulSoup
import urllib2
import string

def main():
    base_url = "http://www.eurobricks.com/forum/index.php?showforum=86"

    for start in range(0, 30, 30): 
        page = urllib2.urlopen("%s&st=%s" % (base_url, str(start)))
        soup = BeautifulSoup(page.read(), "lxml")

        print "Scraping %s..." % soup.title.string
        
        for topic in soup.find_all(class_="col_f_content"):
            title = topic.find(itemprop="name").string
            link = topic.find(class_="topic_title")["href"]
            tags = [tag.contents[0].string if tag.find("span") else tag.string \
                    for tag in topic.find_all(attrs = {"data-tooltip": True})]

            if (("moc" in string.lower(title) or hasTag(tags, "moc")) \
                and not ("wip" in string.lower(title) or hasTag(tags, "wip")) \
                and not isPinned(topic)):
                print"\n-----\n"
                print title
                print link
                print tags

def hasTag(tags, key_tag):
    return key_tag in (string.lower(raw_tag.strip()) for raw_tag in tags)

def isPinned(topic):
    return "Pinned" in [badge.string for badge in \
            topic.find_all(class_="ipsBadge ipsBadge_green")]

if __name__ == "__main__":
    main()
