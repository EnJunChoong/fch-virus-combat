import time
import scrapy
import random
import pymongo
import pandas as pd
from retry import retry
import requests
from bs4 import BeautifulSoup
from pymongo import TEXT
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


url = "free-proxy.cz/en/proxylist/country/MY/all/speed/all"
# url = "https://google.com"
page = requests.get(url)
bs = BeautifulSoup(page.text, "html.parser")
# table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
# rows = table.findAll(lambda tag: tag.name=='tr')
# bs.find("table", {"id":"proxy_list"})
# x = bs.find("table")
# print(x)
print(bs)