import re
p = re.compile('<a\shref=\"\/table\?table=(\d+)\"')

games = p.findall(open("scrapping/gamelist.html").read())
print('found '+str(len(games))+' games')


import json
with open('scrapping/games_data.json', 'w') as f:
    json.dump([{"id": el} for el in games], f)
