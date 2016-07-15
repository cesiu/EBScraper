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

        for key, entry in entries.iteritems():
            if entry.img_url:
                sections[entry.category] += "[url=\"%s%s\"][img]%s[/img][/url] [url=\"%s%s\"][i]%s[/i][/url], by %s\n\n" % (base_url, entry.topic_id, entry.img_url, base_url, entry.topic_id, entry.title, entry.author)

        if sections["OR"]:
            body += "[size=5]Old Republic:[/size][hr]\n" + sections["OR"]
        if sections["PT"]:
            body += "[size=5]Prequel Trilogy:[/size][hr]\n" + sections["PT"]
        if sections["CW"]:
            body += "[size=5]Clone Wars:[/size][hr]\n" + sections["CW"]
        if sections["OT"]:
            body += "[size=5]Original Trilogy:[/size][hr]\n" + sections["OT"]
        if sections["EU"]:
            body += "[size=5]Expanded Universe:[/size][hr]\n" + sections["EU"]
        if sections["ST"]:
            body += "[size=5]Sequel Trilogy:[/size][hr]\n" + sections["ST"]
        if sections["NC"]:
            body += "[size=5]Fanon or Non-Canon:[/size][hr]\n" + sections["NC"]

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
                browser.find_element_by_xpath("//a[@href='http://www.eurobricks.com/forum/index.php?showtopic=136468']").click()
                browser.find_element_by_xpath("//a[@title='Reply to this topic']").click()

                time.sleep(2)
                tries = 10
                while tries > 0:
                    try:
                        browser.find_element_by_xpath("//a[@title='Toggle editing mode']").click()
                    except:
                        tries -= 1
                        continue
                    tries = 0
                time.sleep(2)
                tries = 10
                while tries > 0:
                    try:
                        browser.find_element_by_xpath("//textarea[@class='cke_source cke_enable_context_menu']").send_keys(body)
                    except:
                        tries -= 1
                        continue
                    tries = 0

                browser.find_element_by_name("dosubmit").click()

                browser.find_element_by_link_text("Sign Out").click()
                browser.close()

if __name__ == "__main__":
    main()
