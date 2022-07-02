import hltDiscovery as hlt
import logging

def get_distance_between_pos_entity(position, entity):
    entityX = entity.x
    entityY = entity.y
    positionX = position[0]
    positionY = position[1]
    return ((positionX - entityX) ** 2 + (positionY - entityY) ** 2) ** 0.5


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


def get_enemy_min_distance(game_map, entity):
    enemyShipsByDistance = get_enemy_ships_by_distance(game_map, entity)
    return entity.calculate_distance_between(enemyShipsByDistance[0])


def get_enemy_ships_in_radius(game_map, entity, radius):
    enemyShipList = []
    for ship in game_map.all_enemy_ships():
        if entity.calculate_distance_between(ship) <= radius:
            enemyShipList.append(ship)
    return enemyShipList

def get_ally_ships_in_radius(game_map, entity, radius):
    ally_ship_list = []
    for ship in game_map.get_me().free_ships():
        if entity.calculate_distance_between(ship) <= radius:
            ally_ship_list.append(ship)
    return ally_ship_list

def get_initial_planet_scores(game_map):
    MAX_RANGE_PLANETS_THRESHOLD = 40

    planet_scores = []

    for planet in game_map.all_planets():
        dockingSpots = planet.num_docking_spots
        #enemyShipsByDistance = get_enemy_ships_by_distance(game_map, planet)
        # distanceToClosetEnemy = planet.calculate_distance_between(enemyShipsByDistance[0])
        ownAverageDistanceToPlanet = 0
        ships = game_map.get_me().all_ships()
        x_sum = 0
        y_sum = 0
        for ship in ships:
            x_sum += ship.x
            y_sum += ship.y
        
        x_sum /= len(ships)
        y_sum /= len(ships)
        ownAverageDistanceToPlanet = planet.calculate_distance_between(hlt.entity.Position(x_sum, y_sum))
        distanceToCenter = planet.calculate_distance_between(hlt.entity.Position(game_map.width / 2, game_map.height / 2))
        numberOfPlanetsInRadius = len([planetInRadius for planetInRadius in game_map.all_planets() if planet.calculate_distance_between(planetInRadius) < MAX_RANGE_PLANETS_THRESHOLD - planet.radius - planetInRadius.radius])
        max_map_distance = max(game_map.width, game_map.height)

        # normalize values
        dockingSpots = (dockingSpots - 2) / (20 - 2)
        ownAverageDistanceToPlanet = ownAverageDistanceToPlanet / max_map_distance 
        numberOfPlanetsInRadius = numberOfPlanetsInRadius / len(game_map.all_planets())
        distanceToCenter = distanceToCenter / max_map_distance

        # score is best if minimal
        # dockingspots best if high, ownAverageDistanceToPlanet best if low, numberOfPlanetsInRadius best if high, distanceToCenter best if low
        evaluation_score =  2.8 * (ownAverageDistanceToPlanet/1) + 2 * (distanceToCenter/1) - 1 * (numberOfPlanetsInRadius) - 1.7 * (dockingSpots) 

        planet_scores.append([planet, evaluation_score])

    planet_scores.sort(key=lambda x: x[1])
    planet_scores = [planet[0] for planet in planet_scores]

    return planet_scores

def get_initial_planet_scores2(game_map):
    MAX_RANGE_PLANETS_THRESHOLD = 40

    planet_scores = []

    for planet in game_map.all_planets():
        dockingSpots = planet.num_docking_spots
        #enemyShipsByDistance = get_enemy_ships_by_distance(game_map, planet)
        # distanceToClosetEnemy = planet.calculate_distance_between(enemyShipsByDistance[0])
        ships = game_map.get_me().all_ships()
        x_sum = 0
        y_sum = 0
        for ship in ships:
            x_sum += ship.x
            y_sum += ship.y
        x_sum /= len(ships)
        y_sum /= len(ships)
        ownAverageDistanceToPlanet = planet.calculate_distance_between(hlt.entity.Position(x_sum, y_sum))
        evaluation_score =  ownAverageDistanceToPlanet
        planet_scores.append([planet, evaluation_score])

    planet_scores.sort(key=lambda x: x[1])
    planet_scores = [planet[0] for planet in planet_scores]
    return planet_scores

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

    if closestEnemyShipDistance < hlt.constants.RUSH_MAX_RANGE or \
        game_map.size < hlt.constants.RUSH_MAP_SIZE_MAX:
        return True

    if game_map.size < hlt.constants.RUSH_MAP_SIZE_MAX:
        return True
