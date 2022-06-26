import hltDiscovery

def rush_on_game_start(game_map):
    #if len(game_map.all_players()) > 2:
    #   return False

    if game_map.size < hltDiscovery.constants.RUSH_MAP_SIZE_MAX:
        return True
    

def activate_rush_mode(game_map):
    if len(game_map.all_players()) > 2:
        return False

    if game_map.size < hltDiscovery.constants.RUSH_MAP_SIZE_MAX:
        return True
