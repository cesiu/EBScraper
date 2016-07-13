# An experiment in using Beautiful Soup to scrape selected threads from a forum.
# author: Christopher (cesiu)
# version: 13 July 2016

from bs4 import BeautifulSoup
import urllib2
import string
import pickle
import os

def main():
    # Maps the subforum names to their id numbers.
    SUBFORUM_IDS = {
        "StarWars": "86",
    }
    # The base forum URL.
    base_url = "http://www.eurobricks.com/forum/index.php?showforum="

    # Load the list of already-indexed topic ids.
    old_urls = {}
    if "indexed.p" in os.listdir(os.getcwd()):
        old_urls = pickle.load(open("indexed.p", "rb"))

    # For every page:
    for start in range(0, 30, 30): 
        # Construct the URL and scrape the page.
        urls = scrape_forum_page("%s%s&st=%s" 
         % (base_url, SUBFORUM_IDS["StarWars"], str(start)))
        
        # Find the topics that haven't been indexed.
        for url in urls:
            if url in old_urls:
                print "%s is already indexed." % url
            else:
                print "%s needs to be indexed." % url
                old_urls[url] = True

    # Save the newly indexed topics.
    pickle.dump(old_urls, open("indexed.p", "wb"))

# Scrapes a page of a forum to find all the MOC topics.
# url - the url of the forum page
# returns a list of topic ids
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
        # If the tag is used as badge, it isn't wrapped in any tags.
        tags = [tag.contents[0].string if tag.find("span") else tag.string \
                for tag in topic.find_all(attrs = {"data-tooltip": True})]

        # If the topic is a non-pinned, non-WIP MOC:
        if (("moc" in string.lower(title) or has_tag(tags, "moc")) \
            and not ("wip" in string.lower(title) or has_tag(tags, "wip")) \
            and not is_pinned(topic)):
            #print title
            #print tags
            ret_urls.append(link.split('=')[-1])

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

if __name__ == "__main__":
    main()
