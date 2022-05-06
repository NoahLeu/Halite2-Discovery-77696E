from asyncio.log import logger
import numpy as np

def navigate_astar(self, target, game_map, speed): 
    # make grid as a numpy array
    hitmap = np.zeros((game_map.height, game_map.width))

    for planet in game_map.all_planets():
        # hitmap True for every cell in planet circle
        for x in range(planet.x - planet.radius, planet.x + planet.radius):
            for y in range(planet.y - planet.radius, planet.y + planet.radius):
                if (x - planet.x)**2 + (y - planet.y)**2 < planet.radius**2:
                    hitmap[x][y] = 1

    for ship in game_map.all_ships():
        hitmap[ship.x][ship.y] = 1

    # convert hitmap into a numpy array
    hitmap = np.array(hitmap)


    ####################################################################################################################################



    # GOAL: find the shortest path from ship to target using A* and avoiding planets and other ships
    # start at ship
    start = (self.x, self.y)
    # end at target
    end = (target.x, target.y)
    # create a grid of the same size as the map
    grid = np.zeros((game_map.height, game_map.width))
    # set the start and end points to 1
    grid[start] = 1
    grid[end] = 1
    # set the hitmap to 0
    grid[hitmap == 1] = 0
    # set the ship to 0
    grid[self.x][self.y] = 0
    # set the target to 0
    grid[target.x][target.y] = 0
    # set the planets to 0
    for planet in game_map.all_planets():
        grid[planet.x][planet.y] = 0
    # set the other ships to 0
    for ship in game_map.all_ships():
        if ship != self:
            grid[ship.x][ship.y] = 0
    # set the obstacles to 0
    for obstacle in game_map.all_planets() + game_map.all_ships():
        grid[obstacle.x][obstacle.y] = 0
    # set the empty cells to 1
    grid[grid == 0] = 1
    # set the start and end points to 0
    grid[start] = 0
    grid[end] = 0
    # set the hitmap to 1
    grid[hitmap == 1] = 1
    # set the ship to 1
    grid[self.x][self.y] = 1
    # set the target to 1
    grid[target.x][target.y] = 1
    # set the planets to 1
    for planet in game_map.all_planets():
        grid[planet.x][planet.y] = 1
    # set the other ships to 1
    for ship in game_map.all_ships():
        if ship != self:
            grid[ship.x][ship.y] = 1
    # set the obstacles to 1
    for obstacle in game_map.all_planets() + game_map.all_ships():
        grid[obstacle.x][obstacle.y] = 1
    # set the empty cells to 0
    grid[grid == 1] = 0
    # set the start and end points to 1
    grid[start] = 1
    grid[end] = 1
    # set the hitmap to 0
    grid[hitmap == 1] = 0

            

