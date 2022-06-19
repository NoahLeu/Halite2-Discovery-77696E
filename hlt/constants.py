#: Max number of units of distance a ship can travel in a turn
MAX_SPEED = 7
#: Radius of a ship
SHIP_RADIUS = 0.5
#: Starting health of ship, also its max
MAX_SHIP_HEALTH = 255
#: Starting health of ship, also its max
BASE_SHIP_HEALTH = 255
#: Weapon cooldown period
WEAPON_COOLDOWN = 1
#: Weapon damage radius
WEAPON_RADIUS = 5.0
#: Weapon damage
WEAPON_DAMAGE = 64
#: Radius in which explosions affect other entities
EXPLOSION_RADIUS = 10.0
#: Distance from the edge of the planet at which ships can try to dock
DOCK_RADIUS = 4.0
#: Number of turns it takes to dock a ship
DOCK_TURNS = 5
#: Number of production units per turn contributed by each docked ship
BASE_PRODUCTIVITY = 6
#: Distance from the planets edge at which new ships are created
SPAWN_RADIUS = 2.0


# CUSTOM CONSTANTS

MAX_TURN_LENGTH = 1.7

RUSH_MAP_SIZE_MAX = 20
RUSH_MAX_TURNS = 30
RUSH_MAX_RANGE = MAX_SPEED * RUSH_MAX_TURNS

EARLY_GAME_MAX_SHIPS = 5
EARLY_GAME_SAFE_DISTANCE = 1000* MAX_SPEED * DOCK_TURNS * WEAPON_RADIUS + DOCK_RADIUS
EARLY_GAME_MAX_TURNS = 40

# early game big and small map differences
# for travelling to planet: if amount travelling more than docking spots + enemies in radius + X then choose next planet