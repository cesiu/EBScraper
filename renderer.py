# Renders a pickled index.
# author: Christopher (cesiu)
# version: 0.2

from eb_scraper import IndexEntry
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

def main():
    if "to_render.p" in os.listdir(os.getcwd()):
        entries = pickle.load(open("to_render.p", "rb"))
        base_url = "http://www.eurobricks.com/forum/index.php?showtopic="
        post_ids = {"OT":"2612377", "PT":"2612386", "ST":"2613058", "EU":"2613068", "CW":"2613077", "OR":"2613085", "NC":"2613095"}
        sections = dict([(key, "") for key in CLASSES])
        successes = []
        failures = []

        for key in CLASSES:
            if not key in post_ids:
                print "Post id not found for %s." % key
                exit()

        for key, entry in entries.iteritems():
            if entry.img_url or "-d" in argv and entry.category != "NA":
                sections[entry.category] += "\n\n[url=\"%s%s\"][img]%s[/img][/url] [url=\"%s%s\"][i]%s[/i][/url], by %s" % (base_url, entry.topic_id, entry.img_url, base_url, entry.topic_id, entry.title, entry.author)

        for key in CLASSES:
            print "\n\n" + key + ":\n-----" + sections[key]

        if "-u" in argv:
            with open("info", 'r') as info_file:
                username = info_file.readline().strip()
                password = info_file.readline().strip()

                browser = webdriver.Firefox()
                browser.get("http://www.eurobricks.com/forum/index.php?app=core&module=global&section=login")
                browser.find_element_by_name("ips_username").send_keys(username)
                browser.find_element_by_name("ips_password").send_keys(password + Keys.RETURN)
                browser.find_element_by_xpath("//a[@href='http://www.eurobricks.com/forum/index.php?act=idx']").click()
                browser.find_element_by_xpath("//a[@href='http://www.eurobricks.com/forum/index.php?showforum=125']").click()
                browser.find_element_by_xpath("//a[@href='http://www.eurobricks.com/forum/index.php?showtopic=137557']").click()


                if sections["OT"]:
                    try:
                        edit_post(browser, "2612377", sections["OT"])
                        successes.append("OT")
                    except:
                        failures.append("OT")
                if sections["PT"]:
                    try:
                        edit_post(browser, "2612386", sections["PT"])
                        successes.append("PT")
                    except:
                        failures.append("PT")
                if sections["ST"]:
                    try:
                        edit_post(browser, "2613058", sections["ST"])
                        successes.append("ST")
                    except:
                        failures.append("ST")
                if sections["EU"]:
                    try:
                        edit_post(browser, "2613068", sections["EU"])
                        successes.append("EU")
                    except:
                        failures.append("EU")
                if sections["CW"]:
                    try:
                        edit_post(browser, "2613077", sections["CW"])
                        successes.append("CW")
                    except:
                        failures.append("CW")
                if sections["OR"]:
                    try:
                        edit_post(browser, "2613085", sections["OR"])
                        successes.append("OR")
                    except:
                        failures.append("OR")
                if sections["NC"]:
                    try:
                        edit_post(browser, "2613095", sections["NC"])
                        successes.append("Fanon")
                    except:
                        failures.append("Fanon")

                log_msg = ""
                if len(successes) > 0:
                    log_msg += ", ".join(successes) + " indices successfully updated; "
                else:
                    log_msg += "No successes; "
                if len(failures) > 0:
                    log_msg += ", ".join(failures) + " indices failed to update."
                else:
                    log_msg += "no failures."

                edit_post(browser, "2613104", time.strftime("\n[b]%d %B %Y[/b] at %H:%M:%S, %Z: ") + log_msg)

                browser.find_element_by_link_text("Sign Out").click()
                browser.close()

def edit_post(browser, post_id, text):
    browser.find_element_by_id("edit_post_%s" % post_id).click()
    time.sleep(2)

    if edit_post.need_toggle:
        tries = 10
        while tries > 0:
            try:
                browser.find_element_by_xpath("//a[@title='Toggle editing mode']").click()
            except:
                tries -= 1
                continue
            tries = 0
        time.sleep(2)
        edit_post.need_toggle = False

    tries = 10
    while tries > 0:
        try:
            browser.find_element_by_xpath("//textarea[@class='cke_source cke_enable_context_menu']").send_keys(text)
        except:
            tries -= 1
            continue
        tries = 0
    temp = browser.find_element_by_id("post_edit_reason_%s" % post_id)
    temp.clear()
    temp.send_keys(time.strftime("Updated %d %B %Y at %H:%M:%S, %Z."))
    #browser.find_element_by_id("add_edit_2612377").click()
    browser.find_element_by_id("edit_save_e%s" % post_id).click()

edit_post.need_toggle = True

if __name__ == "__main__":
    main()
