require "json"

# load data
data = JSON.parse(File.read("data.json"))

all_players_pseudo = []

data.each do |d|
  d["players"].each do |pl|
    all_players_pseudo << pl["pseudo"] unless all_players_pseudo.include?(pl["pseudo"])
    pl["pseudo"] = "user_#{all_players_pseudo.index(pl["pseudo"])}"
  end
end

File.open("data.json",'w+'){|f| f.write data.to_json}