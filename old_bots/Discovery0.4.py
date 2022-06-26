import hltDiscovery
import logging

game = hltDiscovery.Game("Discovery 0.4")
logging.info("Starting my Discovery!")

while True:
    game_map = game.update_map()

    planets = [planet for planet in game_map.all_planets()]

    planets_owned = 0
    for planet in planets:
        if planet.is_owned():
            planets_owned += 1
            continue

    command_queue = []
    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        planet_distance_list = [[planet, ship.calculate_distance_between(planet)] for planet in planets]
        planet_distance_list.sort(key=lambda x: x[1])
        

        for planet in planet_distance_list:
            if planet[0].is_owned():
                #if planet[0].all_docked_ships()[0].owner == game_map.get_me() and planets[0].is_full():
                 #    continue
                if planet[0].all_docked_ships()[0].owner == game_map.get_me() and not planet[0].is_full():
                    if ship.can_dock(planet[0]):
                        command_queue.append(ship.dock(planet[0]))
                        break
                    else:
                        navigate_command = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(hltDiscovery.constants.MAX_SPEED))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break
                elif planet[0].all_docked_ships()[0].owner == game_map.get_me() and planet[0].is_full():
                    continue
                elif planet[0].all_docked_ships()[0].owner != game_map.get_me(): 
                    enemy_ships_at_planet_sorted_distance = [[e_ship, ship.calculate_distance_between(e_ship)] for e_ship in planet[0].all_docked_ships()]
                    enemy_ships_at_planet_sorted_distance.sort(key=lambda x: x[1])

                    ship_to_enemy_distance = ship.calculate_distance_between(enemy_ships_at_planet_sorted_distance[0][0])
                    if ship_to_enemy_distance < 6:
                        continue
                    else:
                        ship_speed = int(hltDiscovery.constants.MAX_SPEED)
                        if ship_to_enemy_distance <= 12:
                            ship_speed = int(ship_to_enemy_distance - 5)

                        navigate_command = ship.navigate(ship.closest_point_to(enemy_ships_at_planet_sorted_distance[0][0]), game_map, speed=ship_speed)
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break
                else:
                    if ship.can_dock(planet[0]):
                        command_queue.append(ship.dock(planet[0]))
                        break
                    else:
                        navigate_command = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(hltDiscovery.constants.MAX_SPEED))
                        if navigate_command:
                            command_queue.append(navigate_command)
                            break
                        break
            else:
                if ship.can_dock(planet[0]):
                    command_queue.append(ship.dock(planet[0]))
                    break
                else:
                    navigate_command = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(hltDiscovery.constants.MAX_SPEED))
                    if navigate_command:
                        command_queue.append(navigate_command)
                        break
                    break
        
        
    game.send_command_queue(command_queue)
