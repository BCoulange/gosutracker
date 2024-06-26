from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import random
from os.path import exists
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup
import re

games = [{
  "path": f,
  "id": re.compile(r"(\d+)\.html").search(f).group(1),
} for f in listdir("scrapping/games/") if isfile(join("scrapping/games/", f))]



browser = webdriver.Chrome()
browser.get("https://en.boardgamearena.com/account")
username = browser.find_element(By.CSS_SELECTOR, "#username_input")
password = browser.find_element(By.CSS_SELECTOR, "#password_input")
login = browser.find_element(By.CSS_SELECTOR, "#submit_login_button")

# Opening JSON file
f = open('scrapping/creds.json')
 

# returns JSON object as 
# a dictionary
creds = json.load(f)


username.send_keys(creds["login"])
password.send_keys(creds["password"])
login.click()

WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-label='dismiss cookie message']")))

cookie_button = browser.find_element(By.CSS_SELECTOR, "[aria-label='dismiss cookie message']")
cookie_button.click()

time.sleep(5+random.random()*5)
# we are good to go
 
i = 0

for d in games:
  info_path = "scrapping/games/"+str(d["id"])+".html"
  print(i)

  print("getting "+str(d["id"])+"...")
  browser.get("https://boardgamearena.com/table?table="+str(d["id"]))
  
  WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".col-md-8.col-push-4")))
  time.sleep(1)

  allpage = browser.find_element(By.CSS_SELECTOR, "#main-content")
  html = allpage.get_attribute('innerHTML')
  f = open(info_path, "w+")
  f.write(html)
  f.close()

  time.sleep(1+random.random()*2)

  i = i+1

