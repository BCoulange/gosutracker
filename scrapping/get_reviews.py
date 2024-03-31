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
import re

# Opening JSON file
f = open('scrapping/creds.json')
 
# returns JSON object as 
# a dictionary
creds = json.load(f)


browser = webdriver.Chrome()
browser.get("https://en.boardgamearena.com/account")
username = browser.find_element(By.CSS_SELECTOR, "#username_input")
password = browser.find_element(By.CSS_SELECTOR, "#password_input")
login = browser.find_element(By.CSS_SELECTOR, "#submit_login_button")

username.send_keys(creds["login"])
password.send_keys(creds["password"])
login.click()

WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-label='dismiss cookie message']")))

cookie_button = browser.find_element(By.CSS_SELECTOR, "[aria-label='dismiss cookie message']")
cookie_button.click()

time.sleep(5+random.random()*5)
# we are good to go
 
games = [{
  "id": re.compile(r"(\d+)_(\d+)").search(f).group(2),
  "average_rank": int(re.compile(r"(\d+)_(\d+)").search(f).group(1)),
  "path": f
} for f in listdir("scrapping/gamestatistics/") if isfile(join("scrapping/gamestatistics/", f))]
print(games[0])


# sort by reverse elo
games.sort(key=lambda x: x["average_rank"], reverse=True)

 
i = 0


for g in games:
  # Opening JSON file
  f = open("scrapping/gamestatistics/"+g["path"])
  # returns JSON object as 
  # a dictionary
  d = json.load(f)
  info_path = "scrapping/gamereviews/"+str(d["id"])+".html"
  print(str(i)+" ELO "+str(d["average_rank"]))
  if ("is_first_player" not in d["players"][0]) and (not exists(info_path)):
    print("getting "+str(d["id"])+"...")
    browser.get("https://boardgamearena.com/gamereview?table="+str(d["id"]))
    
    WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".gamelogreview")))

    allpage = browser.find_element(By.CSS_SELECTOR, "#main-content")
    html = allpage.get_attribute('innerHTML')
    f = open(info_path, "w+")
    f.write(html)
    f.close()

    time.sleep(10+random.random()*5)

  i = i+1

