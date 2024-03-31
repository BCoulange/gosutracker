# Etant donné 5 clans
# optimal draft 6th clan = clan max victory P2
# etant donné 3 clan
# optimal draft 4-5th clans = max victory P1  for each optimal draft 6th clan P2
# etant donné 1 clan
# optimal draft 2-3th clans = max victory P2 each optimal draft 4-5th clan P1
# etant donné 0 clan
# optimal draft 1st clan = max victory P1 each optimal draft 2-3th clan

require "json"
data = JSON.parse(File.read("data.json"))
MIN_DATASET_SIZE = 10

def nb_p1_victory_dataset(data)
  return data.select{|d| d["players"].select{|el| el["is_first_player"]}[0]["is_winner"]}.size
end

def optimal_6th_clan_draft(data,current_selection)
  dataset = data.select do |d| 
    (d["clans_selected"][0] == current_selection[0]) && ((d["clans_selected"][1..2]-current_selection[1..2]).size == 0) && ((d["clans_selected"][3..4]-current_selection[3..4]).size == 0)
  end
  dataset.group_by{|d| d["clans_selected"][5]}.map do |sixth_clan,g|
    v = nb_p1_victory_dataset(g)
    {
      clan_name: sixth_clan,
      nb_p1_victory: v,
      selection_size: g.size,
      pct_p1_victory: (v.to_f/g.size*100)
    }
  end.select{|el| el[:selection_size] >= MIN_DATASET_SIZE}.sort_by{|el| -(100-el[:pct_p1_victory])}[0] # max victory P2
end

def optimal_45th_clan_draft(data,current_selection)
  dataset = data.select do |d| 
    (d["clans_selected"][0] == current_selection[0]) && ((d["clans_selected"][1..2]-current_selection[1..2]).size == 0)
  end
  dataset.group_by{|d| d["clans_selected"][3..4].sort}.map do |fourfifth_clan,g|
    # find the optimal next clan
    {
      fourfifth_clan: fourfifth_clan,
      best_scenario: optimal_6th_clan_draft(g,current_selection + fourfifth_clan)
    }
  end.select{|el| !el[:best_scenario].nil?}.sort_by{|el| -(el[:best_scenario][:pct_p1_victory])}[0] # max victory P1
end

def optimal_23th_clan_draft(data,current_selection)
  dataset = data.select do |d| 
    (d["clans_selected"][0] == current_selection[0]) 
  end
  dataset.group_by{|d| d["clans_selected"][1..2].sort}.map do |secondthird_clan,g|
    # find the optimal next clan
    {
      secondthird_clan: secondthird_clan,
      best_scenario: optimal_45th_clan_draft(g,current_selection + secondthird_clan)
    }
  end.select{|el| !el[:best_scenario].nil?}.sort_by{|el| -(100-el[:best_scenario][:best_scenario][:pct_p1_victory])}[0] # max victory P2
end

def optimal_1st_clan_draft(data)
  res = data.group_by{|d| d["clans_selected"][0]}.map do |first_clan,g|
    # find the optimal next clan
    {
      first_clan: first_clan,
      best_scenario: optimal_23th_clan_draft(g,[first_clan])
    }
  end.select{|el| !el[:best_scenario].nil?}.sort_by{|el| -(el[:best_scenario][:best_scenario][:best_scenario][:pct_p1_victory])}[0] # max victory P1
  {
    draft: [
      res[:first_clan],
      res[:best_scenario][:secondthird_clan][0],
      res[:best_scenario][:secondthird_clan][1],
      res[:best_scenario][:best_scenario][:fourfifth_clan][0],
      res[:best_scenario][:best_scenario][:fourfifth_clan][1],
      res[:best_scenario][:best_scenario][:best_scenario][:clan_name]
    ],
    pct_p1_victory:  res[:best_scenario][:best_scenario][:best_scenario][:pct_p1_victory],
    dataset_size: res[:best_scenario][:best_scenario][:best_scenario][:selection_size]
  }
end

puts(optimal_1st_clan_draft(data))

