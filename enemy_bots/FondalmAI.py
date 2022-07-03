import hlt
import logging
import random as rnd
import math

'''
Bot by FondalmAI: 
    Jonny Schlutter     220200194
    Dennis Kelm         220200295
    Ole Adelmann        220200054 
    Gia Huy Hans Tran   220200285
    Bastian Reichert    220200414

This bot does not need any additional files to run. 
Simply specify one of the competung bots in run_game.bat as "python FondalmAI.py".

Strategy:
-if the bot has less than 10 ships: try to claim more planets
    -> the bot assigns ships to nearby planets that arent owned by an enemy, still have rescources and dont have too many ships assigned to it
    -> each planet can have as many ships assigned to it as it has docking spots (2-5).
    -> if the planet is sucked dry, the ships undock
-else if the bot has between 10 and 20 ships: only try to claim more planets if enemies are far away
-else if the bot has more than 20 ships: only a portion of the ships try to claim safe nearby planets
-else: every undocked ship navigates to their closest enemy ship and destroys it
'''

game = hlt.Game("FondalmAI")
logging.info("Starting my FondalmAI bot!")


# +-----+ Ship Methods +-----+

# returns a suitable planet that is nearest to the ship
# extension of the function found on Halites "Improve your Basic Bot" page
def nearest_planet(ship):
    values = {}
    entities_by_distance = game_map.nearby_entities_by_distance(ship)

    for distance in sorted(entities_by_distance):
        planet = next((nearest_entity for nearest_entity in entities_by_distance[distance] if
                       isinstance(nearest_entity, hlt.entity.Planet)), None)
        # make sure the planet exists, can be docked to and still has rescources
        # also make sure the planet doesnt have too many ships assigned to it
        if planet and (not planet.is_owned() or planet.owner == me) \
                and not planet.is_full() and planet.remaining_resources > 0 \
                and (planet not in assigned_ships_of_planet \
                or len(assigned_ships_of_planet[planet]) < planet.num_docking_spots):
            values[planet] = evaluate_planet(ship,planet)

    return max(values, default=None, key=values.get)


# returns a value based on how useful the planet is
def evaluate_planet(ship,planet):

    # --- heuristic function ---
    # planets base value is defined by its distance
    # value is increased based on its docking spots and the docking spots of its neighbors
    value = 1000 - ship.calculate_distance_between(planet)
    value += planet.num_docking_spots * 3
    distance_from_other_planets = game_map.nearby_entities_by_distance(planet)

    for distance2 in sorted(distance_from_other_planets):
        other_planet = next((nearest_entity for nearest_entity in distance_from_other_planets[distance2] if
                             isinstance(nearest_entity, hlt.entity.Planet)), None)
        if other_planet and (not other_planet.is_owned() or other_planet.owner == me) \
                and not other_planet.is_full() and other_planet.remaining_resources > 0 \
                and planet.calculate_distance_between(other_planet) < 40.0:
            distance_between_planets = planet.calculate_distance_between(other_planet)    
            value += other_planet.num_docking_spots * 400/(distance_between_planets*distance_between_planets)
    return value


# returns an enemy ship that is nearest to the ship
def nearest_enemy(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        next_enemy = next((nearest_entity for nearest_entity in entities_by_distance[distance]), None)
        if isinstance(next_enemy, hlt.entity.Ship) and next_enemy.owner != me:
            return next_enemy


# returns a friendly ship that is nearest to the ship
def nearest_ally(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        next_ship = next((nearest_entity for nearest_entity in entities_by_distance[distance]), None)
        if isinstance(next_ship, hlt.entity.Ship) and next_ship.owner == me:
            return next_ship


# returns a command, making the ship navigate to the target
# with collision detection
def generate_navigate_command(ship, target):
    return ship.navigate(ship.closest_point_to(target), game_map, 7)


# evaluates a planet and returns true/false whether the ship should navigate to it
def worth_it(ship, target):
    my_ships = len(me.all_ships())
    distance_to_target = ship.calculate_distance_between(target)

    if my_ships < 10: return True
    if role_of_ship[ship] == "battler" and my_ships < 20 and distance_to_target < 100: return True
    if role_of_ship[ship] == "settler" and distance_to_target < 200: return True
    return False


# returns true/false wether the planet can be safely navigated to without enemy presence
def planet_is_safe(ship, target):
    enemy = nearest_enemy(ship)
    distance_to_target = ship.calculate_distance_between(target)
    distance_to_enemy = ship.calculate_distance_between(enemy)
    distance_from_target_to_enemy = target.calculate_distance_between(enemy)
    tolerance = 64 if role_of_ship[ship] == "battler" else 32

    if distance_to_target * 1.8 + 10 < distance_to_enemy:  # check if enemy is very far away
        return True
    elif distance_to_target + 5 < distance_to_enemy * distance_to_enemy / tolerance:  # check if enemy is not too close
        # check if enemy is behind ship, when facing target
        angles = [ship.calculate_angle_between(enemy), ship.calculate_angle_between(target)]
        angle_difference = max(angles) - min(angles)
        return 90 < angle_difference < 270
    return False


# +-----+ A* Navigator +-----+
'''
We were thinking about implementing the A* algorithm but after thorough consideration 
we decided to skip it in favour of a more primitive approach as to reduce the complexity of the 
code and the effort we have to put in
'''

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


# goal: find the path ( between "starting" vertex and "goal" vertex ) with the least overall value
# given a cartisian coordinate System as the playing field
# each point on the MxN grid is considered a Vertex
# each neighbouring point ( the instance between the points 1 or sqrt(2)
# both of which are connected by an edge

# overall values are calculated as followed: heuristic value + path length
# enemy entities have a heuristic value of 1 (arbitrary value)
# path length is the euclidiean distance between the "starting" vertex and "goal" vertex

# idea: instead of using the whole map, only use the rectangle area of the ship and the target
# A*: shortest path with as less collisions with other ships

def a_star_navigator(ship, target):
    Q = PriorityQueue()
    came_from = {}
    Q.put((ship.x, ship.y), 0)
    came_from[ship] = None

    while not Q.empty():
        current = Q.get()
        if current == target:
            break
        for next in None:
            if next not in came_from:
                Q.put(next, ship.calculate_distance_between(target))  # wie ist die Priority?
                came_from[next] = current
    return None  # ???(came_from, ship, target)


# +-----+ Main Loop +-----+

turn_count = 0
role_of_ship = {}  # keeps track of the role of each ship (battler or settler)
assigned_ships_of_planet = {}  # keeps track of wich planets have wich ships assigned to them

while True:
    turn_count += 1
    game_map = game.update_map()
    me = game_map.get_me()
    command_queue = []
    # my_planets = [p for p in game_map.all_planets() if p.owner == me]

    # -----assign ship types-----
    # randomly assign a role (Settler or Battler) to each ship, to later determine its behaviour
    # a ratio of 0.2 results in 20% Settlers, 80% Battlers
    role_ratio = 0.2
    for ship in set(me.all_ships()) - set(role_of_ship):
        role_of_ship[ship] = "settler" if rnd.random() < role_ratio else "battler"

    # -----update the assigned planets-----
    # if a ship assigned to a planet is dead, it is removed from the set
    # if a planet is sucked dry, its entry is removed
    for planet in assigned_ships_of_planet:
        assigned_ships_of_planet[planet] = {s for s in assigned_ships_of_planet[planet] if s.health != 0}
        if planet.remaining_resources == 0: assigned_ships_of_planet.pop(planet)

    for ship in me.all_ships():
        
        # super amazing fix for turn 1 crashes :D
        if turn_count == 1 and (ship.id == 0 or ship.id == 3):
            angle = 180 if ship.id == 0 else 0
            command_queue.append(ship.thrust(7, angle))
            continue

        # if already docked to a planet: undock if its empty, else skip
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            if ship.docking_status == ship.DockingStatus.DOCKED and ship.planet.remaining_resources == 0:
                command_queue.append(ship.undock())
            continue

        # (First Settle!) if a suitable planet exists and the bot still doesnt have enough ships: colonize it!
        # (Then  Battle!) else: attack the nearest enemy!
        target = nearest_planet(ship)
        if target and planet_is_safe(ship, target) and worth_it(ship, target):
            # add the ship to the assigned ships of the planet
            if target not in assigned_ships_of_planet:
                assigned_ships_of_planet[target] = {ship}
            else:
                assigned_ships_of_planet[target].add(ship)

            # dock if possible
            if ship.can_dock(target):
                command_queue.append(ship.dock(target))
                continue
        else:
            target = nearest_enemy(ship)

        # navigate to target and add it to command list
        navigate_command = generate_navigate_command(ship, target)
        if navigate_command:
            command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
