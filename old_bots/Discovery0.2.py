"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.

Docs:
https://2017.forums.halite.io/c/documentation.html
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hltDiscovery
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hltDiscovery.Game("Discovery 0.2")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # For each planet in the game (only non-destroyed planets are included)
        
        planet_distance_list = [[planet, ship.calculate_distance_between(planet)] for planet in game_map.all_planets()]
        planet_distance_list.sort(key=lambda x: x[1])

        for planet in planet_distance_list:
            if planet[0].is_owned():
                continue
            else:
                if ship.can_dock(planet[0]):
                    # logging.info("Docking ship: ", str(ship.id), " to planet: ", str(planet[0].id))
                    command_queue.append(ship.dock(planet[0]))
                    break
                else:
                    navigate_command = ship.navigate(ship.closest_point_to(planet[0]), game_map, speed=int(hltDiscovery.constants.MAX_SPEED))
                    if navigate_command:
                        command_queue.append(navigate_command)
                        break
                    break
        

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
