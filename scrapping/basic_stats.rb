require "json"
require "date"

data = JSON.parse(File.read("data.json"))
gosu_clans = ["Xi'an", 'Narashima', 'Abhilasha', 'Galmi', 'Tomorrow', 'Goan-Sul','Justice', 'Phoenix','Abunakkashii']


# make 5 groups of same size
nb_groups = 2
ranks = data.map{|el| el["average_rank"]}.sort
max_rank_groups = []
for i in (0..nb_groups)
  max_rank_groups << ranks[data.size*i/nb_groups]
end

dates = data.select{|el| !el["creation_time_year"].nil?}.map{|el| Date.new(el["creation_time_year"],el["creation_time_month"],el["creation_time_day"])}
puts "#{data.size} matchs between #{dates.min} and #{dates.max}"

max_rank_groups.each_cons(2) do |r_min,r_max|
  puts "\n\n\n----- GROUP #{r_min} < ELO < #{r_max} -----\n"
  dataset = data.select{|d| (d["average_rank"] >= r_min) && ((r_max.nil?) || (d["average_rank"] < r_max)) }

  count_passives = {}
  count_passives_ext = {}
  count_ext = 0
  first_pick = {}
  first_pick_ext = {}
  meta_count = 0
  meta_oracle = 0
  victory = {}
  victory_ext = {}
  average_rank = {}
  win_trio_stats = {}
  first_player_winner = 0
  first_player_winner_ext = 0


  dataset.each do |d|
    d["players"].each do |pl|
      win_trio_stats[pl["clans"].sort.join(" - ")] = {win: 0, lose: 0} if win_trio_stats[pl["clans"].sort.join(" - ")].nil?
      if pl["is_winner"]
        "boo"
        win_trio_stats[pl["clans"].sort.join(" - ")][:win] = win_trio_stats[pl["clans"].sort.join(" - ")][:win] + 1
      else
        win_trio_stats[pl["clans"].sort.join(" - ")][:lose] = win_trio_stats[pl["clans"].sort.join(" - ")][:lose] + 1
      end
    end

    if (d["players"].select{|el| el["is_winner"]}.first["is_first_player"])
      if d["Abunakkashii"]
        first_player_winner_ext += 1
      else
        first_player_winner += 1
      end
    end

    if d["Abunakkashii"]
      count_ext += 1
    end

    
    if d["Abunakkashii"]
      if victory_ext[d["victory_condition"]].nil?
        victory_ext[d["victory_condition"]] = 1
      else
        victory_ext[d["victory_condition"]] += 1
      end
    else
      if victory[d["victory_condition"]].nil?
        victory[d["victory_condition"]] = 1
      else
        victory[d["victory_condition"]] += 1
      end
    end


    if d["Abunakkashii"]
      if first_pick_ext[d["clans_selected"][0]].nil?
        first_pick_ext[d["clans_selected"][0]] = 1
      else
        first_pick_ext[d["clans_selected"][0]] += 1
      end
    else
      if first_pick[d["clans_selected"][0]].nil?
        first_pick[d["clans_selected"][0]] = 1
      else
        first_pick[d["clans_selected"][0]] += 1
      end
    end

    if d["clans_selected"][0] == "Abhilasha"
      if d["clans_banned"].nil? || ((d["clans_banned"] - ["Xi'an","Galmi"]).size > 0)
        meta_oracle +=1
        if (d["clans_selected"][0..2] - ["Abhilasha","Xi'an","Galmi"]) == []
          meta_count += 1
        end
      end
    end

    d["clan_passives"].each do |el|
      if d["Abunakkashii"]
        if count_passives_ext[el].nil?
          count_passives_ext[el] = 1
        else
          count_passives_ext[el] = count_passives_ext[el] + 1
        end
      else
        if count_passives[el].nil?
          count_passives[el] = 1
        else
          count_passives[el] = count_passives[el] + 1
        end
      end
    end
  end

  puts "#{count_ext}/#{dataset.size} parties avec ext"

  puts "without ext ---"
  puts "- PASSIVES"
  count_passives.sort_by{|k,v| -v}.each do |k,v|
    puts "#{k} : #{(v.to_f/(dataset.size-count_ext)*100).to_i}% (#{v}/#{dataset.size-count_ext})"
  end
  puts "- First Pick"
  first_pick.sort_by{|k,v| -v}.each do |k,v|
    puts "#{k} : #{(v.to_f/(dataset.size-count_ext)*100).to_i}% (#{v}/#{dataset.size-count_ext})"
  end
  puts "- Victory"
  victory.sort_by{|k,v| -v}.each do |k,v|
    puts "#{k} : #{(v.to_f/(dataset.size-count_ext)*100).to_i}% (#{v}/#{dataset.size-count_ext})"
  end
  puts "FIRST PLAYER WINNER (no ext) : #{(first_player_winner.to_f/(dataset.size-count_ext)*100).to_i} (#{first_player_winner}/#{(dataset.size-count_ext)})"


  puts "\n\n with ext ---"
  puts "- PASSIVES"
  count_passives_ext.sort_by{|k,v| -v}.each do |k,v|
    puts "#{k} : #{(v.to_f/count_ext*100).to_i}% (#{v}/#{count_ext})"
  end
  puts "- First Pick"
  first_pick_ext.sort_by{|k,v| -v}.each do |k,v|
    puts "#{k} : #{(v.to_f/(count_ext)*100).to_i}% (#{v}/#{count_ext})"
  end
  puts "- Victory"
  victory_ext.sort_by{|k,v| -v}.each do |k,v|
    puts "#{k} : #{(v.to_f/(count_ext)*100).to_i}% (#{v}/#{count_ext})"
  end


  metastat = dataset.select{|d| (d["clans_selected"][0] == "Abhilasha") && (d["clans_banned"].nil? || ((d["clans_banned"] - ["Xi'an","Galmi"]).size > 0))}.map do |d|
    {
      meta_chosen: (d["clans_selected"][0..2] - ["Abhilasha","Xi'an","Galmi"]) == [],
      first_player_winner: d["players"].select{|el| el["is_winner"]}[0]["is_first_player"]
    }
  end
  metacho = metastat.select{|d| d[:meta_chosen]}.size
  metaora = metastat.size
  metafpwin = metastat.select{|d| d[:meta_chosen] && d[:first_player_winner]}.size
  puts "META #{(metacho.to_f/metaora*100).to_i}% (#{metacho}/#{metaora})"
  puts "META FP WIN #{(metafpwin.to_f/metacho*100).to_i}% (#{metafpwin}/#{metacho})"





  puts "TRIOS :"
  win_trio_stats.sort_by{|k,v| -v[:win].to_f/v[:lose]}.each do |k,v|
    if v[:win]+v[:lose] > dataset.size/10
      puts "#{k} : #{(v[:win].to_f/(v[:win]+v[:lose])*100).to_i}% (#{v[:win]}/#{v[:win]+v[:lose]})"
    end
  end

  puts "FIRST PLAYER WINNER (ext) : #{(first_player_winner_ext.to_f/(count_ext)*100).to_i} (#{first_player_winner_ext}/#{(count_ext)})"

  puts "Victory Chance First Pick : "
  wins_first_pick = {}
  dataset.group_by{|d| d["clans_selected"][0]}.each do |c,g|
    wins = g.select{|d| d["players"].select{|el| el["is_first_player"]}[0]["is_winner"]}.size
    wins_first_pick[c] = {wins: wins, tot: g.size}
  end
  wins_first_pick.sort_by{|c,el| -el[:wins].to_f/el[:tot]}.each do |c,el|
    puts "- #{c} : #{(el[:wins].to_f/el[:tot]*100).to_i}% (#{el[:wins]}/#{el[:tot]})"
  end

end

puts "----- GLOBAL -----"
win_fp = data.select{|d| d["players"].select{|el| el["is_winner"]}[0]["is_first_player"]}.size
puts "#{(win_fp.to_f/data.size*100).to_i}% win fp (#{win_fp}/#{data.size})"

metastat = data.select{|d| (d["clans_selected"][0] == "Abhilasha") && (d["clans_banned"].nil? || ((d["clans_banned"] - ["Xi'an","Galmi"]).size > 0))}.map do |d|
  {
    meta_chosen: (d["clans_selected"][0..2] - ["Abhilasha","Xi'an","Galmi"]) == [],
    first_player_winner: d["players"].select{|el| el["is_winner"]}[0]["is_first_player"]
  }
end
metacho = metastat.select{|d| d[:meta_chosen]}.size
metaora = metastat.size
metafpwin = metastat.select{|d| d[:meta_chosen] && d[:first_player_winner]}.size
puts "META #{(metacho.to_f/metaora*100).to_i}% (#{metacho}/#{metaora})"
puts "META FP WIN #{(metafpwin.to_f/metacho*100).to_i}% (#{metafpwin}/#{metacho})"

puts "CLAN BANNED : "
banned_stats = Hash[gosu_clans.map{|el| [el,0]}]
with_ban = data.select{|d| !d["clans_banned"].nil?}
with_ban.each do |d|
  d["clans_banned"].each do |el|
    banned_stats[el] += 1
  end
end

puts "oracle : #{(100.to_f/gosu_clans.size).to_i}% (#{with_ban.size/gosu_clans.size})"
banned_stats.each do |k,v|
  puts "- #{k} : #{(v.to_f/with_ban.size*100).to_i}% (#{v}/#{with_ban.size})"
end

total_nb_of_clans = 9
to_ban = (9..total_nb_of_clans).inject(:*)
base_game_configs = 8*7*6*5*4*3/6/6
max_number_of_configs = to_ban*base_game_configs
puts "max number of configs : #{max_number_of_configs}"
puts "base game configs : #{base_game_configs}"
nb_of_configs_seen = data.map{|d| (d["clans_banned"] + [d["clans_selected"][0],d["clans_selected"][3],d["clans_selected"][4]].sort + [d["clans_selected"][1],d["clans_selected"][2],d["clans_selected"][5]].sort).join("-")}.uniq.size


groups = data.map{|d| (d["clans_banned"] + [d["clans_selected"][0],d["clans_selected"][3],d["clans_selected"][4]].sort + [d["clans_selected"][1],d["clans_selected"][2],d["clans_selected"][5]].sort).join('-')}.group_by{|el| el}
# groups.sort_by{|k,v| -v.size}.each do |k,v|
#   if v.size > 5
#     puts "#{k} : #{v.size}"
#   end
# end 

threshold = 10
res = {}
groups.each do |k,v|
  siz_t = v.size
  if siz_t > threshold
    siz_t = threshold
  end
  if res[siz_t].nil?
    res[siz_t] = 0
  end
  res[siz_t] += 1
end
res.sort_by{|k,v| k}.each do |k,v|
  if k == threshold
    puts "seen more than #{k} : #{v}"
  else
    puts "seeen #{k} times : #{v}"
  end
end
puts res.map{|k,v| v}.inject(:+)

puts "#{(nb_of_configs_seen.to_f/max_number_of_configs*100).to_i}% configs seen (#{nb_of_configs_seen}/#{max_number_of_configs})"

# simulation
puts "SIMULATION"
res = {}
oracle = (1...data.size).map{|el| Random.rand(max_number_of_configs).to_i}
groups = oracle.group_by{|el| el}

threshold = 10
res = {}
groups.each do |k,v|
  siz_t = v.size
  if siz_t > threshold
    siz_t = threshold
  end
  if res[siz_t].nil?
    res[siz_t] = 0
  end
  res[siz_t] += 1
end
res.sort_by{|k,v| k}.each do |k,v|
  if k == threshold
    puts "seen more than #{k} : #{v}"
  else
    puts "seeen #{k} times : #{v}"
  end
end

# justice
elo = 200
bigelo = data.select{|el| el["average_rank"] > elo}
j = bigelo.select{|el| el["clans_selected"].include?("Justice")}
puts "#{j.size} parties avec justice"
jw = j.select{|el| el["victory_condition"] == "Turn over 3 Clan tiles (Justice)"}
puts "#{jw.size} justice victories"
puts "#{jw.size.to_f/j.size*100}%"

j = bigelo.select{|el| ([el["clans_selected"][0],el["clans_selected"][3],el["clans_selected"][4]].include?("Justice") && el["players"][0]["is_winner"]) || ([el["clans_selected"][1],el["clans_selected"][2],el["clans_selected"][5]].include?("Justice") && el["players"][1]["is_winner"])}
puts "#{j.size} parties avec justice"
jw = j.select{|el| el["victory_condition"] == "Turn over 3 Clan tiles (Justice)"}
puts "#{jw.size} justice victories"
puts "#{jw.size.to_f/j.size*100}%"