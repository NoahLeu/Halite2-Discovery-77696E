import numpy as np
from queue import PriorityQueue
import heapq

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

# https://www.analytics-link.com/post/2018/09/14/applying-the-a-path-finding-algorithm-in-python-part-1-2d-square-grid 
def astar(np_grid, start, goal):
    # allow ship to move diagonally
    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    # setup the search
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}

    oheap = []
    heapq.heappush(oheap, (fscore[start], start))
    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < np_grid.shape[0]:
                if 0 <= neighbor[1] < np_grid.shape[1]:                
                    if np_grid[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))


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

    ##############################################################################


            

