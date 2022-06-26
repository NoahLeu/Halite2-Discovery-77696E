
import hltDiscovery
import logging
import random as rnd

game = hltDiscovery.Game("Settle then Battle v2")
logging.info("Starting my FondalmJ bot!")

'''
Strategy:
-if the bot has less than 10 ships: try to claim more planets
    -> the bot assigns ships to nearby planets that arent owned by an enemy, still have rescources and dont have too many ships assigned to it
    -> each planet can have as many ships assigned to it as it has docking spots (2-5).
    -> if the planet is sucked dry, the ships undock
-else: every undocked ship navigates to their closest enemy ship and destroys it
'''

#returns a suitable planet that is nearest to the ship
def nearest_planet(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        planet = next((nearest_entity for nearest_entity in entities_by_distance[distance] if isinstance(nearest_entity, hltDiscovery.entity.Planet)), None)
        #make sure the planet exists, can be docked to and still has rescources
        if planet and (not planet.is_owned() or planet.owner == me) and not planet.is_full() and planet.remaining_resources > 0:
            #make sure the planet doesnt have too many ships assigned to it
            if planet not in assigned_ships_of_planet or len(assigned_ships_of_planet[planet]) < planet.num_docking_spots:
                return planet

#returns an enemy ship that is nearest to the ship
def nearest_enemy(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        next_enemy = next((nearest_entity for nearest_entity in entities_by_distance[distance]), None)
        if isinstance(next_enemy, hltDiscovery.entity.Ship) and next_enemy.owner != me:
            return next_enemy

#returns a command, making the ship navigate to the target
def generate_navigate_command(ship, target):
    return ship.navigate(ship.closest_point_to(target), game_map, speed=int(hltDiscovery.constants.MAX_SPEED))

while True:
    game_map = game.update_map()
    me = game_map.get_me()
    command_queue = []
    assigned_ships_of_planet = {} #this keeps track of wich planets have wich ships assigned to them
    #my_planets = [p for p in game_map.all_planets() if p.owner == me]

    #update the assigned planets
    #if a ship assigned to a planet is dead, it is removed from the set
    #if a planet is sucked dry, its entry is removed
    for planet in assigned_ships_of_planet:
        assigned_ships_of_planet[planet] = {s for s in assigned_ships_of_planet[planet] if s.health != 0}
        if planet.remaining_resources == 0: assigned_ships_of_planet.pop(planet)    


    for ship in me.all_ships():
        #if already docked to a planet: undock if its empty, else skip
        if ship.docking_status != ship.DockingStatus.UNDOCKED: 
            if ship.docking_status == ship.DockingStatus.DOCKED and ship.planet.remaining_resources == 0:
                command_queue.append(ship.undock())
            continue
        
        #(First Settle!) if a suitable planet exists and the bot still doesnt have enough ships: colonize it!
        #(Then  Battle!) else: attack the nearest enemy!
        target = nearest_planet(ship)
        if target and len(me.all_ships()) < 10:# or ship.calculate_distance_between(target)*2 < ship.calculate_distance_between(nearest_enemy(ship)):
            #add the ship to the assigned ships of the planet
            if target not in assigned_ships_of_planet:
                assigned_ships_of_planet[target] = {ship}
            else: assigned_ships_of_planet[target].add(ship)

            #dock if possible
            if ship.can_dock(target):
                command_queue.append(ship.dock(target))
                continue
        else: target = nearest_enemy(ship)

        #navigate to target and add it to command list
        navigate_command = generate_navigate_command(ship, target)
        if navigate_command:
            command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
