import hlt

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




def get_enemy_ships_in_radius(game_map, entity, radius):
    enemyShipList = []
    for ship in game_map.all_enemy_ships():
        if entity.calculate_distance_between(ship) <= radius:
            enemyShipList.append(ship)
    return enemyShipList


def get_initial_planet_scores(game_map):
    # größe (docking spots)
    # (entfernung zu den anderem Spieler)
    # entfernung zu sich selbst
    # entfernung zur durschnittsposition unserer Schiffe
    # entfernung zu anderen planeten bzw. anzahl von planeten in radius X um PLanet
    # entfernung zur mitte des spielfeldes (näher zur mitte = besser)

    # score niedriger = besser

    MAX_RANGE_PLANETS_THRESHOLD = 40

    planet_scores = []

    for planet in game_map.all_planets():
        dockingSpots = planet.num_docking_spots

        enemyShipsByDistance = get_enemy_ships_by_distance(game_map, planet)
        distanceToClosetEnemy = planet.calculate_distance_between(enemyShipsByDistance[0])

        ownAverageDistanceToPlanet = 0
        for ship in game_map.get_me().all_ships():
            ownAverageDistanceToPlanet += planet.calculate_distance_between(ship) - planet.radius
        ownAverageDistanceToPlanet = ownAverageDistanceToPlanet / len(game_map.get_me().all_ships())

        distanceToCenter = get_distance_between_pos_entity([0,0], planet) - planet.radius

        numberOfPlanetsInRadius = len([planetInRadius for planetInRadius in game_map.all_planets() if planet.calculate_distance_between(planetInRadius) < MAX_RANGE_PLANETS_THRESHOLD - planet.radius - planetInRadius.radius])

        # CHANGE PRIOS HERE
        # dockingSpots: [2, 20]
        # ownAverageDistanceToPlanet: [0, 200]
        # numberOfPlanetsInRadius: [0, 10]
        # distanceToCenter: [0, 250]

        score = 400/dockingSpots + ownAverageDistanceToPlanet/1 + 1000/numberOfPlanetsInRadius + distanceToCenter/1.5

        planet_scores.append([planet, score])

    planet_scores.sort(key=lambda x: x[1])

    return planet_scores

def get_initial_planet_scores2(game_map):
    # größe (docking spots)
    # (entfernung zu den anderem Spieler)
    # entfernung zu sich selbst
    # entfernung zur durschnittsposition unserer Schiffe
    # entfernung zu anderen planeten bzw. anzahl von planeten in radius X um PLanet
    # entfernung zur mitte des spielfeldes (näher zur mitte = besser)

    # score niedriger = besser

    MAX_RANGE_PLANETS_THRESHOLD = 40

    planet_scores = []

    for planet in game_map.all_planets():
        dockingSpots = planet.num_docking_spots

        enemyShipsByDistance = get_enemy_ships_by_distance(game_map, planet)
        distanceToClosetEnemy = planet.calculate_distance_between(enemyShipsByDistance[0])

        ownAverageDistanceToPlanet = 0
        for ship in game_map.get_me().all_ships():
            ownAverageDistanceToPlanet += planet.calculate_distance_between(ship) - planet.radius
        ownAverageDistanceToPlanet = ownAverageDistanceToPlanet / len(game_map.get_me().all_ships())

        distanceToCenter = get_distance_between_pos_entity([0,0], planet) - planet.radius

        numberOfPlanetsInRadius = len([planetInRadius for planetInRadius in game_map.all_planets() if planet.calculate_distance_between(planetInRadius) < MAX_RANGE_PLANETS_THRESHOLD - planet.radius - planetInRadius.radius])

        # CHANGE PRIOS HERE
        # dockingSpots: [2, 20]
        # ownAverageDistanceToPlanet: [0, 200]
        # numberOfPlanetsInRadius: [0, 10]
        # distanceToCenter: [0, 250]

        score = 400/dockingSpots + ownAverageDistanceToPlanet/1 + 1000/numberOfPlanetsInRadius + distanceToCenter/1.8

        planet_scores.append([planet, score])

    planet_scores.sort(key=lambda x: x[1])

    return planet_scores
