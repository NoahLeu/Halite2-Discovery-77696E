from errno import EALREADY
import hlt
import logging
import math
import time

game = hlt.Game("Discovery 0.6")
logging.info("Starting my Discovery!")


ALLOW_DOCKING = True

# focus on getting first planet
EARLY_GAME = True
# rush to enemy and destroy fast
RUSH_MODE = False
# focus on expanding and destroying enemies
MID_GAME = False

turn = -1

# ship_after_turn_positions = []

while True:
    # Do not exceed MAX_TURN_LENGTH
    # startOfTurn = time.time()

    game_map = game.update_map()

    command_queue = []

    turn += 1

    planets = [planet for planet in game_map.all_planets() if planet.remaining_resources > 0]

    planets_owned = 0
    for planet in planets:
        if planet.is_owned():
            planets_owned += 1
            continue

    if turn == 0 and hlt.strats.rush_on_game_start(game_map):
        RUSH_MODE = True
        logging.info("RUSH MODE ACTIVATED")
        # ALLOW_DOCKING = False

    # get all ships
    my_free_ships = game_map.get_me().free_ships()
    my_docked_ships = game_map.get_me().docked_ships()
    my_docking_ships = game_map.get_me().docking_ships()
    my_undocking_ships = game_map.get_me().undocking_ships()

    my_ship_count = len(game_map.get_me().all_ships())

    # get all enemy ships
    enemy_ships = game_map.all_enemy_ships()
    # get all enemy planets
    enemy_planets = game_map.all_enemy_planets()

    min_enemy_distance = 9999999


    if EARLY_GAME or RUSH_MODE:
        # ! heavy calculation here    
        # for every ship find distance to closest enemy ship
        for ship in my_free_ships + my_docked_ships + my_docking_ships + my_undocking_ships:
            # find distance to closest enemy ship
            closest_enemy_ship = None
            closest_enemy_ship_distance = 9999999
            for enemy_ship in enemy_ships:
                distance = ship.calculate_distance_between(enemy_ship)
                if distance < closest_enemy_ship_distance:
                    closest_enemy_ship = enemy_ship
                    closest_enemy_ship_distance = distance

            if closest_enemy_ship_distance < min_enemy_distance:
                min_enemy_distance = closest_enemy_ship_distance


    if EARLY_GAME and (turn > hlt.constants.EARLY_GAME_MAX_TURNS or \
        my_ship_count > hlt.constants.EARLY_GAME_MAX_SHIPS or \
        min_enemy_distance < hlt.constants.EARLY_GAME_SAFE_DISTANCE):

        EARLY_GAME = False
        MID_GAME = True

    logging.info("min_enemy_distance: " + str(min_enemy_distance))

    #if turn > hlt.constants.RUSH_MAX_TURNS or \
     #   min_enemy_distance > hlt.constants.RUSH_MAX_RANGE:
      #  logging.info("RUSH MODE DEACTIVATED")
       # RUSH_MODE = False

    if RUSH_MODE:
        logging.info("RUSH MODE")
        # attack enemy ships and destroy them without docking
        first_ship = my_free_ships[0]
        # find closest enemy ship

        for ship in game_map.get_me().all_ships():
            logging.info("ship: " + str(ship))

        for ship in game_map.get_me().all_ships():
            # logging.info("ship: " + str(ship))
            enemy_by_distance = hlt.calculations.get_enemy_ships_by_distance(game_map, first_ship)
            for enemy in enemy_by_distance:
                ship_to_enemy_distance = ship.calculate_distance_between(enemy)
                if ship_to_enemy_distance < 6:
                    continue
                else:
                    ship_speed = int(hlt.constants.MAX_SPEED)

                    if ship_to_enemy_distance <= 5:
                        continue

                    if ship_to_enemy_distance <= 12:
                        ship_speed = int(ship_to_enemy_distance - 5)

                    # ship simulate movement

                    navigate_command = ship.navigate(ship.closest_point_to(enemy), game_map, speed=ship_speed)
                    if navigate_command:
                        #ship_after_turn_positions.append((ship.x, ship.y))
                        command_queue.append(navigate_command)
                        break
                    break
            
        
    else:
        if EARLY_GAME:
            continue
        
        if not EARLY_GAME and MID_GAME:
            for ship in game_map.get_me().all_ships():
                if ship.docking_status != ship.DockingStatus.UNDOCKED:
                    # check if the docked planet is still a viable planet
                    # if not, undock and set the ship free again
                    if ship.planet.remaining_resources == 0:
                        command_queue.append(ship.undock())
                    continue

                planet_distance_list = [[planet, ship.calculate_distance_between(planet)] for planet in planets]
                planet_distance_list.sort(key=lambda x: x[1])

                for planet in planet_distance_list:
                    # planet has owner
                    if planet[0].is_owned():
                        # planet belongs to me and is not full
                        if planet[0].all_docked_ships()[0].owner == game_map.get_me() and not planet[0].is_full() and not planet[0].remaining_resources == 0:
                            if ship.can_dock(planet[0]):
                                command_queue.append(ship.dock(planet[0]))
                                #ship_after_turn_positions.append((ship.x, ship.y))
                                break
                            else:
                                navigate_command = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(hlt.constants.MAX_SPEED))
                                if navigate_command:
                                    #ship_after_turn_positions.append((ship.x, ship.y))
                                    command_queue.append(navigate_command)
                                    # remove planet from list
                                    planets.remove(planet[0])
                                    break
                                break
                        # planet belongs to me and is full
                        elif planet[0].all_docked_ships()[0].owner == game_map.get_me() and planet[0].is_full():
                            continue
                        # planet belongs to enemy
                        elif planet[0].all_docked_ships()[0].owner != game_map.get_me():
                            enemy_ships_at_planet_sorted_distance = [[e_ship, ship.calculate_distance_between(e_ship)] for e_ship in planet[0].all_docked_ships()]
                            enemy_ships_at_planet_sorted_distance.sort(key=lambda x: x[1])

                            ship_to_enemy_distance = enemy_ships_at_planet_sorted_distance[0][1]
                            if ship_to_enemy_distance < 6:
                                continue
                            else:
                                ship_speed = int(hlt.constants.MAX_SPEED)
                                if ship_to_enemy_distance <= 12:
                                    ship_speed = int(ship_to_enemy_distance - 5)

                                navigate_command = ship.navigate(ship.closest_point_to(enemy_ships_at_planet_sorted_distance[0][0]), game_map, speed=ship_speed)
                                if navigate_command:
                                    #ship_after_turn_positions.append((ship.x, ship.y))
                                    command_queue.append(navigate_command)
                                    break
                                break
                    # planet has no owner
                    else:
                        if ship.can_dock(planet[0]):
                            command_queue.append(ship.dock(planet[0]))
                            # ship_after_turn_positions.append((ship.x, ship.y))
                            break
                        else:
                            navigate_command = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(hlt.constants.MAX_SPEED))
                            if navigate_command:
                                #ship_after_turn_positions.append((ship.x, ship.y))
                                command_queue.append(navigate_command)
                                # remove planet from list
                                planets.remove(planet[0])
                                break
                            break
        
    # ship_after_turn_positions = []

    game.send_command_queue(command_queue)
