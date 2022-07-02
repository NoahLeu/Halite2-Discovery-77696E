import hltDiscovery as hlt
import logging

game = hlt.Game("Discovery 0.7 E OLD")
logging.info("Starting my Discovery!")


turn = -1

planets_first_turn = []

while True:
    # focus on getting first planet
    EARLY_GAME = True
    # rush to enemy and destroy fast
    RUSH_MODE = False
    # focus on expanding and destroying enemies
    MID_GAME = False
    # focus on attacking enemy ships (active if no ressources left or if all not empty planets are owned)
    LATE_GAME = False

    # Do not exceed MAX_TURN_LENGTH
    # startOfTurn = time.time()

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
        logging.info("RUSH MODE ACTIVATED")

    my_free_ships = game_map.get_me().free_ships()
    my_docked_ships = game_map.get_me().docked_ships()
    my_docking_ships = game_map.get_me().docking_ships()
    my_undocking_ships = game_map.get_me().undocking_ships()

    my_ship_count = len(game_map.get_me().all_ships())

    enemy_ships = game_map.all_enemy_ships()
    enemy_planets = game_map.all_enemy_planets()

    min_enemy_distance = 9999999

    ships_going_to_planet = {}
    for planet in planets:
        ships_going_to_planet[planet.id] = 0

    if EARLY_GAME and (turn > hlt.constants.EARLY_GAME_MAX_TURNS or
                       my_ship_count > hlt.constants.EARLY_GAME_MAX_SHIPS):
        EARLY_GAME = False
        MID_GAME = True
        LATE_GAME = False

    # ! EXPERIMENTAL for early game
    RUSH_MODE = False

    logging.info("planet amount: " + str(len(planets)))

    if len(planets) == 0 or planets_owned == len(planets):
        RUSH_MODE = False
        EARLY_GAME = False
        MID_GAME = False
        LATE_GAME = True

    logging.info("Current mode: EARLY_GAME = {}, RUSH_MODE = {}, MID_GAME = {}, LATE_GAME = {}".format(
        EARLY_GAME, RUSH_MODE, MID_GAME, LATE_GAME))

    # ! experimental
    #RUSH_MODE = False
    #EARLY_GAME = False
    #MID_GAME = True
    #LATE_GAME = False

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
                # if turn == 0 and planet in planets_first_turn:
                #    continue

                # planet has owner
                if planet[0].is_owned():
                    # planet belongs to me and is not full
                    if planet[0].all_docked_ships()[0].owner == game_map.get_me() and not planet[0].is_full() and not planet[0].remaining_resources == 0:
                        if ship.can_dock(planet[0]):
                            command_queue.append(ship.dock(planet[0]))
                            planets_first_turn.append(planet[0])
                            break
                        else:
                            [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(
                                hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
                            new_ship_positions.append((x, y))
                            if navigate_command:
                                command_queue.append(navigate_command)
                                planets_first_turn.append(planet[0])
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
                                planets_first_turn.append(planet[0])
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
                            planets_first_turn.append(planet[0])
                            command_queue.append(navigate_command)
                            break
                        break

    elif MID_GAME:
        logging.info("MID GAME")
        for ship in game_map.get_me().all_ships():
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                if ship.planet.remaining_resources == 0:
                    command_queue.append(ship.undock())
                continue

            planet_distance_list = [
                [planet, ship.calculate_distance_between(planet)] for planet in planets]
            planet_distance_list.sort(key=lambda x: x[1])

            for planet in planet_distance_list:
                planet_enemy_radius = ship.calculate_distance_between(
                    planet[0])
                if ships_going_to_planet[planet[0].id] < planet[0].num_docking_spots + len(hlt.calculations.get_enemy_ships_in_radius(game_map, planet[0], planet_enemy_radius)) + 2:
                    # planet has owner
                    if planet[0].is_owned():
                        # planet belongs to me and is not full
                        if planet[0].all_docked_ships()[0].owner == game_map.get_me() and not planet[0].is_full():
                            if ship.can_dock(planet[0]):
                                command_queue.append(ship.dock(planet[0]))
                                ships_going_to_planet[planet[0].id] += 1
                                break
                            else:
                                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(
                                    hlt.constants.MAX_SPEED), new_ship_positions=new_ship_positions)
                                new_ship_positions.append((x, y))
                                if navigate_command:
                                    command_queue.append(navigate_command)
                                    ships_going_to_planet[planet[0].id] += 1
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
                                    ship_speed = int(
                                        ship_to_enemy_distance - 5)

                                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(
                                    enemy_ships_at_planet_sorted_distance[0][0]), game_map, speed=ship_speed, new_ship_positions=new_ship_positions)
                                new_ship_positions.append((x, y))
                                if navigate_command:
                                    command_queue.append(navigate_command)
                                    ships_going_to_planet[planet[0].id] += 1
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
                                ships_going_to_planet[planet[0].id] += 1
                                break
                            break

    elif LATE_GAME:
        logging.info("LATE GAME")

        for ship in game_map.get_me().all_ships():
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                if ship.planet.remaining_resources == 0:
                    command_queue.append(ship.undock())
                continue

            for enemy_ship in game_map.all_enemy_ships():
                enemy_ships_by_distance = [
                    [e_ship, ship.calculate_distance_between(e_ship)] for e_ship in enemy_ships]
                enemy_ships_by_distance.sort(key=lambda x: x[1])

            for enemy in enemy_ships_by_distance:
                enemy_ship = enemy[0]
                own_distance = enemy[1]

                if own_distance <= 5:
                    continue

                ship_speed = int(hlt.constants.MAX_SPEED)

                if own_distance <= 12:
                    ship_speed = int(own_distance - 5)

                [navigate_command, (x, y)] = ship.navigate(ship.closest_point_to(
                    enemy_ship), game_map, speed=ship_speed, new_ship_positions=new_ship_positions)
                new_ship_positions.append((x, y))
                if navigate_command:
                    command_queue.append(navigate_command)
                    break

    game.send_command_queue(command_queue)
