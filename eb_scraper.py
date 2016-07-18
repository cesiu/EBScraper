# An experiment using Beautiful Soup to scrape selected threads from a forum.
# author: Christopher (cesiu)
# version: 0.2

from bs4 import BeautifulSoup
from PIL import Image
from sys import argv, exit
from classifier import *
from time import time
import urllib
import urllib2
import string
import pickle
import os
import re

# The base forum URL.
BASE_URL = "http://www.eurobricks.com/forum/index.php"
# The number of topics per page.
NUM_TOPICS = 30

# Represents one entry in an index.
class IndexEntry:
    def __init__(self, topic_id, title, author):
        self.topic_id = topic_id
        self.title = title
        self.author = author
        self.img_url = ""
        self.category = "unknown"

def main():
    # Maps the subforum names to their id numbers.
    SUBFORUM_IDS = {
        "StarWars": "86",
        "WattosJunkyard": "114",
        "NarEurbrikka": "175",
    }

    # Get the range from the args.
    if len(argv) < 3:
        err_exit()
    try:
        page_min = int(argv[1]) - 1
        page_max = int(argv[2]) 
    except:
        err_exit()

    # Check for options.
    opts = ""
    if len(argv) > 3:
        for arg in argv[3:]:
            opts += arg

    # Load the dictionary of already-indexed topics.
    old_entries = {}
    if "indexed.p" in os.listdir(os.getcwd()):
        old_entries = pickle.load(open("indexed.p", "rb"))
    # Create the dictionary of newly-indexed topics.
    new_entries = {}

    with Classifier("c" in opts) as classifier:
        # For every page:
        for start in range(page_min * NUM_TOPICS, \
                           page_max * NUM_TOPICS, NUM_TOPICS): 
            # Construct the URL and scrape the page.
            entries = scrape_forum_page("%s?showforum=%s&st=%s" \
             % (BASE_URL, SUBFORUM_IDS["StarWars"], str(start)), "m" in opts)
        
            # Find the MOCs that haven't been indexed and scrape them.
            for entry in entries:
                if entry.topic_id in old_entries:
                    print "%s (%s) by %s already indexed." \
                           % (entry.title, entry.topic_id, entry.author)
                else:
                    print "%s (%s) by %s needs indexing." \
                           % (entry.title, entry.topic_id, entry.author)
                    (entry.img_url, entry.category) \
                     = scrape_topic(entry.topic_id, classifier, "i" in opts)
                    old_entries[entry.topic_id] = True
                    new_entries[entry.topic_id] = entry

    # Save the updated dictionaries.
    pickle.dump(old_entries, open("indexed.p", "wb"))
    pickle.dump(new_entries, open("to_render.p", "wb"))

    # Tar and remove the images.
    if "i" in opts:
        os.system("tar -cf %s.tar *.png *.jpg" % int(time()))
        os.system("rm *.png *.jpg")

# Scrapes a page of a forum to find all the MOC topics.
# url - the url of the forum page
# include_mods - whether or not to include mods
# returns a list of IndexEntries
def scrape_forum_page(url, include_mods = False):
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

        # Grab all the non-pinned, non-WIP, MOC (or mod) topics:
        if (re.search("(^|[^a-z])moc([^a-z]|$)", string.lower(title)) \
           or has_tag(tags, "moc") or (include_mods \
           and (re.search("(^|[^a-z])mod([^a-z]|$)", string.lower(title)) \
           or has_tag(tags, "mod")))) and not ("wip" in string.lower(title) \
           or has_tag(tags, "wip")) and not is_pinned(topic):
            ret_urls.append(IndexEntry(link.split('=')[-1].encode('utf-8'), \
             format_title(title).encode('utf-8'), author.encode('utf-8')))

    return ret_urls

# Scrapes a topic and saves the first image.
# topic_id - the id of the topic
# classifier - the optional classifier to use on the topic
# gen_thumbs - whether or not to generate thumbnails
# returns a tuple, the URL of the thumbnail generated for the topic and
#         the category of the topic
def scrape_topic(topic_id, classifier = None, gen_thumbs = False):
    # Load the page and initialize the parser.
    page = urllib2.urlopen("%s?showtopic=%s" % (BASE_URL, topic_id))
    soup = BeautifulSoup(page.read())
    print "   Scraping %s..." % soup.title.string

    if classifier:
        # Classify the topic, giving the title twenty times more weight than 
        # the first post's content.
        category = classifier.check(((format_title(soup.find( \
                   class_="ipsType_pagetitle").string) + " ") * 20 + \
                   soup.find(itemprop="commentText") \
                   .getText()).encode('utf-8'))

    # Check to see if the topic shouldn't be indexed (a find, for example).
    if gen_thumbs and category != "NA":
        # Find the first non-emoticon, non-attached, non-'Indexed!' image 
        # in the first post.
        img_url = None
        images = soup.find(itemprop="commentText").find_all("img", class_=True)
        for image in images:
            if "bbc_img" in image["class"] and image["src"] \
             != "http://www.eurobricks.com/forum/uploads/1242820715/"\
             + "gallery_2351_18_164.gif" and image["src"] \
             != "http://www.brickshelf.com/gallery/KimT/Mixed/EB/indexed.gif" \
             and image["src"] != "http://www.brickshelf" \
             + ".com/gallery/legowiz23/ebthumbnails/indexed.gif":
                img_url = image["src"]
                break;
        if img_url == None:
            print "   Could not find an image."
            return ("", category)

        # Define a name for the image, keeping the extension.
        img_name = ("%s/%s.%s" % (os.getcwd(), topic_id, \
                                  img_url.split(".")[-1])).encode('utf-8')

        # Download and open the image.
        try:
            (filename, header) = urllib.urlretrieve(img_url, img_name)
            img = Image.open(img_name)
            print "   Downloaded %s." % filename
        except:
            print "   Could not download or open image."
            return ("", category)

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
        img_name = ("%s/%sthumb.png" % (os.getcwd(), topic_id)).encode('utf-8')
        img.save(img_name, "PNG")

        # Upload the image and save the URL.
        while True:
            os.system("./imguru %s > imgurOut" % img_name)
            with open("imgurOut", 'r') as imgur_file:
                img_url = imgur_file.readline().strip()
                if "http://i.imgur.com/" in img_url:
                    return (img_url, category)
    return ("", category)

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

# Prints the help message and exits.
def err_exit():
    print "Usage : pypy eb_scraper.py [page min] [page max] <options>\n" \
          + "Options:\n" \
          + "   -i  -  Generate thumbnails.\n" \
          + "   -c  -  Automatically classify MOCs.\n" \
          + "   -m  -  Include mods."
    exit()

if __name__ == "__main__":
    main()
