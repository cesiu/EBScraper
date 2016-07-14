# Renders a pickled index.
# author: Christopher (cesiu)
# version: 0.1

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib2
import string
import pickle
import os
import time
from eb_scraper import IndexEntry

def main():
    if "indexed.p" in os.listdir(os.getcwd()):
        entries = pickle.load(open("indexed.p", "rb"))
        base_url = "http://www.eurobricks.com/forum/index.php?showtopic="
        body = "[url=\"https://github.com/cesiu/EBScraper\"]https://github.com/cesiu/EBScraper[/url]\n\n"

        for key, entry in entries.iteritems():
            body += "[url=\"%s%s\"][img]%s[/img][/url] [url=\"%s%s\"][i]%s[/i][/url], by %s\n\n" % (base_url, entry.topic_id, entry.img_url, base_url, entry.topic_id, entry.title, entry.author)

        print body

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
            browser.find_element_by_xpath("//a[@title='Toggle editing mode']").click()
            time.sleep(1)
            browser.find_element_by_xpath("//textarea[@class='cke_source cke_enable_context_menu']").send_keys(body)
            browser.find_element_by_name("dosubmit").click()

            browser.find_element_by_link_text("Sign Out").click()
            browser.close()

if __name__ == "__main__":
    main()
