from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# ---------------------------
# Global Game State
# ---------------------------
WINDOW_W, WINDOW_H = 800, 600

# Game levels
LEVEL_1, LEVEL_2, LEVEL_3 = 1, 2, 3
current_level = LEVEL_1
game_over = False
win = False
level_1_completed = False
level_2_completed = False

# ---------------------------
# Level 1 (Rolling Stones)
# ---------------------------
player_1 = {"x": 0.0, "y": 0.5, "z": 5.0}
score_1 = 0
stones = []
STONE_SPEED = 0.05
STONE_SPAWN_INTERVAL = 0.5
last_spawn_time = 0
GOAL_Z_1 = -50.0

# Level 1 Countdown Timer
countdown_timer_1 = 60.0
last_update_time_1 = time.time()


# ---------------------------
# Level 2 (3D Maze)
# ---------------------------
player_2 = {"x": 0.0, "z": 0.0}
score_2 = 0
b_key_pressed = False
countdown_timer_2 = 60.0
last_update_time_2 = time.time()

maze = [
    [1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1],
]
ROWS, COLS = len(maze), len(maze[0])
TILE_SIZE = 2.0
WALL_HEIGHT = 2.0
isometric_angle_2 = 45
isometric_elevation_2 = 35
camera_distance_2 = 20.0
rewards = []
bombs = []
MAX_REWARDS = 5
MAX_BOMBS = 3


# ---------------------------
# Level 3 (Dragon Slayer)
# ---------------------------
player_3 = {"x": 0.0, "z": 0.0}
score_3 = 0
fireball_hits = 0
MAX_FIREBALL_HITS = 10
ENV_SIZE = 30.0

DRAGON_COUNT = 5
dragons = []
fireballs = []
player_projectiles = []
LAST_FIRE_TIME = 0.0
FIRE_INTERVAL = 1.0

# Isometric view settings for Level 3
isometric_angle_3 = 45
isometric_elevation_3 = 30
camera_distance_3 = 40.0

# ---------------------------
# Drawing Utilities
# ---------------------------
def draw_text(text, x, y):
    """Draws text on the screen at specified coordinates."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)
    glWindowPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ---------------------------
# Level 1 Drawing & Logic
# ---------------------------
def draw_ground_1():
    """Draws a grid for the ground."""
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, -30)
    glVertex3f(30, 0, -30)
    glVertex3f(30, 0, 30)
    glVertex3f(-30, 0, 30)
    glEnd()

    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-15, 16, 2):
        glVertex3f(i, 0.01, -30)
        glVertex3f(i, 0.01, 30)
        glVertex3f(-30, 0.01, i)
        glVertex3f(30, 0.01, i)
    glEnd()

    # Draw the finish line
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3f(-30, 0.02, GOAL_Z_1)
    glVertex3f(30, 0.02, GOAL_Z_1)
    glEnd()
    glLineWidth(1.0)

def draw_player_1():
    """Draws the player as a colored cube."""
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(player_1["x"], 0.5, player_1["z"])
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_stones():
    """Draws the rolling stones as solid spheres with different colors."""
    for stone in stones:
        if stone["type"] == "yellow":
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(stone["x"], 0.5, stone["z"])
        glutSolidSphere(0.8, 16, 16)
        glPopMatrix()

def update_game_state_1():
    """Updates the position of all stones and handles spawning and scoring."""
    global game_over, score_1, last_spawn_time, level_1_completed
    global countdown_timer_1, last_update_time_1
    global stones

    if not game_over and not level_1_completed:
        # Update timer
        current_time = time.time()
        delta_time = current_time - last_update_time_1
        last_update_time_1 = current_time
        countdown_timer_1 -= delta_time

        if countdown_timer_1 <= 0:
            game_over = True
            win = False
            return

        # Check for win condition and set a flag
        if player_1["z"] <= GOAL_Z_1:
            level_1_completed = True
            return

        # Move stones towards the player
        for stone in stones:
            stone["z"] += STONE_SPEED

        # Remove stones that have passed the player
        stones = [stone for stone in stones if stone["z"] < player_1["z"] + 10]

        # Spawn new stones
        if current_time - last_spawn_time > STONE_SPAWN_INTERVAL:
            spawn_stone()
            last_spawn_time = current_time

        check_collision_1()

    glutPostRedisplay()

def spawn_stone():
    """Spawns a new stone at the far end of the environment, with a chance to be yellow."""
    x = random.uniform(-30 / 2 + 2, 30 / 2 - 2)
    z = -30 / 2 - 10.0
    stone_type = "yellow" if random.random() < 0.2 else "gray"
    stones.append({"x": x, "z": z, "type": stone_type})

def check_collision_1():
    """Checks for collisions between the player and any stone and updates score based on stone color."""
    global score_1
    player_radius = 0.5
    stone_radius = 0.8

    for stone in stones:
        distance = math.sqrt((player_1["x"] - stone["x"])**2 + (player_1["z"] - stone["z"])**2)
        if distance < player_radius + stone_radius:
            if stone["type"] == "yellow":
                score_1 += 1
            else:
                score_1 -= 1
            stones.remove(stone)

def set_third_person_camera_1():
    """Sets the camera to a third-person perspective behind the player."""
    gluLookAt(player_1["x"],
              player_1["y"] + 5,
              player_1["z"] + 10,
              player_1["x"],
              player_1["y"],
              player_1["z"],
              0, 1, 0)

# ---------------------------
# Level 2 Drawing & Logic
# ---------------------------

def draw_ground_2():
    glColor3f(0.2, 0.9, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, -30)
    glVertex3f(30, 0, -30)
    glVertex3f(30, 0, 30)
    glVertex3f(-30, 0, 30)
    glEnd()

    glColor3f(0.4, 0.6, 0.4)
    glBegin(GL_LINES)
    for i in range(-15, 16, 2):
        glVertex3f(i, 0.01, -30)
        glVertex3f(i, 0.01, 30)
        glVertex3f(-30, 0.01, i)
        glVertex3f(30, 0.01, i)
    glEnd()

def draw_walls():
    for i in range(ROWS):
        for j in range(COLS):
            if maze[i][j] == 1:
                x = (i - ROWS//2) * TILE_SIZE
                z = (j - COLS//2) * TILE_SIZE
                draw_wall(x, z)

def draw_wall(x, z):
    glColor3f(0.5, 0.5, 0.7)
    glPushMatrix()
    glTranslatef(x, WALL_HEIGHT/2, z)
    glScalef(TILE_SIZE, WALL_HEIGHT, TILE_SIZE)
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(-0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, 0.5); glVertex3f(0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
    # Back face
    glVertex3f(-0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, -0.5); glVertex3f(0.5, 0.5, -0.5); glVertex3f(-0.5, 0.5, -0.5)
    # Top face
    glColor3f(0.6, 0.2, 0.1)
    glVertex3f(-0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
    # Bottom face
    glVertex3f(-0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, 0.5); glVertex3f(-0.5, -0.5, 0.5)
    # Right face
    glVertex3f(0.5, -0.5, -0.5); glVertex3f(0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, 0.5); glVertex3f(0.5, -0.5, 0.5)
    # Left face
    glVertex3f(-0.5, -0.5, -0.5); glVertex3f(-0.5, 0.5, -0.5); glVertex3f(-0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
    glEnd()
    glPopMatrix()

def draw_items():
    for rx, rz in rewards:
        glColor3f(1.0, 1.0, 0.0)
        glPushMatrix()
        glTranslatef(rx, 0.5, rz)
        glutSolidSphere(0.3, 16, 16)
        glPopMatrix()

    for bx, bz in bombs:
        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(bx, 0.5, bz)
        glutSolidSphere(0.3, 16, 16)
        glPopMatrix()

def draw_player_2():
    glColor3f(0.0, 0.0, 1.0)
    glPushMatrix()
    glTranslatef(player_2["x"], 0.5, player_2["z"])
    glutSolidSphere(0.3, 16, 16)
    glPopMatrix()

def set_isometric_camera_2():
    angle_rad = math.radians(isometric_angle_2)
    elevation_rad = math.radians(isometric_elevation_2)

    center_x = 0
    center_z = 0

    cam_x = center_x + camera_distance_2 * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = camera_distance_2 * math.sin(elevation_rad)
    cam_z = center_z + camera_distance_2 * math.sin(angle_rad) * math.cos(elevation_rad)

    gluLookAt(cam_x, cam_y, cam_z,
              center_x, 0, center_z,
              0, 1, 0)

def find_valid_start():
    for i in range(ROWS):
        for j in range(COLS):
            if maze[i][j] == 0:
                x = (i - ROWS//2) * TILE_SIZE
                z = (j - COLS//2) * TILE_SIZE
                return x, z
    return 0, 0

def spawn_items():
    global rewards, bombs
    empty_spaces = []
    for i in range(ROWS):
        for j in range(COLS):
            if maze[i][j] == 0:
                x = (i - ROWS//2) * TILE_SIZE
                z = (j - COLS//2) * TILE_SIZE
                empty_spaces.append((x, z))

    random.shuffle(empty_spaces)

    rewards = []
    for i in range(min(MAX_REWARDS, len(empty_spaces))):
        rewards.append(empty_spaces.pop())

    bombs = []
    for i in range(min(MAX_BOMBS, len(empty_spaces))):
        bombs.append(empty_spaces.pop())

def check_collision_2(x, z):
    i = int(round((x + (ROWS//2)*TILE_SIZE) / TILE_SIZE))
    j = int(round((z + (COLS//2)*TILE_SIZE) / TILE_SIZE))

    if i < 0 or i >= ROWS or j < 0 or j >= COLS:
        return True

    return maze[i][j] == 1

def check_item_collision():
    global score_2, rewards, bombs
    player_pos = (player_2["x"], player_2["z"])

    new_rewards = []
    for rx, rz in rewards:
        dist_sq = (player_pos[0] - rx)**2 + (player_pos[1] - rz)**2
        if dist_sq < 0.5**2:
            score_2 += 1
            spawn_items()
            return
        else:
            new_rewards.append((rx, rz))
    rewards = new_rewards

    new_bombs = []
    for bx, bz in bombs:
        dist_sq = (player_pos[0] - bx)**2 + (player_pos[1] - bz)**2
        if dist_sq < 0.5**2:
            if b_key_pressed:
                score_2 += 1
            else:
                score_2 -= 1
            spawn_items()
            return
        else:
            new_bombs.append((bx, bz))
    bombs = new_bombs

def draw_minimap():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    tile_px = 10
    offset_x, offset_y = 20, WINDOW_H - 20

    for i in range(ROWS):
        for j in range(COLS):
            if maze[i][j] == 1:
                glColor3f(0.5, 0.5, 0.5)
            else:
                glColor3f(0.2, 0.7, 0.2)

            x1 = offset_x + j * tile_px
            y1 = offset_y - i * tile_px
            glBegin(GL_QUADS)
            glVertex2f(x1, y1)
            glVertex2f(x1+tile_px, y1)
            glVertex2f(x1+tile_px, y1-tile_px)
            glVertex2f(x1, y1-tile_px)
            glEnd()

    pi = int(round((player_2["x"] + (ROWS//2)*TILE_SIZE) / TILE_SIZE))
    pj = int(round((player_2["z"] + (COLS//2)*TILE_SIZE) / TILE_SIZE))
    glColor3f(0,0,1)
    px = offset_x + pj*tile_px + tile_px/2
    py = offset_y - pi*tile_px - tile_px/2
    glBegin(GL_QUADS)
    glVertex2f(px-3, py-3)
    glVertex2f(px+3, py-3)
    glVertex2f(px+3, py+3)
    glVertex2f(px-3, py+3)
    glEnd()

    for rx, rz in rewards:
        r_i = int(round((rx + (ROWS//2)*TILE_SIZE) / TILE_SIZE))
        r_j = int(round((rz + (COLS//2)*TILE_SIZE) / TILE_SIZE))
        r_x_mini = offset_x + r_j * tile_px + tile_px/2
        r_y_mini = offset_y - r_i * tile_px - tile_px/2
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(r_x_mini-2, r_y_mini-2)
        glVertex2f(r_x_mini+2, r_y_mini-2)
        glVertex2f(r_x_mini+2, r_y_mini+2)
        glVertex2f(r_x_mini-2, r_y_mini+2)
        glEnd()

    for bx, bz in bombs:
        b_i = int(round((bx + (ROWS//2)*TILE_SIZE) / TILE_SIZE))
        b_j = int(round((bz + (COLS//2)*TILE_SIZE) / TILE_SIZE))
        b_x_mini = offset_x + b_j * tile_px + tile_px/2
        b_y_mini = offset_y - b_i * tile_px - tile_px/2
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(b_x_mini-2, b_y_mini-2)
        glVertex2f(b_x_mini+2, b_y_mini-2)
        glVertex2f(b_x_mini+2, b_y_mini+2)
        glVertex2f(b_x_mini-2, b_y_mini+2)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ---------------------------
# Level 3 Drawing & Logic (Dragon Slayer)
# ---------------------------

def init_level_3():
    """Initializes or resets the game state for Level 3."""
    global dragons, fireballs, player_projectiles, player_3, LAST_FIRE_TIME, score_3, fireball_hits
    score_3 = 0
    fireball_hits = 0
    dragons = []
    fireballs = []
    player_projectiles = []
    player_3["x"] = 0.0
    player_3["z"] = 0.0
    LAST_FIRE_TIME = time.time()
    spawn_dragons()

def draw_ground_3():
    """Draws a grid for the ground."""
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glEnd()

    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-int(ENV_SIZE/2), int(ENV_SIZE/2) + 1, 2):
        glVertex3f(i, 0.01, -ENV_SIZE)
        glVertex3f(i, 0.01, ENV_SIZE)
        glVertex3f(-ENV_SIZE, 0.01, i)
        glVertex3f(ENV_SIZE, 0.01, i)
    glEnd()

def draw_dragon(x, z):
    """Draws a simplified dragon model with new colors."""
    glPushMatrix()
    glTranslatef(x, 1.5, z)

    # Body
    glColor3f(0.4, 0.2, 0.6) # Dark purple
    glutSolidCube(1.0)

    # Head
    glColor3f(0.6, 0.4, 0.8) # Lighter purple head
    glPushMatrix()
    glTranslatef(0.0, 0.8, 0.4)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.5, 1.0, 10, 2)
    glPopMatrix()

    # Wings
    glColor3f(0.3, 0.1, 0.5)
    glBegin(GL_TRIANGLES)
    # Right wing
    glVertex3f(0.5, 0.5, 0.0)
    glVertex3f(1.5, 1.5, 0.0)
    glVertex3f(0.5, 1.5, 0.0)
    # Left wing
    glVertex3f(-0.5, 0.5, 0.0)
    glVertex3f(-1.5, 1.5, 0.0)
    glVertex3f(-0.5, 1.5, 0.0)
    glEnd()

    glPopMatrix()

def draw_fireball(x, z):
    """Draws a red fireball."""
    glPushMatrix()
    glTranslatef(x, 0.5, z)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(0.3, 16, 16)
    glPopMatrix()

def draw_player_projectile(x, z):
    """Draws a blue player projectile."""
    glPushMatrix()
    glTranslatef(x, 0.5, z)
    glColor3f(0.0, 0.0, 1.0)
    glutSolidSphere(0.3, 16, 16)
    glPopMatrix()

def draw_player_3():
    """Draws player as a colored cube."""
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(player_3["x"], 0.5, player_3["z"])
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_entities():
    """Draws all dragons, fireballs, and player projectiles."""
    for d in dragons:
        draw_dragon(d["x"], d["z"])
    for fb in fireballs:
        draw_fireball(fb["x"], fb["z"])
    for pp in player_projectiles:
        draw_player_projectile(pp["x"], pp["z"])

def set_isometric_camera_3():
    """Calculates and sets the camera for an isometric view."""
    angle_rad = math.radians(isometric_angle_3)
    elevation_rad = math.radians(isometric_elevation_3)

    cam_x = camera_distance_3 * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = camera_distance_3 * math.sin(elevation_rad)
    cam_z = camera_distance_3 * math.sin(angle_rad) * math.cos(elevation_rad)

    gluLookAt(cam_x, cam_y, cam_z,
              0, 0, 0,
              0, 1, 0)

def spawn_dragons():
    """Spawns dragons in a circle at a distance from the center."""
    for i in range(DRAGON_COUNT):
        angle = (2 * math.pi / DRAGON_COUNT) * i
        dist = 15.0
        x = dist * math.cos(angle)
        z = dist * math.sin(angle)
        dragons.append({
            "x": x,
            "z": z
        })

def spawn_fireball(dragon_pos, target_pos):
    """Creates a fireball instance aimed at the player."""
    velocity = [target_pos["x"] - dragon_pos["x"], target_pos["z"] - dragon_pos["z"]]
    magnitude = math.sqrt(velocity[0]**2 + velocity[1]**2)
    if magnitude > 0:
        velocity[0] /= magnitude
        velocity[1] /= magnitude

    fireballs.append({
        "x": dragon_pos["x"],
        "z": dragon_pos["z"],
        "vx": velocity[0] * 0.2,
        "vz": velocity[1] * 0.2
    })

def check_collision_general(pos1, pos2, radius1, radius2):
    """Checks for collision between two circular objects."""
    distance = math.sqrt((pos1["x"] - pos2["x"])**2 + (pos1["z"] - pos2["z"])**2)
    return distance < radius1 + radius2

def update_game_state_3():
    """Updates the position of all entities and checks for collisions."""
    global fireballs, player_projectiles, dragons, game_over, win, LAST_FIRE_TIME, score_3, fireball_hits

    if game_over or level_2_completed:
        return

    # Check for win condition
    if len(dragons) == 0:
        game_over = True
        win = True
        return

    # Check for lose condition (10 fireballs hits)
    if fireball_hits >= MAX_FIREBALL_HITS:
        game_over = True
        win = False
        return

    # Update fireballs
    fireballs_to_keep = []
    for fb in fireballs:
        fb["x"] += fb["vx"]
        fb["z"] += fb["vz"]
        if abs(fb["x"]) < ENV_SIZE and abs(fb["z"]) < ENV_SIZE:
            fireballs_to_keep.append(fb)
    fireballs = fireballs_to_keep

    # Update player projectiles
    player_projectiles_to_keep = []
    for pp in player_projectiles:
        pp["x"] += pp["vx"]
        pp["z"] += pp["vz"]
        if abs(pp["x"]) < ENV_SIZE and abs(pp["z"]) < ENV_SIZE:
            player_projectiles_to_keep.append(pp)
    player_projectiles = player_projectiles_to_keep

    # Dragon firing logic
    if time.time() - LAST_FIRE_TIME > FIRE_INTERVAL and dragons:
        random.shuffle(dragons)
        for i in range(min(1, len(dragons))):
            spawn_fireball(dragons[i], player_3)
        LAST_FIRE_TIME = time.time()

    # Collision detection
    # Player vs. fireball collision
    fireballs_to_keep = []
    for fb in fireballs:
        if check_collision_general(player_3, fb, 0.5, 0.3):
            fireball_hits += 1
        else:
            fireballs_to_keep.append(fb)
    fireballs = fireballs_to_keep

    # Projectile vs. dragon collision
    projectiles_to_remove = set()
    dragons_to_keep = []
    for i, pp in enumerate(player_projectiles):
        hit = False
        for d in dragons:
            if check_collision_general(d, pp, 1.0, 0.3):
                score_3 += 1
                hit = True
                projectiles_to_remove.add(i)
                dragons.remove(d)
                break

    player_projectiles = [pp for i, pp in enumerate(player_projectiles) if i not in projectiles_to_remove]
    glutPostRedisplay()

# ---------------------------
# Main Game Loop & Controls
# ---------------------------
def transition_to_level_2():
    """Resets Level 2 state and initiates the transition."""
    global current_level, score_2, countdown_timer_2, last_update_time_2, level_1_completed
    current_level = LEVEL_2
    score_2 = 0
    countdown_timer_2 = 60.0
    last_update_time_2 = time.time()
    player_2["x"], player_2["z"] = find_valid_start()
    spawn_items()
    level_1_completed = False # Reset the flag
    print("Level 2 initiated.")

def transition_to_level_3():
    global current_level, level_2_completed
    current_level = LEVEL_3
    init_level_3()
    level_2_completed = False
    print("Level 3 initiated.")

def display():
    global current_level, countdown_timer_1, countdown_timer_2, last_update_time_2, game_over, win, score_1, score_2, score_3, level_1_completed, level_2_completed

    # Game over and win/lose logic for all levels
    if current_level == LEVEL_2 and not level_2_completed and not game_over:
        current_time = time.time()
        delta_time = current_time - last_update_time_2
        last_update_time_2 = current_time
        countdown_timer_2 -= delta_time

        if score_2 >= 10:
            level_2_completed = True
        elif countdown_timer_2 <= 0:
            game_over = True
            win = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.7, 0.9, 1.0)

    if current_level == LEVEL_1:
        set_third_person_camera_1()
        draw_ground_1()
        draw_stones()
        draw_player_1()
        draw_text(f"Score: {score_1} | Time: {int(countdown_timer_1)}", 10, WINDOW_H - 30)
        draw_text("Arrow Keys: Move, R: Reset, ESC: Quit", 10, 10)
    elif current_level == LEVEL_2:
        set_isometric_camera_2()
        draw_ground_2()
        draw_walls()
        draw_items()
        draw_player_2()
        glDisable(GL_DEPTH_TEST)
        draw_minimap()
        glEnable(GL_DEPTH_TEST)
        draw_text(f"Score: {score_2} | Time: {int(countdown_timer_2)}", 10, WINDOW_H - 30)
        draw_text("Arrow Keys: Move, I/K: Zoom, J/L: Rotate, R: Reset, B: Bomb Mode", 10, 10)
    elif current_level == LEVEL_3:
        set_isometric_camera_3()
        draw_ground_3()
        draw_player_3()
        draw_entities()
        draw_text(f"Score: {score_3}", 10, WINDOW_H - 30)
        draw_text(f"Hits Taken: {fireball_hits} / {MAX_FIREBALL_HITS}", 10, WINDOW_H - 50)
        draw_text(f"Dragons left: {len(dragons)}", 10, WINDOW_H - 70)
        draw_text("Space: Shoot | Arrow Keys: Move | I/K: Zoom | J/L: Rotate | R: Reset", 10, 10)

    # Display level completion or game over messages
    if level_1_completed and not game_over:
        draw_text("Level 1 Complete! Press ENTER to continue.", WINDOW_W / 2 - 150, WINDOW_H / 2)
    elif level_2_completed and not game_over:
        draw_text("Level 2 Complete! Press ENTER to continue.", WINDOW_W / 2 - 150, WINDOW_H / 2)
    elif game_over:
        message = ""
        if current_level == LEVEL_1:
            message = "Game Over! Time's up!"
        elif current_level == LEVEL_2:
            message = "Game Over! You didn't collect 10 items in time."
        elif current_level == LEVEL_3:
            message = "Game Over! Too many hits!"

        if win:
            if current_level == LEVEL_3:
                message = "You Win! Final Score: " + str(score_3)
            elif current_level == LEVEL_2:
                 message = "You Win! Final Score: " + str(score_2)
            else:
                 message = "You Win! Level 1 Complete!"

        glWindowPos2f(WINDOW_W/2 - len(message)*4, WINDOW_H/2)
        for c in message:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

        reset_msg = "Press 'R' to play again."
        glWindowPos2f(WINDOW_W/2 - len(reset_msg)*4, WINDOW_H/2 - 30)
        for c in reset_msg:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

    glutSwapBuffers()

def update_game_state():
    if not game_over:
        if current_level == LEVEL_1 and not level_1_completed:
            update_game_state_1()
        elif current_level == LEVEL_3 and not level_2_completed:
            update_game_state_3()
    glutPostRedisplay()

def keyboard(key, x, y):
    global current_level, game_over, win, score_1, score_2, countdown_timer_1, countdown_timer_2, last_update_time_1, last_update_time_2, isometric_angle_2, camera_distance_2, b_key_pressed, level_1_completed, level_2_completed, isometric_angle_3, camera_distance_3, player_projectiles
    key_str = key.decode('utf-8')

    if key_str == '\x1b':
        glutLeaveMainLoop()
    elif key_str == 'r':
        current_level = LEVEL_1
        game_over = False
        win = False
        level_1_completed = False
        level_2_completed = False
        score_1 = 0
        score_2 = 0
        player_1["x"] = 0.0
        player_1["z"] = 5.0
        player_2["x"], player_2["z"] = find_valid_start()
        spawn_items()
        countdown_timer_1 = 60.0
        last_update_time_1 = time.time()
        countdown_timer_2 = 30.0
        last_update_time_2 = time.time()
        init_level_3()
    elif key_str == '\r': # Enter key
        if level_1_completed:
            transition_to_level_2()
        elif level_2_completed:
            transition_to_level_3()
    elif current_level == LEVEL_2 and not game_over:
        if key_str == 'i':
            camera_distance_2 = max(8.0, camera_distance_2 - 2.0)
        elif key_str == 'k':
            camera_distance_2 = min(35.0, camera_distance_2 + 2.0)
        elif key_str == 'j':
            isometric_angle_2 = (isometric_angle_2 - 5) % 360
        elif key_str == 'l':
            isometric_angle_2 = (isometric_angle_2 + 5) % 360
        elif key_str == 'b':
            b_key_pressed = True
    elif current_level == LEVEL_3 and not game_over:
        if key_str == 'i':
            camera_distance_3 = max(5.0, camera_distance_3 - 2.0)
        elif key_str == 'k':
            camera_distance_3 = min(40.0, camera_distance_3 + 2.0)
        elif key_str == 'j':
            isometric_angle_3 = (isometric_angle_3 - 5) % 360
        elif key_str == 'l':
            isometric_angle_3 = (isometric_angle_3 + 5) % 360
        elif key_str == ' ': # Spacebar to shoot
            player_projectiles.append({
                "x": player_3["x"],
                "z": player_3["z"],
                "vx": 0.0,
                "vz": -0.5
            })

    glutPostRedisplay()

def keyboard_up(key, x, y):
    global b_key_pressed
    key_str = key.decode('utf-8')
    if key_str == 'b':
        b_key_pressed = False
    glutPostRedisplay()

def special_keys(key, x, y):
    if game_over or level_1_completed or level_2_completed:
        return

    if current_level == LEVEL_1:
        if key == GLUT_KEY_LEFT:
            player_1["x"] = max(-30 / 2 + 0.5, player_1["x"] - 0.5)
        elif key == GLUT_KEY_RIGHT:
            player_1["x"] = min(30 / 2 - 0.5, player_1["x"] + 0.5)
        elif key == GLUT_KEY_UP:
            player_1["z"] = player_1["z"] - 0.5
        elif key == GLUT_KEY_DOWN:
            player_1["z"] = player_1["z"] + 0.5

    elif current_level == LEVEL_2:
        new_x, new_z = player_2["x"], player_2["z"]
        if key == GLUT_KEY_UP:
            new_z -= 0.5
        elif key == GLUT_KEY_DOWN:
            new_z += 0.5
        elif key == GLUT_KEY_LEFT:
            new_x -= 0.5
        elif key == GLUT_KEY_RIGHT:
            new_x += 0.5

        if not check_collision_2(new_x, new_z):
            player_2["x"] = new_x
            player_2["z"] = new_z

        check_item_collision()
    
    elif current_level == LEVEL_3:
        move_speed = 0.5
        if key == GLUT_KEY_UP:
            player_3["z"] = max(-ENV_SIZE/2 + 1, player_3["z"] - move_speed)
        elif key == GLUT_KEY_DOWN:
            player_3["z"] = min(ENV_SIZE/2 - 1, player_3["z"] + move_speed)
        elif key == GLUT_KEY_LEFT:
            player_3["x"] = max(-ENV_SIZE/2 + 1, player_3["x"] - move_speed)
        elif key == GLUT_KEY_RIGHT:
            player_3["x"] = min(ENV_SIZE/2 - 1, player_3["x"] + move_speed)

    glutPostRedisplay()

# ---------------------------
# Main
# ---------------------------

def main():
    """Initializes OpenGL and starts the main loop."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Three-Level Game Challenge - PyOpenGL")

    player_1["x"] = 0.0
    player_1["z"] = 5.0
    player_2["x"], player_2["z"] = find_valid_start()

    glutDisplayFunc(display)
    glutIdleFunc(update_game_state)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)

    print("Three-Level Game Challenge")
    print("Level 1: Rolling Stones - Dodge stones to reach the finish line.")
    print("Level 2: 3D Maze - Collect 10 rewards before the time runs out.")
    print("Level 3: Dragon Slayer - Shoot down dragons and avoid fireballs.")
    print("Controls:")
    print("Arrow Keys: Move")
    print("R: Reset the game")
    print("ESC: Quit")

    glutMainLoop()

if __name__ == "__main__":
    main()
