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
import glob

games = [f for f in listdir("scrapping/games/") if isfile(join("scrapping/games/", f))]

gosu_clans = ["Xi'an", 'Narashima', 'Abhilasha', 'Galmi', 'Tomorrow', 'Goan-Sul','Justice', 'Phoenix','Abunakkashii']

all_infos = []

for game in games:
  print("processing "+game+"...")


  with open(join("scrapping/games/", game)) as fp: 
    game_id = re.compile("(\d+)\.html").search(game).group(1)

    # check if already done
    if len(glob.glob("scrapping/gamestatistics/*_"+game_id+".json")) > 0:
      print("already done!")
      continue

    soup = BeautifulSoup(fp, "html.parser")
    # check if game cancelled
    if (len(soup.select(".game_cancelled")) > 0) and (soup.select(".game_cancelled")[0]["style"] != "display:none"):
      continue

    # game conceded
    conceded = False
    if (len(soup.select(".game_conceded")) > 0) and (soup.select(".game_conceded")[0]["style"] != "display:none"):
      conceded = True

    game_infos = {
      "name":game, 
      "players":[],
      "id":game_id
    }

    # statistics
    statistics = soup.select('#statistics_content')[0]
    # - average rank
    game_infos["average_rank"] = (int(statistics.select('.gamerank_value')[0].get_text()))
    

    
    # creation time
    game_infos["creation_time"] = soup.select('#creationtime')[0].get_text()
    m = re.compile('.*(\d\d)\/(\d\d)\/(\d\d\d\d).*')
    result = m.search(game_infos["creation_time"])
    if result is not None:
      game_infos["creation_time_month"] = int(result.group(1))
      game_infos["creation_time_day"] = int(result.group(2))
      game_infos["creation_time_year"] = int(result.group(3))
    else:
      print("no date :(")




    # expansion
    exp_infos = soup.select('#gameoption_100_displayed_value')
    if len(exp_infos) == 0:
      game_infos["Abunakkashii"] = False
    else:
      game_infos["Abunakkashii"] = (exp_infos[0].get_text() == "Yes")




    # - duration
    m = re.compile('\s*(\d+)\s*min')

    text = statistics.select('div.row-label:-soup-contains("Game duration")')[0].find_next_sibling("div").get_text()
    result = m.search(text)
    if result is not None:
      game_infos["duration_min"] = int(result.group(1))


    # - passives
    p1 = statistics.select('div.row-label:-soup-contains("Passive Clan 1")')[0].find_next_sibling("div").get_text().strip()
    p2 = statistics.select('div.row-label:-soup-contains("Passive Clan 2")')[0].find_next_sibling("div").get_text().strip()
    game_infos["clan_passives"] = [p1,p2]

    # - victory condition
    if conceded:
      game_infos["victory_condition"] = "Conceded"
    else:
      game_infos["victory_condition"] = statistics.select('div.row-label:-soup-contains("Victory Type")')[0].find_next_sibling("div").get_text().strip()
      
    # - number of rounds
    game_infos["nb_of_rounds"] = int(statistics.select('div.row-label:-soup-contains("Number of rounds")')[0].find_next_sibling("div").get_text().strip())
    
    # - selected clans
    has_first_player_infos = ((len(statistics.select('th:-soup-contains("First player")')) > 0 ) and (statistics.select('th:-soup-contains("First player")')[0].find_next_sibling("td").get_text().strip() != "-"))
    if has_first_player_infos:
      p1_first_player = statistics.select('th:-soup-contains("First player")')[0].find_next_sibling("td").get_text().strip() == "yes"
      p2_first_player = statistics.select('th:-soup-contains("First player")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip() == "yes"
      print(p1_first_player)

    p1_c1 = statistics.select('th:-soup-contains("Clan 1")')[0].find_next_sibling("td").get_text().strip()
    p1_c2 = statistics.select('th:-soup-contains("Clan 2")')[0].find_next_sibling("td").get_text().strip()
    p1_c3 = statistics.select('th:-soup-contains("Clan 3")')[0].find_next_sibling("td").get_text().strip()
    p2_c1 = statistics.select('th:-soup-contains("Clan 1")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()
    p2_c2 = statistics.select('th:-soup-contains("Clan 2")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()
    p2_c3 = statistics.select('th:-soup-contains("Clan 3")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()

    if has_first_player_infos: 
      if p1_first_player:
        game_infos["clans_selected"] = [p1_c1, p2_c1, p2_c2, p1_c2, p1_c3, p2_c3]
      else:
        game_infos["clans_selected"] = [p2_c1, p1_c1, p1_c2, p2_c2, p2_c3, p1_c3]
    else:
      game_infos["clans_selected"] = [p1_c1, p2_c1, p2_c2, p1_c2, p1_c3, p2_c3]

    # - winner
    w = statistics.select('th:-soup-contains("Game result")')[0].find_next_sibling("td").get_text().strip()
    p1_won = (re.compile('1st').match(w) is not None)
    w = statistics.select('th:-soup-contains("Game result")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()
    p2_won = (re.compile('1st').match(w) is not None)

    # - banned clan
    if game_infos["Abunakkashii"]:
      game_infos["clans_banned"] = [c for c in gosu_clans if c not in game_infos["clans_selected"] and c not in game_infos["clan_passives"] ]
    else:
      game_infos["clans_banned"] = ["Abunakkashii"]


    game_infos["players"] = [
      {
        "pseudo":soup.select('#player_stats_header')[0].find('th').find_next_sibling('th').get_text(),
        "clans":[p1_c1,p1_c2,p1_c3],
        "is_winner":p1_won,
        "lvl1_played": int(statistics.select('th:-soup-contains("Level I played")')[0].find_next_sibling("td").get_text().strip()),
        "lvl2_played": int(statistics.select('th:-soup-contains("Level II played")')[0].find_next_sibling("td").get_text().strip()),
        "lvl3_played": int(statistics.select('th:-soup-contains("Level III played")')[0].find_next_sibling("td").get_text().strip()),
        "cards_drawn": int(statistics.select('th:-soup-contains("Cards drawn")')[0].find_next_sibling("td").get_text().strip()),
        "cards_captured": int(statistics.select('th:-soup-contains("Cards captured")')[0].find_next_sibling("td").get_text().strip()),
        "cards_destroyed": int(statistics.select('th:-soup-contains("Cards destroyed")')[0].find_next_sibling("td").get_text().strip()),
        "cards_sacrificed": int(statistics.select('th:-soup-contains("Cards sacrificed")')[0].find_next_sibling("td").get_text().strip()),
        "cards_shifted": int(statistics.select('th:-soup-contains("Cards shifted")')[0].find_next_sibling("td").get_text().strip()),
        "force_of_will": int(statistics.select('th:-soup-contains("Force of will")')[0].find_next_sibling("td").get_text().strip()),
        "activation_tokens": int(statistics.select('th:-soup-contains("Activation tokens")')[0].find_next_sibling("td").get_text().strip()),
        "clan_most_played": statistics.select('th:-soup-contains("Clan most played")')[0].find_next_sibling("td").get_text().strip(),
        "clan_most_played_last_5_turns": statistics.select('th:-soup-contains("Clan most played (last 5 turns)")')[0].find_next_sibling("td").get_text().strip()
      },
      {
        "pseudo":soup.select('#player_stats_header')[0].find('th').find_next_sibling('th').find_next_sibling('th').get_text(),
        "clans":[p2_c1,p2_c2,p2_c3],
        "is_winner":p2_won,
        "lvl1_played": int(statistics.select('th:-soup-contains("Level I played")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "lvl2_played": int(statistics.select('th:-soup-contains("Level II played")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "lvl3_played": int(statistics.select('th:-soup-contains("Level III played")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "cards_drawn": int(statistics.select('th:-soup-contains("Cards drawn")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "cards_captured": int(statistics.select('th:-soup-contains("Cards captured")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "cards_destroyed": int(statistics.select('th:-soup-contains("Cards destroyed")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "cards_sacrificed": int(statistics.select('th:-soup-contains("Cards sacrificed")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "cards_shifted": int(statistics.select('th:-soup-contains("Cards shifted")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "force_of_will": int(statistics.select('th:-soup-contains("Force of will")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "activation_tokens": int(statistics.select('th:-soup-contains("Activation tokens")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip()),
        "clan_most_played": statistics.select('th:-soup-contains("Clan most played")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip(),
        "clan_most_played_last_5_turns": statistics.select('th:-soup-contains("Clan most played (last 5 turns)")')[0].find_next_sibling("td").find_next_sibling("td").get_text().strip(),
      }
    ]
    if has_first_player_infos:
      game_infos["players"][0]["is_first_player"] = p1_first_player
      game_infos["players"][1]["is_first_player"] = p2_first_player

    # coherence checks
    if (len(list(set(game_infos["players"][0]["clans"]))) < len(game_infos["players"][0]["clans"])):
      continue
    if (len(list(set(game_infos["players"][1]["clans"]))) < len(game_infos["players"][1]["clans"])):
      continue
    
    game_infos_path = "scrapping/gamestatistics/"+str(game_infos["average_rank"])+"_"+game_id+".json"
    with open(game_infos_path, 'w+') as f:
        json.dump(game_infos, f)
