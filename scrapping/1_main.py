from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random

browser = webdriver.Chrome()

browser.get("https://boardgamearena.com/gamepanel?game=gosux")

WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Number of games played')]")))
WebDriverWait(browser,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-label='dismiss cookie message']")))



cookie_button = browser.find_element(By.CSS_SELECTOR, "[aria-label='dismiss cookie message']")
cookie_button.click()

element = browser.find_element(By.XPATH, "//*[contains(text(), 'Number of games played')]/following-sibling::div/child::div")
# element = browser.find_element(By.XPATH, "//*[contains(text(), 'Number of games played')]/following-sibling::div")
print(element)

browser.execute_script("arguments[0].scrollIntoView();", element)

element.click()


time.sleep(2)
popup = browser.find_element(By.CSS_SELECTOR, ".bga-popup-modal__content")

for i in range(15):
  print(i)
  browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup)

  more = browser.find_element(By.XPATH, "//*[contains(text(), 'See more...')]")
  more.click()
  time.sleep(2+random.random()*2)

html = popup.get_attribute('innerHTML')
f = open("scrapping/gamelist.html", "w+")
f.write(html)
f.close()



