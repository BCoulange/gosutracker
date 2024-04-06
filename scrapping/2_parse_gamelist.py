import re
from datetime import datetime, timedelta
from os.path import exists

p = re.compile(r'<a\shref=\"\/table\?table=(\d+)\"')
p2 = re.compile(r'<span\sclass=\"postdate\">([^<]+)<\/span>')

games = p.findall(open("scrapping/gamelist.html").read())
postdates = p2.findall(open("scrapping/gamelist.html").read())

print('found '+str(len(games))+' games')

def relative_to_absolute(relative_time):
    now = datetime.now()
    min_reg = re.compile(r'(\d+) minutes? ago')
    hour_reg = re.compile(r'(\d+) hours? ago')
    hour30_reg = re.compile(r'(\d+) h (\d+) m ago')
    day_reg = re.compile(r'(\d+) days? ago')

    if min_reg.match(relative_time):
        m = min_reg.search(relative_time)
        delta = int(m.group(1))
        absolute_time = now - timedelta(minutes=delta)
    elif hour_reg.match(relative_time):
        m = hour_reg.search(relative_time)
        delta = int(m.group(1))
        absolute_time = now - timedelta(hours=delta)
    elif hour30_reg.match(relative_time):
        m = hour30_reg.search(relative_time)
        absolute_time = now - timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
    elif day_reg.match(relative_time):
        m = day_reg.search(relative_time)
        absolute_time = now - timedelta(days=int(m.group(1)))
    else:
        print(relative_time)
        raise ValueError("Unsupported time format")

    return int(absolute_time.timestamp())

def absolute_to_iso(absolute_time):
    return absolute_time.isoformat()

postdates = [absolute_to_iso(datetime.fromtimestamp(relative_to_absolute(el))) for el in postdates]



import json
with open('scrapping/games_data.json', 'w') as f:
    json.dump([{
        "id": games[i]
        "date":postdates[i]
    } for i in range(len(games))], f)

    for i in range(len(games)):
        date_path = 'scrapping/enddates/'+str(games[i])+".json"
        if not exists(date_path):
            with open(date_path,"w+") as f2:
                json.dump({
                "id": games[i],
                "date":postdates[i]
            }, f2)

