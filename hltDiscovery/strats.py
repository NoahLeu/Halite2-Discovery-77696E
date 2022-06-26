import logging
import hltDiscovery

def rush_on_game_start(game_map):
    if len(game_map.all_players()) > 2:
       return False

    myShips = game_map.get_me().all_ships()
    enemyShips = game_map.all_enemy_ships()
    closestEnemyShipDistance = float('inf')
    for enemyShip in enemyShips:
        for myShip in myShips:
            distance = myShip.calculate_distance_between(enemyShip)
            if distance < closestEnemyShipDistance:
                closestEnemyShipDistance = distance


    logging.info("closestEnemyShipDistance: " + str(closestEnemyShipDistance))
    if closestEnemyShipDistance < hltDiscovery.constants.RUSH_MAX_RANGE:
        return True


    if game_map.size < hltDiscovery.constants.RUSH_MAP_SIZE_MAX:
        return True
    

def activate_rush_mode(game_map):
    if len(game_map.all_players()) > 2:
        return False

    if game_map.size < hltDiscovery.constants.RUSH_MAP_SIZE_MAX:
        return True
