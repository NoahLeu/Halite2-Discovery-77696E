import hltDiscovery as hlt
import logging
import math
import time

game = hlt.Game("Discovery 0.7 E NEW")
logging.info("Starting my Discovery!")

turn = -1

RUSH_MODE = False


while True:
    turn_start = time.time()
    EARLY_GAME = True
    MID_GAME = False
    game_map = game.update_map()
    command_queue = []
    new_ship_positions = []
    turn += 1
    planets = [planet for planet in game_map.all_planets()
               if planet.remaining_resources > 0]

    planets_owned = 0
    for planet in planets:
        if planet.is_owned():
            planets_owned += 1
            continue

    if turn == 0 and hlt.calculations.rush_on_game_start(game_map):
        RUSH_MODE = True
        EARLY_GAME = False
        logging.info("RUSH MODE ACTIVATED")

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

    if EARLY_GAME and (turn > hlt.constants.EARLY_GAME_MAX_TURNS or
                       my_ship_count > hlt.constants.EARLY_GAME_MAX_SHIPS):
        EARLY_GAME = False
        MID_GAME = True

    logging.info("Current mode: EARLY_GAME = {}, RUSH_MODE = {}, MID_GAME = {}".format(
        EARLY_GAME, RUSH_MODE, MID_GAME))
    # ! experimental for improving bot early game
    RUSH_MODE = False

    if RUSH_MODE:
        logging.info("RUSH MODE")
        first_ship = my_free_ships[0]

        for ship in game_map.get_me().all_ships():
            enemy_by_distance = hlt.calculations.get_enemy_ships_by_distance(
                game_map, first_ship)
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

                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(
                        enemy), game_map, speed=ship_speed, new_ship_positions=new_ship_positions)
                    new_ship_positions.append((x, y))
                    if navigate_command:
                        command_queue.append(navigate_command)
                        break
                    break

    elif EARLY_GAME:
        logging.info("EARLY GAME")

        if turn == 0:
            planet_priority_list = hlt.calculations.get_initial_planet_scores(
                game_map)

        for ship in game_map.get_me().all_ships():
            if turn != 0:
                planet_distance_list = [
                    [planet, ship.calculate_distance_between(planet)] for planet in planets]
                planet_distance_list.sort(key=lambda x: x[1])
                planet_priority_list = planet_distance_list

            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                if ship.planet.remaining_resources == 0:
                    command_queue.append(ship.undock())
                continue

            for planet in planet_priority_list:
                # planet has owner
                if planet[0].is_owned():
                    # planet belongs to me and is not full
                    if planet[0].all_docked_ships()[0].owner == game_map.get_me() and not planet[0].is_full() and not planet[0].remaining_resources == 0:
                        if ship.can_dock(planet[0]):
                            command_queue.append(ship.dock(planet[0]))
                            break
                        else:
                            [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(
                                hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
                            new_ship_positions.append((x, y))
                            if navigate_command:
                                command_queue.append(navigate_command)
                                break
                            break
                    # planet belongs to me and is full
                    elif planet[0].all_docked_ships()[0].owner == game_map.get_me() and planet[0].is_full():
                        continue
                    # planet belongs to enemy
                    elif planet[0].all_docked_ships()[0].owner != game_map.get_me():
                        enemy_ships_at_planet_sorted_distance = [[e_ship, ship.calculate_distance_between(
                            e_ship)] for e_ship in planet[0].all_docked_ships()]
                        enemy_ships_at_planet_sorted_distance.sort(
                            key=lambda x: x[1])

                        ship_to_enemy_distance = enemy_ships_at_planet_sorted_distance[0][1]
                        if ship_to_enemy_distance < 6:
                            continue
                        else:
                            ship_speed = int(hlt.constants.MAX_SPEED)
                            if ship_to_enemy_distance <= 12:
                                ship_speed = int(ship_to_enemy_distance - 5)

                            [navigate_command, (x, y)] = ship.navigate(
                                enemy_ships_at_planet_sorted_distance[0][0], game_map, speed=ship_speed, new_ship_positions=new_ship_positions)
                            new_ship_positions.append((x, y))
                            if navigate_command:
                                command_queue.append(navigate_command)
                                break
                            break
                # planet has no owner
                else:
                    if ship.can_dock(planet[0]):
                        command_queue.append(ship.dock(planet[0]))
                        break
                    else:
                        [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(
                            hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
                        new_ship_positions.append((x, y))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break

    elif MID_GAME:
        logging.info("MID GAME")
        for ship in game_map.get_me().all_ships():
            current_time = time.time()
            if current_time - turn_start > hlt.constants.MAX_TURN_LENGTH:
                logging.info("Turn time exceeded")
                break

            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                if ship.planet.remaining_resources == 0:
                    command_queue.append(ship.undock())
                continue

            entities_by_distance = game_map.nearby_enemies_and_planets_by_distance(
                ship)

            for entity in entities_by_distance:
                current_time = time.time()
                if current_time - turn_start > hlt.constants.MAX_TURN_LENGTH:
                    logging.info("Turn time exceeded")
                    break
                if isinstance(entity, hlt.entity.Planet):
                    logging.info("Planet detected")
                    planet = entity
                    planet_enemy_radius = ship.calculate_distance_between(
                        planet)
                    if ships_going_to_planet[planet.id] < planet.num_docking_spots + len(hlt.calculations.get_enemy_ships_in_radius(game_map, planet, planet_enemy_radius)) + 2:
                        # planet has owner
                        if planet.is_owned():
                            # planet belongs to me and is not full
                            if planet.all_docked_ships()[0].owner == game_map.get_me() and not planet.is_full():
                                if ship.can_dock(planet):
                                    command_queue.append(ship.dock(planet))
                                    ships_going_to_planet[planet.id] += 1
                                    break
                                else:
                                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(
                                        hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
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
                                enemy_ships_at_planet_sorted_distance = [[e_ship, ship.calculate_distance_between(
                                    e_ship)] for e_ship in planet.all_docked_ships()]
                                enemy_ships_at_planet_sorted_distance.sort(
                                    key=lambda x: x[1])

                                ship_to_enemy_distance = enemy_ships_at_planet_sorted_distance[0][1]
                                if ship_to_enemy_distance < 6:
                                    continue
                                else:
                                    ship_speed = int(hlt.constants.MAX_SPEED)
                                    if ship_to_enemy_distance <= 12:
                                        ship_speed = int(
                                            ship_to_enemy_distance - 5)

                                    [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(
                                        enemy_ships_at_planet_sorted_distance[0][0]), game_map, speed=ship_speed, new_ship_positions=new_ship_positions)
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
                                break
                            else:
                                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet), game_map, speed=int(
                                    hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
                                new_ship_positions.append((x, y))
                                if navigate_command:
                                    command_queue.append(navigate_command)
                                    ships_going_to_planet[planet.id] += 1
                                    break
                                break

                else:
                    logging.info("Enemy detected")
                    enemy_ship = entity

                    current_time = time.time()
                    if current_time - turn_start > hlt.constants.MAX_TURN_LENGTH:
                        logging.info("Turn time exceeded")
                        break

                    if not ((len(planets) > 0 and planets_owned < len(planets)) or len(enemy_planets) == 0):
                        if ships_following_enemy[enemy_ship.id] >= 3:
                            logging.info("skip, enemy_follow_count: " +
                                         str(ships_following_enemy[enemy_ship.id]))
                            continue

                    else:
                        logging.info("following enemy")
                        ships_following_enemy[enemy_ship.id] += 1

                    own_distance = ship.calculate_distance_between(enemy_ship)

                    if own_distance == hlt.constants.WEAPON_RADIUS:
                        continue

                    elif own_distance < hlt.constants.WEAPON_RADIUS:
                        enemy_x = enemy_ship.x
                        enemy_y = enemy_ship.y
                        own_x = ship.x
                        own_y = ship.y
                        angle = math.atan2(enemy_y - own_y, enemy_x - own_x)
                        x = own_x + \
                            math.cos(angle) * \
                            (hlt.constants.WEAPON_RADIUS - own_distance)
                        y = own_y + \
                            math.sin(angle) * \
                            (hlt.constants.WEAPON_RADIUS - own_distance)
                        target_position = hlt.entity.Position(x, y)
                        [navigate_command, (x, y)] = ship.navigate(target_position, game_map, speed=int(
                            hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
                        new_ship_positions.append((x, y))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break

                    else:
                        ship_speed = int(hlt.constants.MAX_SPEED)

                        if own_distance <= 12:
                            ship_speed = int(own_distance - 5)

                        [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(
                            enemy_ship), game_map, speed=ship_speed, new_ship_positions=new_ship_positions)
                        new_ship_positions.append((x, y))
                        logging.info("navigate_command: " +
                                     str(navigate_command))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            logging.info("nav success")
                            break
                        break

    game.send_command_queue(command_queue)
