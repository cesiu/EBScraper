# Renders a pickled index.
# author: Christopher (cesiu)
# version: 0.2

from eb_scraper import IndexEntry, BASE_URL
from classifier import CLASSES
from sys import argv, exit
import urllib2
import string
import pickle
import os
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
except:
    print "Selenium not installed."

# Maps the entry categories to the posts that they're currently being added to.
POST_IDS = {"OTveh":"2617870", "OTloc":"2617873", "OTchr":"2617876", \
            "OTmin":"2617878", "PTveh":"2617880", "PTloc":"2617882", \
            "PTchr":"2617885", "PTmin":"2617887", "STveh":"2617889", \
            "STloc":"2617891", "STchr":"2617893", "STmin":"2617895", \
            "EUveh":"2617897", "EUloc":"2617899", "EUchr":"2617901", \
            "EUmin":"2617904", "CWveh":"2617906", "CWloc":"2617908", \
            "CWchr":"2617910", "CWmin":"2617912", "NCveh":"2617914", \
            "NCloc":"2617917", "NCchr":"2617917", "NCmin":"2617914", \
            "SPall":"2617924"}

def main():
    # Check for options.
    opts = ""
    if len(argv) > 1:
        for arg in argv[1:]:
            opts += arg

    if "to_render.p" in os.listdir(os.getcwd()):
        # Initialize empty strings for the new contents of each post.
        sections = dict([(key, "") for key in CLASSES])
        successes = []
        failures = []
        # Load the entries that need to be rendered.
        entries = pickle.load(open("to_render.p", "rb"))

        # Check that we have all the necessary post ids.
        for key in CLASSES:
            if not key in POST_IDS:
                print "Post id not found for %s." % key
                exit()

        # Render the BBCode for all the entries that have images and should be
        # indexed.
        for key, entry in entries.iteritems():
            if (entry.img_url or "d" in opts) and entry.category in CLASSES:
                sections[entry.category] += ("\n\n[url=\"%s?showtopic=%s\"]" \
                 + "[img]%s[/img][/url] [url=\"%s?showtopic=%s\"][i]%s[/i]" \
                 + "[/url], by %s") % (BASE_URL, entry.topic_id, \
                 entry.img_url, BASE_URL, entry.topic_id, entry.title, \
                 entry.author)

        # Dump the render results to stdout.
        for key in CLASSES:
            print "\n\n" + key + ":\n-----" + sections[key]

        # If the results should be uploaded:
        if "u" in opts:
            with open("info", 'r') as info_file:
                # Read the EB username and password from the info file.
                username = info_file.readline().strip()
                password = info_file.readline().strip()

                # Open a Firefox instance and load the login page.
                browser = webdriver.Firefox()
                browser.get("http://www.eurobricks.com/forum/index.php?app=" \
                            + "core&module=global&section=login")

                # Log in.
                browser.find_element_by_name("ips_username") \
                       .send_keys(username)
                browser.find_element_by_name("ips_password") \
                       .send_keys(password + Keys.RETURN)

                # Go to the main forum.
                browser.find_element_by_xpath("//a[@href='http://" \
                 + "www.eurobricks.com/forum/index.php?act=idx']").click()

                # Go to the Freezer.
                browser.find_element_by_xpath("//a[@href='http://" \
                 + "www.eurobricks.com/forum/index.php?showforum=125']") \
                 .click()

                # Go to the index topic.
                browser.find_element_by_xpath("//a[@href='http://" \
                 + "www.eurobricks.com/forum/index.php?showtopic=137853']") \
                 .click()

                # For every category that has new entries:
                for category in CLASSES:
                    if sections[category]:
                        # Edit the appropriate post and add the entries.
                        try:
                            edit_post(browser, POST_IDS[category], \
                                      sections[category])
                            successes.append(category)
                        except:
                            failures.append(category)

                # Generate a log message.
                log_msg = ""
                if len(successes) > 0:
                    log_msg += ", ".join(successes) \
                            + " indices successfully updated; "
                else:
                    log_msg += "No successes; "
                if len(failures) > 0:
                    log_msg += ", ".join(failures) \
                            + " indices failed to update."
                else:
                    log_msg += "no failures."

                # Add the message to the log.
                edit_post(browser, "2617925", time.strftime("\n[b]%d %B %Y" \
                          + "[/b] at %H:%M:%S, %Z: ") + log_msg)

                # Log out and close the browser.
                browser.find_element_by_link_text("Sign Out").click()
                browser.close()
        
            # Tar and remove the images and pickle file.
            stamp = int(time.time())
            os.system("tar -cf %s.tar to_render.p *.png *.jpg *.gif" % stamp)
            os.system("gzip %s.tar" % stamp)
            os.system("rm to_render.p *.png *.jpg *.gif")

# Edits a post and adds text to it.
# browser - the browser instance with the post loaded.
# post_id - the id of the post to be edited.
# text - the text to add to the post.
def edit_post(browser, post_id, text):
    # Click on the "Edit" button and wait a couple seconds for IPB to load the
    # editor. 
    browser.find_element_by_id("edit_post_%s" % post_id).click()
    time.sleep(2)

    # If this is the first time editing, switch to the plain text editor.
    if edit_post.need_toggle:
        tries = 10
        while tries > 0:
            try:
                browser.find_element_by_xpath("//a[@title=" \
                 + "'Toggle editing mode']").click()
            except:
                tries -= 1
                continue
            tries = 0
        time.sleep(2)
        edit_post.need_toggle = False

    # Find the editor and send it the text.
    tries = 10
    while tries > 0:
        try:
            browser.find_element_by_xpath("//textarea[@class='" \
             + "cke_source cke_enable_context_menu']").send_keys(text)
        except:
            tries -= 1
            continue
        tries = 0

    # Update the text in the "Reason for edit" field.
    temp = browser.find_element_by_id("post_edit_reason_%s" % post_id)
    temp.clear()
    temp.send_keys(time.strftime("Updated %d %B %Y at %H:%M:%S, %Z."))
    #browser.find_element_by_id("add_edit_2612377").click()

    # Save the post.
    browser.find_element_by_id("edit_save_e%s" % post_id).click()

edit_post.need_toggle = True

if __name__ == "__main__":
    main()
