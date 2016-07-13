# An experiment in using Beautiful Soup to scrape selected threads from a forum.
# author: Christopher (cesiu)
# version: 0.1

from bs4 import BeautifulSoup
import urllib2
import string
import pickle
import os
import re

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
    }
    # The base forum URL.
    base_url = "http://www.eurobricks.com/forum/index.php?showforum="

    # Load the list of already-indexed topics.
    old_entries = {}
    if "indexed.p" in os.listdir(os.getcwd()):
        old_entries = pickle.load(open("indexed.p", "rb"))

    # For every page:
    for start in range(0, 30, 30): 
        # Construct the URL and scrape the page.
        entries = scrape_forum_page("%s%s&st=%s" 
         % (base_url, SUBFORUM_IDS["StarWars"], str(start)))
        
        # Find the topics that haven't been indexed.
        for entry in entries:
            if entry.topic_id in old_entries:
                print "%s (%s) by %s already indexed." \
                      % (entry.title, entry.topic_id, entry.author)
            else:
                print "%s (%s) by %s needs indexing." \
                      % (entry.title, entry.topic_id, entry.author)
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
    soup = BeautifulSoup(page.read(), "lxml")

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

        # If the topic is a non-pinned, non-WIP MOC:
        if (("moc" in string.lower(title) or has_tag(tags, "moc")) \
            and not ("wip" in string.lower(title) or has_tag(tags, "wip")) \
            and not is_pinned(topic)):
            #print title
            #print tags
            ret_urls.append(IndexEntry(str(link.split('=')[-1]), \
             str(format_title(title)), str(author), None))

    return ret_urls

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
    # colons because some people put a scale at the start of their titles, e.g., 
    # "1:40 Mini X-wing".) 
    for token in title.split():
        if not tags_done and re.search("[\[\]\(\)]|[\D]:", token) == None:
            tags_done = True
        if tags_done:
            ret_str.append(token)

    return ' '.join(ret_str)

if __name__ == "__main__":
    main()
