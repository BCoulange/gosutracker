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
  "id": re.compile(r"(\d+)_(\d+)").search(f).group(2),
  "average_rank": int(re.compile(r"(\d+)_(\d+)").search(f).group(1)),
  "path": f
} for f in listdir("scrapping/gamestatistics/") if isfile(join("scrapping/gamestatistics/", f)) and f!=".DS_Store"]
print(games[0])


# sort by reverse elo
games.sort(key=lambda x: x["average_rank"], reverse=True)
output = []


for g in games:
  # Opening JSON file
  f = open("scrapping/gamestatistics/"+g["path"])
  # returns JSON object as 
  # a dictionary
  d = json.load(f)


  if "is_first_player" in d["players"][0]:
    # it's already done
    print("already got first player!")
  else:
    path = join("scrapping/gamereviews/", str(d["id"])+".html")
    if not exists(path):
      # output.append(d)
      continue
    print(d["id"]+" geting first player.")

    with open(path) as fp: 

      soup = BeautifulSoup(fp, "html.parser")
      logs = soup.select('.pagesection__content')[0]
      m = re.compile(r"(.*)\stakes\s+the\s+([^\s]+) clan.*")
      results = logs.find_all(string=m)
      picks = []
      for el in results:
        res = m.search(el)
        picks.append({
          'pseudo': res.group(1),
          'clan': res.group(2)
        })

      if len(picks) == 0:
        print("pb in review")
        continue
      else:
        # matching the info
        first_player_pseudo = picks[0]["pseudo"]
        
        d["players"][0]["is_first_player"] = first_player_pseudo.strip() ==  d["players"][0]["pseudo"].strip()
        d["players"][1]["is_first_player"] = first_player_pseudo.strip() ==  d["players"][1]["pseudo"].strip()
        d["clans_selected"] = [el['clan'] for el in picks]

        if len(d["clans_selected"]) < 6:
          raise "Not the good number of clans"


  # # date
  # date_path = join("scrapping/enddates/", str(d["id"])+".json")
  # if exists(date_path):
  #   with open(date_path) as dp:
  #     dpp = json.load(dp)
  #     d["finished_at"] = dpp["date"]
  # else:
  #   print("no date")
  
  output.append(d)


print(str(len(output))+" stats with fp")

# cleaning pseudo out of data


with open('data.json', 'w+') as f:
  json.dump(output, f)
