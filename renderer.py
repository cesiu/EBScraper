# Renders a pickled index.
# author: Christopher (cesiu)
# version: 0.1

from bs4 import BeautifulSoup
from eb_scraper import IndexEntry
from sys import argv
import urllib2
import string
import pickle
import os
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
except:
    if "-u" in argv:
        argv.remove("-u")
        print "Selenium not installed. Not posting results."

def main():
    if "to_render.p" in os.listdir(os.getcwd()):
        entries = pickle.load(open("to_render.p", "rb"))
        base_url = "http://www.eurobricks.com/forum/index.php?showtopic="
        body = "[url=\"https://github.com/cesiu/EBScraper\"]https://github.com/cesiu/EBScraper[/url]\n\n"

        sections = {"OT": "", "PT": "", "CW": "", "EU": "", "ST": "", \
                    "OR": "", "NC": ""}
        successes = []
        failures = []

        for key, entry in entries.iteritems():
            if entry.img_url:
                sections[entry.category] += "\n\n[url=\"%s%s\"][img]%s[/img][/url] [url=\"%s%s\"][i]%s[/i][/url], by %s" % (base_url, entry.topic_id, entry.img_url, base_url, entry.topic_id, entry.title, entry.author)

        if sections["OR"]:
            body += "[color=\"#8B0000\"][size=5][b]Old Republic:[/b][/size][/color][hr]\n" + sections["OR"]
        if sections["PT"]:
            body += "[color=\"#8B0000\"][size=5][b]Prequel Trilogy:[/b][/size][/color][hr]\n" + sections["PT"]
        if sections["CW"]:
            body += "[color=\"#8B0000\"][size=5][b]Clone Wars:[/b][/size][/color][hr]\n" + sections["CW"]
        if sections["OT"]:
            body += "[color=\"#8B0000\"][size=5][b]Original Trilogy:[/b][/size][/color][hr]\n" + sections["OT"]
        if sections["EU"]:
            body += "[color=\"#8B0000\"][size=5][b]Expanded Universe:[/b][/size][/color][hr]\n" + sections["EU"]
        if sections["ST"]:
            body += "[color=\"#8B0000\"][size=5][b]Sequel Trilogy:[/b][/size][/color][hr]\n" + sections["ST"]
        if sections["NC"]:
            body += "[color=\"#8B0000\"][size=5][b]Fanon or Non-Canon:[/b][/size][/color][hr]\n" + sections["NC"]

        print body

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
                        edit_post(browser, "2612379", sections["PT"])
                        successes.append("PT")
                    except:
                        failures.append("PT")
                if sections["ST"]:
                    try:
                        edit_post(browser, "2612382", sections["ST"])
                        successes.append("ST")
                    except:
                        failures.append("ST")
                if sections["EU"]:
                    try:
                        edit_post(browser, "2612384", sections["EU"])
                        successes.append("EU")
                    except:
                        failures.append("EU")
                if sections["CW"]:
                    try:
                        edit_post(browser, "2612386", sections["CW"])
                        successes.append("CW")
                    except:
                        failures.append("CW")
                if sections["OR"]:
                    try:
                        edit_post(browser, "2612388", sections["OR"])
                        successes.append("OR")
                    except:
                        failures.append("OR")
                if sections["NC"]:
                    try:
                        edit_post(browser, "2612390", sections["NC"])
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

                edit_post(browser, "2612405", time.strftime("\n[b]%d %B %Y[/b] at %H:%M:%S, %Z: ") + log_msg)

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
