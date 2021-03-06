import hltDiscovery as hlt
import logging
import math
import time

from hltDiscovery.calculations import get_planets_by_distance

game = hlt.Game("Discovery 0.8 EARLY 2")
logging.info("Starting my Discovery!")

turn = -1

RUSH_MODE = False
EARLY_GAME = True
MID_GAME = False

while True:
    turn_start = time.time()
    game_map = game.update_map()
    command_queue = []
    new_ship_positions = []
    turn += 1
    planets = [planet for planet in game_map.all_planets() if planet.remaining_resources > 0]

    planets_owned = 0
    for planet in planets:
        if planet.is_owned():
            planets_owned += 1
            continue
    
    my_planets = [planet for planet in game_map.all_planets() if planet.owner == game_map.get_me()]
    my_planets_owned = len(my_planets)
    
    if turn == 0:
        planet_priority_list = hlt.calculations.get_initial_planet_scores2(game_map)

    if turn == 0 and hlt.calculations.rush_on_game_start(game_map):
        RUSH_MODE = True
        EARLY_GAME = False
        logging.info("RUSH MODE ACTIVATED TURN 0")

    my_free_ships = game_map.get_me().free_ships()
    my_docked_ships = game_map.get_me().docked_ships()
    my_docking_ships = game_map.get_me().docking_ships()
    my_undocking_ships = game_map.get_me().undocking_ships()
    my_ship_count = len(game_map.get_me().all_ships())
    enemy_ships = game_map.all_enemy_ships()
    enemy_planets = game_map.all_enemy_planets()
    all_planets = game_map.all_planets()
    ships_going_to_planet = {}
    for planet in all_planets:
        ships_going_to_planet[planet.id] = 0
    ships_following_enemy = {}
    for e_ship in enemy_ships:
        ships_following_enemy[e_ship.id] = 0

    if RUSH_MODE:
        EARLY_GAME = False
        MID_GAME = False

    if EARLY_GAME and (turn > hlt.constants.EARLY_GAME_MAX_TURNS or \
        my_ship_count >= hlt.constants.EARLY_GAME_MAX_SHIPS):
        EARLY_GAME = False
        MID_GAME = True

    logging.info("Turn: " + str(turn))
    logging.info("Current mode: EARLY_GAME = {}, RUSH_MODE = {}, MID_GAME = {}".format(EARLY_GAME, RUSH_MODE, MID_GAME))

    if EARLY_GAME:
        allow_docking_for_ship = {}
        ships_in_critical_zone = set()
        my_ships = game_map.get_me().all_ships()

        closest_enemy_dist = float("inf")
        my_closest_to_enemy = my_ships[0].id 
        closest_enemy_ship = enemy_ships[0]

        # find closest enemy and my closest ship to that enemy
        for ship in my_ships:
            allow_docking_for_ship[ship.id] = True
            for e_ship in enemy_ships:
                ship_to_enemy_distance = ship.calculate_distance_between(e_ship)
                if ship_to_enemy_distance < hlt.constants.EARLY_GAME_ENEMY_RADIUS:
                    ships_in_critical_zone.add(e_ship)

                if ship_to_enemy_distance < closest_enemy_dist:
                    closest_enemy_dist = ship_to_enemy_distance
                    my_closest_to_enemy = ship.id
                    closest_enemy_ship = e_ship

        ships_in_critical_zone_count = len(ships_in_critical_zone)

        if len(enemy_ships) > 3:
            ships_in_critical_zone_count = 0

        #if ships_in_critical_zone_count == 0:
            #logging.info("0 SHIPS IN CRITICAL ZONE -> SAFE TO GO TO PLANETS")

        # disable docking for one ship and protect own docking ships
        if ships_in_critical_zone_count == 1:
            #logging.info("1 SHIP IN CRITICAL ZONE")
            # find closest ship to enemy that is status undocked
            my_ships_sorted = sorted(my_ships, key=lambda ship: ship.calculate_distance_between(closest_enemy_ship))

            found_undocked_ship = False
            for ship in my_ships_sorted:
                if ship.docking_status == ship.DockingStatus.UNDOCKED:
                    allow_docking_for_ship[ship.id] = False
                    found_undocked_ship = True
                    break

            if not found_undocked_ship:
                allow_docking_for_ship[my_ships_sorted[0].id] = False

        if ships_in_critical_zone_count > 1 or (ships_in_critical_zone_count == 1 and len(enemy_ships) == 1):
            logging.info("CRITICAL ZONE RUSH")

            # check if all ships are undocked
            if len([ship for ship in my_ships if ship.docking_status == ship.DockingStatus.UNDOCKED]) == len(my_ships): 
                logging.info("activating rush")
                EARLY_GAME = False
                MID_GAME = False
                RUSH_MODE = True
            else:
                for ship in my_ships: 
                    if ship.docking_status != ship.DockingStatus.UNDOCKED:
                        command_queue.append(ship.undock())
                        new_ship_positions.append((ship.x, ship.y))

                game.send_command_queue(command_queue)
                continue
                    
        if not RUSH_MODE:
            i = 0
            my_ship_positions = [(ship.x, ship.y) for ship in my_ships]
            avg_ship_x = sum([ship.x for ship in my_ships]) / len(my_ships)
            avg_ship_y = sum([ship.y for ship in my_ships]) / len(my_ships)
            startPos = hlt.entity.Position(avg_ship_x, avg_ship_y)

            for ship in my_ships:
                i += 1
                if ship.docking_status != ship.DockingStatus.UNDOCKED:
                    new_ship_positions.append((ship.x, ship.y))
                    if not allow_docking_for_ship[ship.id]:
                        command_queue.append(ship.undock())
                    continue
                    
                # if ship is allowed to dock go to planet
                if allow_docking_for_ship[ship.id]:
                    logging.info("SHIP {} ALLOWED TO DOCK".format(ship.id))
                    #planet_priority_list = planets

                    #closest_planet = None
                    #closest_planet_distance = float("inf")
                    #for planet in planet_priority_list:
                    #    planet=planet[0]
                    #    planet_distance = ship.calculate_distance_between(planet)
                    #    if planet_distance < closest_planet_distance:
                    #        closest_planet_distance = planet_distance
                    #        closest_planet = planet 

                    if my_planets_owned > 0:
                        planet_priority_list = get_planets_by_distance(game_map, ship)

                    for planet in planet_priority_list:
                        if i == 1:
                            planet_first_choice = planet
                        elif planet_first_choice is not None:
                            planet = planet_first_choice
                        #planet = planet[0]

                        # navigate to planet
                        # ? potentially spread out if no enemy ships are nearby
                        # ? potentially spread out if no enemy ships are nearby
                        # ? potentially spread out if no enemy ships are nearby

                        #planet_enemy_radius = ship.calculate_distance_between(planet)
                        #if ships_going_to_planet[planet.id] < planet.num_docking_spots + len(hlt.calculations.get_enemy_ships_in_radius(game_map, planet, planet_enemy_radius)) + 2:

                        # planet has owner
                        if planet.is_owned():
                            # planet belongs to me and is not full
                            if planet.all_docked_ships()[0].owner == game_map.get_me() and not planet.is_full():
                                if ship.can_dock(planet):
                                    logging.info("DOCKING OWNED")
                                    command_queue.append(ship.dock(planet))
                                    new_ship_positions.append((ship.x, ship.y))
                                    ships_going_to_planet[planet.id] += 1
                                    break
                                else:
                                    logging.info("MOVE TO OWNED PLANET")
                                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(hlt.constants.MAX_SPEED), max_corrections=120, new_ship_positions = new_ship_positions)
                                    new_ship_positions.append((x, y))
                                    if navigate_command:
                                        command_queue.append(navigate_command)
                                        ships_going_to_planet[planet.id] += 1
                                        break
                                    break
                            # planet belongs to me and is full
                            elif planet.all_docked_ships()[0].owner == game_map.get_me() and planet.is_full():
                                # move to planet and wait there if ship count <= 3 otherwise continue
                                if len(my_ships) > 3:
                                    continue

                                if ship.can_dock(planet):
                                    #logging.info("WAITING FOR ACTION")
                                    break
                                else:
                                    #logging.info("MOVE TO OWNED PLANET")
                                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(hlt.constants.MAX_SPEED), max_corrections=120, new_ship_positions = new_ship_positions)
                                    new_ship_positions.append((x, y))
                                    if navigate_command:
                                        command_queue.append(navigate_command)
                                        ships_going_to_planet[planet.id] += 1
                                        break
                                    break

                                # ? potentially spread out if no enemy ships are nearby
                                # ? potentially spread out if no enemy ships are nearby
                                # ? potentially spread out if no enemy ships are nearby
                            # planet belongs to enemy
                            elif planet.all_docked_ships()[0].owner != game_map.get_me():
                                # take next best planet
                                continue
                        # planet has no owner
                        else:
                            if my_planets_owned > 0 and len(my_ships) <= 3:
                                continue
                            if ship.can_dock(planet):
                                logging.info("docking at: {}".format(planet.id))
                                command_queue.append(ship.dock(planet))
                                new_ship_positions.append((ship.x, ship.y))
                                break
                            else:
                                logging.info("MOVE TO FREE PLANET")
                                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(hlt.constants.MAX_SPEED), max_corrections=120, new_ship_positions = new_ship_positions)
                                new_ship_positions.append((x, y))
                                #logging.info("NAVIGATE COMMAND: {}".format(navigate_command))
                                if navigate_command:
                                    command_queue.append(navigate_command)
                                    ships_going_to_planet[planet.id] += 1
                                    break
                                break
                
                # this ship is the only one to protect own ships
                else:
                    logging.info("SHIP {} PROTECTING".format(ship.id))
                    # stay near own docking ships and attack enemy if in radius of 40?
                    if closest_enemy_dist < hlt.constants.EARLY_GAME_PROTECTION_RADIUS:
                        # ! COPY FIGHTING BEHAVIOR FROM RUSH MODE FOR THIS SHIP
                        [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(closest_enemy_ship), game_map, speed=int(hlt.constants.MAX_SPEED), max_corrections=120, new_ship_positions = new_ship_positions)
                        new_ship_positions.append((x, y))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                    # if no enemy ships are in radius of 40, move to closest ally ship with safety distance of 15
                    else:
                        my_ships_sorted = sorted(my_ships, key=lambda ally: ally.calculate_distance_between(ship))

                        if len(my_ships_sorted) == 0:
                            continue

                        ally_ship = my_ships_sorted[0]
                        own_distance = ship.calculate_distance_between(ally_ship)

                        if own_distance == hlt.constants.EARLY_GAME_ALLY_RADIUS:
                            continue
                            
                        elif own_distance < hlt.constants.EARLY_GAME_ALLY_RADIUS:
                            ally_x = ally_ship.x
                            ally_y = ally_ship.y
                            own_x = ship.x
                            own_y = ship.y
                            angle = ship.calculate_angle_between(ally_ship)
                            x = own_x + math.cos(angle) * (hlt.constants.EARLY_GAME_ALLY_RADIUS - own_distance)
                            y = own_y + math.sin(angle) * (hlt.constants.EARLY_GAME_ALLY_RADIUS - own_distance)
                            target_position = hlt.entity.Position(x, y) 
                            [navigate_command, (x, y)] = ship.navigate(target_position, game_map, speed=int(hlt.constants.MAX_SPEED), max_corrections=120, new_ship_positions = new_ship_positions)
                            new_ship_positions.append((x, y))
                            if navigate_command:
                                command_queue.append(navigate_command)
                                break
                            break

    if RUSH_MODE:
        logging.info("RUSH MODE")
        EARLY_GAME = False
        MID_GAME = False

        # fight will all available ships
        #logging.info("RUSH MODE")
        first_ship = game_map.get_me().all_ships()[0]

        for ship in game_map.get_me().all_ships():
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                command_queue.append(ship.undock())
                new_ship_positions.append((ship.x, ship.y))
                continue

            enemy_by_distance = hlt.calculations.get_enemy_ships_by_distance(game_map, first_ship)
            for enemy in enemy_by_distance:
                ship_to_enemy_distance = ship.calculate_distance_between(enemy)

                if ship_to_enemy_distance <= 5:
                    continue

                ship_speed = int(hlt.constants.MAX_SPEED)

                if ship_to_enemy_distance <= 12:
                    ship_speed = int(ship_to_enemy_distance - 5)

                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(enemy), game_map, speed=ship_speed, max_corrections=120, new_ship_positions = new_ship_positions)
                new_ship_positions.append((x, y))
                logging.info("nav command: {}".format(navigate_command))
                if navigate_command:
                    command_queue.append(navigate_command)
                    break
                break

    elif MID_GAME:
        #logging.info("MID GAME")
        for ship in game_map.get_me().all_ships():
            current_time = time.time()
            if current_time - turn_start > hlt.constants.MAX_TURN_LENGTH:
                logging.info("Turn time exceeded")
                break

            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                if ship.planet.remaining_resources == 0:
                    command_queue.append(ship.undock())
                    new_ship_positions.append((ship.x, ship.y))
                    continue

                #enemy_ship_close_count = len(hlt.calculations.get_enemy_ships_in_radius(game_map, planet, hlt.constants.MID_GAME_ENEMY_RADIUS))
                #ally_ship_close_count = len(hlt.calculations.get_ally_ships_in_radius(game_map, planet, hlt.constants.MID_GAME_ENEMY_RADIUS))

                #if enemy_ship_close_count - ally_ship_close_count > 0:
                #    command_queue.append(ship.undock())
                #    new_ship_positions.append((ship.x, ship.y))

                continue
                
            entities_by_distance = game_map.nearby_enemies_and_planets_by_distance(ship)

            for entity in entities_by_distance:
                current_time = time.time()
                if current_time - turn_start > hlt.constants.MAX_TURN_LENGTH:
                    logging.info("Turn time exceeded")
                    break
                if isinstance(entity, hlt.entity.Planet):
                    planet = entity
                    planet_enemy_radius = ship.calculate_distance_between(planet)
                    if ships_going_to_planet[planet.id] < planet.num_docking_spots + len(hlt.calculations.get_enemy_ships_in_radius(game_map, planet, planet_enemy_radius)) + 2:
                        # planet has owner
                        if planet.is_owned():
                            # planet belongs to me and is not full
                            if planet.all_docked_ships()[0].owner == game_map.get_me() and not planet.is_full():
                                if ship.can_dock(planet):
                                    command_queue.append(ship.dock(planet))
                                    new_ship_positions.append((ship.x, ship.y))
                                    ships_going_to_planet[planet.id] += 1
                                    break
                                else:
                                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(hlt.constants.MAX_SPEED), new_ship_positions = new_ship_positions)
                                    new_ship_positions.append((x, y))
                                    if navigate_command:
                                        command_queue.append(navigate_command)
                                        ships_going_to_planet[planet.id] += 1
                                        break
                                    break
                            # planet belongs to me and is full
                            elif planet.all_docked_ships()[0].owner == game_map.get_me() and planet.is_full():
                                continue
                            # planet belongs to enemy
                            elif planet.all_docked_ships()[0].owner != game_map.get_me():
                                enemy_ships_at_planet_sorted_distance = [[e_ship, ship.calculate_distance_between(e_ship)] for e_ship in planet.all_docked_ships()]
                                enemy_ships_at_planet_sorted_distance.sort(key=lambda x: x[1])

                                ship_to_enemy_distance = enemy_ships_at_planet_sorted_distance[0][1]
                                if ship_to_enemy_distance < 6:
                                    continue
                                else:
                                    ship_speed = int(hlt.constants.MAX_SPEED)
                                    if ship_to_enemy_distance <= 12:
                                        ship_speed = int(ship_to_enemy_distance - 5)

                                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(enemy_ships_at_planet_sorted_distance[0][0]), game_map, speed=ship_speed, new_ship_positions = new_ship_positions)
                                    new_ship_positions.append((x, y))
                                    if navigate_command:
                                        command_queue.append(navigate_command)
                                        ships_going_to_planet[planet.id] += 1
                                        break
                                    break
                        # planet has no owner
                        else:
                            if ship.can_dock(planet):
                                command_queue.append(ship.dock(planet))
                                new_ship_positions.append((ship.x, ship.y))
                                break
                            else:
                                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(hlt.constants.MAX_SPEED), new_ship_positions = new_ship_positions)
                                new_ship_positions.append((x, y))
                                if navigate_command:
                                    command_queue.append(navigate_command)
                                    ships_going_to_planet[planet.id] += 1
                                    break
                                break

                else:
                    logging.info("Enemy detected")
                    enemy_ship = entity

                    # if enemy has planets, planets are available and i dont own all of them:

                    # ? doesnt currently improve performance
                    #if turn <= 100 and len(enemy_planets) > 0 and (len(planets) > 0 and planets_owned <= len(planets)):
                    #    if ships_following_enemy[enemy_ship.id] >= 3:
                    #        logging.info("skip, enemy_follow_count: " + str(ships_following_enemy[enemy_ship.id]))
                    #        continue
                    #    
                    #    else:
                    #        logging.info("following enemy")
                    #        ships_following_enemy[enemy_ship.id] += 1

                    own_distance = ship.calculate_distance_between(enemy_ship)

                    if own_distance == hlt.constants.WEAPON_RADIUS:
                        continue
                        
                    elif own_distance < hlt.constants.WEAPON_RADIUS:
                        enemy_x = enemy_ship.x
                        enemy_y = enemy_ship.y
                        own_x = ship.x
                        own_y = ship.y
                        angle = ship.calculate_angle_between(enemy_ship)
                        x = own_x + math.cos(angle) * (hlt.constants.WEAPON_RADIUS - own_distance)
                        y = own_y + math.sin(angle) * (hlt.constants.WEAPON_RADIUS - own_distance)
                        target_position = hlt.entity.Position(x, y) 
                        [navigate_command, (x, y)] = ship.navigate(target_position, game_map, speed=int(hlt.constants.MAX_SPEED), new_ship_positions = new_ship_positions)
                        new_ship_positions.append((x, y))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break

                    else:
                        ship_speed = int(hlt.constants.MAX_SPEED) 

                        if own_distance <= 12:
                            ship_speed = int(own_distance - 5)

                        [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(enemy_ship), game_map, speed=ship_speed, new_ship_positions = new_ship_positions)
                        new_ship_positions.append((x, y))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break

    game.send_command_queue(command_queue)