# An experiment in using BeautifulSoup to scrape selected threads from forums.
# author: Christopher (cesiu)
# version: 13 July 2016

from bs4 import BeautifulSoup
import urllib2
import string

def main():
    # Maps the subforum names to their id numbers.
    SUBFORUM_IDS = {
        "StarWars": "86",
    }
    # The base forum URL.
    base_url = "http://www.eurobricks.com/forum/index.php?showforum="

    # For every page:
    for start in range(0, 30, 30): 
        # Construct the URL and open the page.
        page = urllib2.urlopen("%s%s&st=%s" \
               % (base_url, SUBFORUM_IDS["StarWars"], str(start)))
        # Initialize a Beautiful Soup parser.
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
            if (("moc" in string.lower(title) or hasTag(tags, "moc")) \
                and not ("wip" in string.lower(title) or hasTag(tags, "wip")) \
                and not isPinned(topic)):
                print"\n-----\n"
                print title
                print link
                print tags

# Checks to see if a topic has a tag.
# tags - a list of tags, each of which is a string
# key_tag - the tag to search for, a lowercase string
# returns True or False
def hasTag(tags, key_tag):
    return key_tag in (string.lower(raw_tag.strip()) for raw_tag in tags)

# Checks to see if a topic is pinned.
# topic - the Beautiful Soup tag object containing the topic
# returns True or False
def isPinned(topic):
    return "Pinned" in [badge.string for badge in \
            topic.find_all(class_="ipsBadge ipsBadge_green")]

if __name__ == "__main__":
    main()
