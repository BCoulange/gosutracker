require "json"

# load data
data = JSON.parse(File.read("data.json"))


# [
#   {
#     "name": "491559730.html", 
#     "players": [
#       {
#         "clans": ["Galmi", "Goan-Sul", "Tomorrow"], 
#         "is_winner": true, 
#         "lvl1_played": 7,
#         "lvl2_played": 5, 
#         "lvl3_played": 1, 
#         "cards_drawn": 21, 
#         "cards_captured": 2, 
#         "cards_destroyed": 5, 
#         "cards_sacrificed": 0, 
#         "cards_shifted": 2, 
#         "force_of_will": 0, 
#         "activation_tokens": 2, 
#         "clan_most_played": 
#         "Goan-Sul", 
#         "clan_most_played_last_5_turns": 
#         "Goan-Sul", 
#         "is_first_player": true
#       },
#     ], 
#     "id": "491559730", 
#     "average_rank": 468, 
#     "creation_time": "Created 03/25/2024 at 11:21", 
#     "creation_time_month": 3, 
#     "creation_time_day": 25, 
#     "creation_time_year": 2024, 
#     "Abunakkashii": true, 
#     "duration_min": 15, 
#     "clan_passives": 
#     ["Justice", "Abunakkashii"], 
#     "victory_condition": "Winning a Great Battle by more than 10 points (Goan-Sul)", 
#     "nb_of_rounds": 1, 
#     "clans_selected": ["Galmi", "Xi'an", "Narashima", "Goan-Sul", "Tomorrow", "Phoenix"], 
#     "clans_banned": ["Abhilasha"]
#   },



output = data.map do |d|
  el = {}
  d.each do |k,v|
    if k == "players"
      d["players"].each_with_index do |pl,i|
        pl.each do |kp,vp|
          if kp != "pseudo"
            el["player#{i+1} #{kp}"] = vp
          end
        end
      end
    elsif k == "clan_passives"
      v.each_with_index do |c,ic|
        el["clan_passive_#{ic+1}"] = c
      end
    elsif k == "clans_selected"
      v.each_with_index do |c,ic|
        el["clans_selected_#{ic+1}"] = c
      end
    elsif k == "clans_banned"
      v.each_with_index do |c,ic|
        el["clans_banned_#{ic+1}"] = c
      end
    elsif !["name"].include?(k)
      el[k] = d[k]
    end
  end

  el
end

csv_lines = [output[0].keys] + output.map{|el| el.map{|k,v| v}}

File.open("data.csv","w+") do |f|
  f.write csv_lines.map{|l| l.join(";")}.join("\n")
end




