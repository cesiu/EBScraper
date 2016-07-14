# An experiment using Beautiful Soup to scrape selected threads from a forum.
# author: Christopher (cesiu)
# version: 0.1

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PIL import Image
import urllib
import urllib2
import string
import pickle
import os
import re

# The base forum URL.
BASE_URL = "http://www.eurobricks.com/forum/index.php"

# Represents one entry in an index.
class IndexEntry:
    def __init__(self, topic_id, title, author, img_url):
        self.topic_id = topic_id
        self.title = title
        self.author = author
        self.img_url = img_url

def main():
    # Maps the subforum names to their id numbers.
    SUBFORUM_IDS = {
        "StarWars": "86",
        "WattosJunkyard": "114",
        "NarEurbrikka": "175",
    }

    # Load the list of already-indexed topics.
    old_entries = {}
    if "indexed.p" in os.listdir(os.getcwd()):
        old_entries = pickle.load(open("indexed.p", "rb"))

    # For every page:
    for start in range(0, 30, 30): 
        # Construct the URL and scrape the page.
        entries = scrape_forum_page("%s?showforum=%s&st=%s" 
         % (BASE_URL, SUBFORUM_IDS["StarWars"], str(start)))
        
        # Find the MOCs that haven't been indexed and scrape them.
        for entry in entries:
            if entry.topic_id in old_entries:
                print "%s (%s) by %s already indexed." \
                      % (entry.title, entry.topic_id, entry.author)
            else:
                print "%s (%s) by %s needs indexing." \
                      % (entry.title, entry.topic_id, entry.author)
                entry.img_url = scrape_topic(entry.topic_id)
                old_entries[entry.topic_id] = entry

    # Save the newly indexed topics.
    pickle.dump(old_entries, open("indexed.p", "wb"))

# Scrapes a page of a forum to find all the MOC topics.
# url - the url of the forum page
# returns a list of IndexEntries
def scrape_forum_page(url):
    ret_urls = []
    # Load the page and initialize the parser.
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    print "Scraping %s..." % soup.title.string
        
    # For every topic on that page:
    for topic in soup.find_all(class_="col_f_content"):
        title = topic.find(itemprop="name").string
        link = topic.find(class_="topic_title")["href"]
        # The author is the first string in this span.
        author = ' '.join(topic.find(class_="desc lighter blend_links") \
                          .contents[0].split()[2:-1])
        # If the tag is used as badge, it isn't wrapped in any tags.
        tags = [tag.contents[0].string if tag.find("span") else tag.string \
                for tag in topic.find_all(attrs = {"data-tooltip": True})]

        # Grab all the non-pinned, non-WIP, MOC topics:
        if (("moc" in string.lower(title) or has_tag(tags, "moc")) \
            and not ("wip" in string.lower(title) or has_tag(tags, "wip")) \
            and not is_pinned(topic)):
            ret_urls.append(IndexEntry(str(link.split('=')[-1]), \
             str(format_title(title)), str(author), None))

    return ret_urls

# Scrapes a topic and saves the first image.
# topic_id - the id of the topic
# returns the URL of the thumbnail generated for the topic
def scrape_topic(topic_id):
    # Load the page and initialize the parser.
    page = urllib2.urlopen("%s?showtopic=%s" % (BASE_URL, topic_id))
    soup = BeautifulSoup(page.read())
    print "   Scraping %s..." % soup.title.string

    # Find the first non-emoticon image in the first post.
    img_url = soup.find(itemprop="commentText") \
                  .find("img", alt="Posted Image")["src"]
    # Define a name for the image, keeping the extension.
    img_name = "%s/%s.%s" % (os.getcwd(), topic_id, img_url.split(".")[-1])

    # Download and open the image.
    (filename, header) = urllib.urlretrieve(img_url, img_name)
    print "   Downloaded %s." % filename
    img = Image.open(img_name)

    # Crop the image to a centered square and resize.
    if img.size[0] > img.size[1]:
        img = img.crop(( \
         (img.size[0] - img.size[1]) / 2, 0, \
         (img.size[0] - img.size[1]) / 2 + img.size[1], img.size[1] \
        ))
    else:
        img = img.crop(( \
         0, (img.size[1] - img.size[0]) / 2, \
         img.size[0], (img.size[1] - img.size[0]) / 2 + img.size[0] \
        ))
    img.thumbnail((100,100))
    # Save the thumbnail as a PNG with a different name.
    img_name = "%s/%sthumb.png" % (os.getcwd(), topic_id)
    img.save(img_name, "PNG")

    # Upload the image and save the URL.
    os.system("./imguru %s > imgurOut" % img_name)
    with open("imgurOut", 'r') as imgur_file:
        return imgur_file.readline().strip()

# Checks to see if a topic has a tag.
# tags - a list of tags, each of which is a string
# key_tag - the tag to search for, a lowercase string
# returns True or False
def has_tag(tags, key_tag):
    return key_tag in (string.lower(raw_tag.strip()) for raw_tag in tags)

# Checks to see if a topic is pinned.
# topic - the Beautiful Soup tag object containing the topic
# returns True or False
def is_pinned(topic):
    return "Pinned" in [badge.string for badge in \
            topic.find_all(class_="ipsBadge ipsBadge_green")]

# Attempts to remove tags from titles.
# title - the string to remove tags from
# returns a string
def format_title(title):
    ret_str = []
    tags_done = False

    # Remove every token at the beginning of the string that includes brackets,
    # parens, or a non-number followed by a colon. (Ignore numbers followed by
    # colons because some people like to put a scale in their titles, e.g., 
    # "1:40 Mini X-wing".) 
    for token in title.split():
        if not tags_done and re.search("[\[\]\(\)]|[\D]:", token) == None:
            tags_done = True
        if tags_done:
            ret_str.append(token)

    return ' '.join(ret_str)

if __name__ == "__main__":
    main()
