import hlt

def get_planets_by_distance(game_map, entity):
    planetList = [[planet, entity.calculate_distance_between(planet)] for planet in game_map.all_planets()]
    planetList.sort(key=lambda x: x[1])

    planetList = [planet[0] for planet in planetList]

    return planetList


def get_enemy_ships_by_distance(game_map, entity):
    enemyShipList = [[ship, entity.calculate_distance_between(ship)] for ship in game_map.all_enemy_ships()]
    enemyShipList.sort(key=lambda x: x[1])

    enemyShipList = [ship[0] for ship in enemyShipList]

    return enemyShipList