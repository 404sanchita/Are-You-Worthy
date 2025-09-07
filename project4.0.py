from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
import subprocess
import sys

WINDOW_W, WINDOW_H = 1000, 800
ENV_SIZE = 30.0
TREE_COUNT = 20

riddle_active = False
current_riddle = ""
current_answer = ""
scrambled_tiles = []
selected_tiles = []
riddle_attempts = 0
riddle_score = 0
riddle_tiles = []
riddle_timer = 0
riddle_time_limit = 60
timer_start_time = 0

# River dimensions
RIVER_X_START = -ENV_SIZE / 2
RIVER_X_END = -ENV_SIZE / 2 + 3
RIVER_Z_START = -ENV_SIZE / 2
RIVER_Z_END = ENV_SIZE / 2

trees = []
while len(trees) < TREE_COUNT:
    x = random.uniform(-ENV_SIZE / 2 + 2, ENV_SIZE / 2 - 2)
    z = random.uniform(-ENV_SIZE / 2 + 2, ENV_SIZE / 2 - 2)

    # Check if the generated position is inside the river area
    is_in_river = (RIVER_X_START <= x <= RIVER_X_END)

    # If the tree is not in the river, add it to the list
    if not is_in_river:
        trees.append((x, z))
watering = False
golden_apple = {"active": False, "x": 0.0, "z": 0.0}

isometric_angle = 45
isometric_elevation = 30
camera_distance = 20.0

player = {"x": 0.0, "z": 0.0, "yaw": 0.0, "y": 0.0}
m_speed = 0.5

watering_gauge = 0
max_gauge = 10
golden_apples = 0
lives = 3
dragon_healed = False
holding_p = False

dragon_pos = [0, 1, 0]

quad = None

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_ground():
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glEnd()

    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-int(ENV_SIZE / 2), int(ENV_SIZE / 2) + 1, 2):
        glVertex3f(i, 0.05, -ENV_SIZE)
        glVertex3f(i, 0.05, ENV_SIZE)
        glVertex3f(-ENV_SIZE, 0.05, i)
        glVertex3f(ENV_SIZE, 0.05, i)
    glEnd()

def draw_tree(x, z):
    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(x, 1.0, z)
    glScalef(0.3, 2.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.1, 0.5, 0.1)
    glPushMatrix()
    glTranslatef(x, 2.5, z)
    glutSolidSphere(0.8, 16, 16)
    glPopMatrix()

def draw_trees():
    for x, z in trees:
        draw_tree(x, z)

def draw_player():
    glPushMatrix()
    glTranslatef(player["x"], player["y"], player["z"])

    glColor3f(0.2, 0.6, 0.8)
    glPushMatrix()
    glScalef(0.5, 1.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(0, 0.75, 0)
    glutSolidSphere(0.25, 20, 20)
    glPopMatrix()

    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(-0.1, 0.85, 0.12)
    glutSolidSphere(0.05, 10, 10)
    glTranslatef(0.2, 0, 0)
    glutSolidSphere(0.05, 10, 10)
    glPopMatrix()

    glColor3f(0.2, 0.2, 0.6)
    for offset in [-0.15, 0.15]:
        glPushMatrix()
        glTranslatef(offset, -0.75, 0)
        glScalef(0.1, 0.5, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

    glColor3f(1.0, 0.8, 0.6)
    for offset, rot in [(-0.3, 90), (0.3, -90)]:
        glPushMatrix()
        glTranslatef(offset, 0.25, 0)
        glRotatef(rot, 0, 1, 0)
        glRotatef(-20, 1, 0, 0)
        gluCylinder(quad, 0.08, 0.08, 0.4, 12, 1)
        glPopMatrix()

    glColor3f(0.8, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, -0.2)
    glRotatef(10, 1, 0, 0)
    glScalef(0.6, 1.0, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

def draw_dragon():
    global quad
    if quad is None:
        quad = gluNewQuadric()

    glPushMatrix()
    glTranslatef(dragon_pos[0], dragon_pos[1], dragon_pos[2])

    glPushMatrix()
    glColor3f(0.7, 0.1, 0.1)
    glScalef(1.2, 0.8, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.8, 0.2, 0.2)
    glTranslatef(0, 0.5, 1.0)

    glPushMatrix()
    glRotatef(-30, 1, 0, 0)
    glScalef(0.4, 0.4, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0.2, 0.8)
    glScalef(0.6, 0.5, 0.8)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.9, 0.3, 0.3)
    glTranslatef(0, 0.1, 1.3)
    glRotatef(-30, 1, 0, 0)
    glScalef(0.3, 0.3, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glTranslatef(-0.2, 0.4, 1.0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.08, 0.3, 10, 10)
    glTranslatef(0.4, 0, 0)
    glutSolidCone(0.08, 0.3, 10, 10)
    glPopMatrix()

    glPopMatrix()

    glPushMatrix()
    glColor3f(0.6, 0.1, 0.1)
    glTranslatef(0, 0.2, -1.2)
    glRotatef(180, 0, 1, 0)
    glutSolidCone(0.3, 1.2, 12, 12)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.6, 0.1, 0.1)

    glPushMatrix()
    glTranslatef(-0.8, 0.4, 0.2)
    glRotatef(45, 0, 0, 1)
    glScalef(0.1, 1.2, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.8, 0.4, 0.2)
    glRotatef(-45, 0, 0, 1)
    glScalef(0.1, 1.2, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(-0.5, -0.4, 0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)

    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)

    for i in range(3):
        glPushMatrix()
        glTranslatef(0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(30 if i == 0 else -30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()

    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(0.5, -0.4, 0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)

    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)

    for i in range(3):
        glPushMatrix()
        glTranslatef(-0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(-30 if i == 0 else 30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()

    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(-0.4, -0.4, -0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)

    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)

    for i in range(3):
        glPushMatrix()
        glTranslatef(0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(30 if i == 0 else -30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()

    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(0.4, -0.4, -0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)

    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)

    for i in range(3):
        glPushMatrix()
        glTranslatef(-0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(-30 if i == 0 else 30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()

    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(-0.3, 0.7, 1.4)
    glutSolidSphere(0.1, 12, 12)
    glTranslatef(0.6, 0, 0)
    glutSolidSphere(0.1, 12, 12)

    glColor3f(0, 0, 0)
    glTranslatef(-0.6, 0, 0.03)
    glutSolidSphere(0.05, 8, 8)
    glTranslatef(0.6, 0, 0)
    glutSolidSphere(0.05, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    for i in range(7):
        z_pos = -1.0 + i * 0.3
        glPushMatrix()
        glTranslatef(0, 0.6, z_pos)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(0.1, 0.3, 8, 8)
        glPopMatrix()
    glPopMatrix()

    glPopMatrix()

def draw_river():
    glColor3f(0.0, 0.4, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(RIVER_X_START, 0.01, RIVER_Z_START)
    glVertex3f(RIVER_X_END, 0.01, RIVER_Z_START)
    glVertex3f(RIVER_X_END, 0.01, RIVER_Z_END)
    glVertex3f(RIVER_X_START, 0.01, RIVER_Z_END)
    glEnd()

def draw_fruits():
    if golden_apple["active"]:
        glColor3f(1.0, 0.84, 0.0)
        glPushMatrix()
        glTranslatef(golden_apple["x"], 3.3, golden_apple["z"])
        glutSolidSphere(0.3, 16, 16)
        glPopMatrix()

def draw_gauge():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(750, 700)
    glVertex2f(970, 700)
    glVertex2f(970, 730)
    glVertex2f(750, 730)
    glEnd()

    glColor3f(0, 1, 0)
    fill = min(watering_gauge * 30, 220)
    glBegin(GL_QUADS)
    glVertex2f(750, 700)
    glVertex2f(750 + fill, 700)
    glVertex2f(750 + fill, 730)
    glVertex2f(750, 730)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_minimap():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor4f(0.1, 0.1, 0.1, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(10, 10)
    glVertex2f(160, 10)
    glVertex2f(160, 160)
    glVertex2f(10, 160)
    glEnd()

    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(20, 20)
    glVertex2f(150, 20)
    glVertex2f(150, 150)
    glVertex2f(20, 150)
    glEnd()

    glColor3f(0.4, 0.2, 0.1)
    for x, z in trees:
        map_x = 20 + (x + ENV_SIZE / 2) * 130 / ENV_SIZE
        map_y = 20 + (z + ENV_SIZE / 2) * 130 / ENV_SIZE
        glBegin(GL_QUADS)
        glVertex2f(map_x - 2, map_y - 2)
        glVertex2f(map_x + 2, map_y - 2)
        glVertex2f(map_x + 2, map_y + 2)
        glVertex2f(map_x - 2, map_y + 2)
        glEnd()

    map_x = 20 + (player["x"] + ENV_SIZE / 2) * 130 / ENV_SIZE
    map_y = 20 + (player["z"] + ENV_SIZE / 2) * 130 / ENV_SIZE
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(map_x - 3, map_y - 3)
    glVertex2f(map_x + 3, map_y - 3)
    glVertex2f(map_x + 3, map_y + 3)
    glVertex2f(map_x - 3, map_y + 3)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def init_riddles(tree_x, tree_z):
    global current_riddle, current_answer, scrambled_tiles, riddle_attempts, riddle_score, riddle_tiles, golden_apple
    
    riddles = [
    {"question": "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?", "answer": "ECHO"},
    {"question": "The more you take, the more you leave behind. What am I?", "answer": "FOOTSTEPS"},
    {"question": "What has keys but can’t open locks?", "answer": "PIANO"},
    {"question": "I’m tall when I’m young and short when I’m old. What am I?", "answer": "CANDLE"},
    {"question": "What can travel around the world while staying in a corner?", "answer": "STAMP"}]

    riddle = random.choice(riddles)
    current_riddle = riddle["question"]
    current_answer = riddle["answer"]

    scrambled = list(current_answer)
    random.shuffle(scrambled)
    scrambled_tiles = scrambled
    selected_tiles.clear()
    riddle_attempts = 0
    riddle_score = 0
    
    riddle_tiles.clear()
    angle_step = 360 / len(scrambled_tiles)
    radius = 3.0
    
    for i, letter in enumerate(scrambled_tiles):
        angle = math.radians(i * angle_step)
        x = player["x"] + radius * math.cos(angle)
        z = player["z"] + radius * math.sin(angle)
        riddle_tiles.append({"x": x, "z": z, "letter": letter, "collected": False})

    golden_apple["active"] = True
    golden_apple["x"] = tree_x
    golden_apple["z"] = tree_z
    
    start_riddle_timer()

def check_riddle_answer():
    global riddle_attempts, riddle_score, riddle_active, golden_apples, selected_tiles
    
    player_answer = ''.join(selected_tiles)
    if player_answer == current_answer:
        riddle_attempts += 1
        
        if riddle_attempts == 1:
            riddle_score = 100
            print("Perfect! +100 points!")
        elif riddle_attempts == 2:
            riddle_score = 70
            print("Good! +70 points!")
        else:
            riddle_score = 40
            print("Correct! +40 points!")
        
        golden_apples += 1
        print(f"You earned a golden apple! Total: {golden_apples}")

        riddle_active = False
        
    else:
        riddle_attempts += 1
        print(f"Wrong answer. Attempt {riddle_attempts}/3")
        
        if riddle_attempts >= 3:
            print("Failed to solve the riddle. Try watering another tree.")
            riddle_active = False
            selected_tiles = []
        else:
            selected_tiles = []
            for tile in riddle_tiles:
                tile["collected"] = False
            print("Try again! Right-click on tiles in the correct order.")

def draw_riddle_tiles():
    if not riddle_active:
        return
        
    for tile in riddle_tiles:
        if tile["collected"]:
            continue
            
        glPushMatrix()
        glTranslatef(tile["x"], 1.0, tile["z"])
        glColor3f(0.8, 0.8, 0.1)
        glutSolidCube(0.5)
        
        glColor3f(0, 0, 0)
        glRasterPos3f(-0.1, 0.5, 0.1)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(tile["letter"]))
        glPopMatrix()

def start_riddle_timer():
    global riddle_timer, timer_start_time
    riddle_timer = riddle_time_limit
    timer_start_time = time.time()

def update_riddle_timer():
    global riddle_timer, lives, riddle_active
    if riddle_active:
        elapsed = time.time() - timer_start_time
        riddle_timer = max(0, riddle_time_limit - elapsed)
        
        if riddle_timer <= 0:
            print("⏰ Time's up! You lost a life.")
            lives -= 1
            riddle_active = False
            return True
    return False

def set_isometric_camera():
    angle_rad = math.radians(isometric_angle)
    elevation_rad = math.radians(isometric_elevation)
    
    cam_x = player["x"] + camera_distance * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = player["y"] + camera_distance * math.sin(elevation_rad)
    cam_z = player["z"] + camera_distance * math.sin(angle_rad) * math.cos(elevation_rad)
    
    gluLookAt(cam_x, cam_y, cam_z,
              player["x"], player["y"], player["z"],
              0, 1, 0)

def check_collision(x, z):
    for tx, tz in trees:
        if math.sqrt((x - tx) ** 2 + (z - tz) ** 2) < 1.5:
            return True
    if abs(x) > ENV_SIZE / 2 - 1 or abs(z) > ENV_SIZE / 2 - 1:
        return True
    return False

def check_river_collision():
    if RIVER_X_START <= player["x"] <= RIVER_X_END and RIVER_Z_START <= player["z"] <= RIVER_Z_END:
        return True
    return False

def check_dragon_collision():
    distance = math.sqrt((player["x"] - dragon_pos[0]) ** 2 +
                         (player["y"] - dragon_pos[1]) ** 2 +
                         (player["z"] - dragon_pos[2]) ** 2)
    return distance < 3.0

def check_golden_apple_collision():
    global golden_apples
    if golden_apple["active"]:
        distance = math.sqrt((player["x"] - golden_apple["x"]) ** 2 + (player["z"] - golden_apple["z"]) ** 2)
        if distance < 1.5:
            golden_apples += 1
            golden_apple["active"] = False
            print(f"🍏 Golden apple collected! Total: {golden_apples}")

def select_nearest_tile():
    global selected_tiles, riddle_active
    
    if not riddle_active:
        return
        
    nearest_tile = None
    min_distance = float('inf')
    
    for tile in riddle_tiles:
        if tile["collected"]:
            continue
            
        dx = tile["x"] - player["x"]
        dz = tile["z"] - player["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        
        if distance < min_distance:
            min_distance = distance
            nearest_tile = tile
    
    if nearest_tile and min_distance < 2.0:
        selected_tiles.append(nearest_tile["letter"])
        nearest_tile["collected"] = True
        print(f"Selected: {''.join(selected_tiles)}")
        
        new_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        nearest_tile["letter"] = new_letter
        nearest_tile["collected"] = False
        print(f"Tile replaced with: {new_letter}")
        
        if len(selected_tiles) == len(current_answer):
            check_riddle_answer()

def keyboard(key, x, y):
    global isometric_angle, camera_distance, holding_p, golden_apples, dragon_healed
    global selected_tiles, riddle_active
    
    key = key.decode('utf-8')
    if key == '\x1b':
        glutLeaveMainLoop()
    elif key == 'r':
        player["x"] = 0.0
        player["z"] = 0.0
        player["y"] = 0.0
    elif key == 'i':
        camera_distance = max(5.0, camera_distance - 2.0)
    elif key == 'k':
        camera_distance = min(40.0, camera_distance + 2.0)
    elif key == 'j':
        isometric_angle = (isometric_angle - 5) % 360
    elif key == 'l':
        isometric_angle = (isometric_angle + 5) % 360
    elif key == 'p':
        holding_p = True
    elif key == 'f':
        feed_dragon()
    elif key == 'e':
        if riddle_active:
            select_nearest_tile()
    elif key.lower() == 'n':
        if dragon_healed:
            print("Loading next level...")
            
            next_file = "project2.6.py"
            subprocess.Popen([sys.executable, next_file])
            glutLeaveMainLoop()
        else:
            print("You must heal the dragon first before moving to the next level!")

def keyboard_up(key, x, y):
    global holding_p
    key = key.decode('utf-8')
    if key == 'p':
        holding_p = False
        water_plant()

def special_keys(key, x, y):
    angle_rad = math.radians(isometric_angle)
    dx = dz = 0
    
    if key == GLUT_KEY_UP:
        dx = m_speed * math.cos(angle_rad)
        dz = -m_speed * math.sin(angle_rad)
    elif key == GLUT_KEY_DOWN:
        dx = -m_speed * math.cos(angle_rad)
        dz = m_speed * math.sin(angle_rad)
    
    elif key == GLUT_KEY_LEFT:
        dx = -m_speed * math.sin(angle_rad)
        dz = -m_speed * math.cos(angle_rad)
    elif key == GLUT_KEY_RIGHT:
        dx = m_speed * math.sin(angle_rad)
        dz = m_speed * math.cos(angle_rad)
    
    new_x = player["x"] + dx
    new_z = player["z"] + dz
    
    if not check_collision(new_x, new_z):
        player["x"] = new_x
        player["z"] = new_z

def water_plant():
    global watering_gauge, riddle_active, fruits
    
    nearest_tree = None
    min_distance = float('inf')
    
    for x, z in trees:
        distance = math.sqrt((player["x"] - x) ** 2 + (player["z"] - z) ** 2)
        if distance < min_distance:
            min_distance = distance
            nearest_tree = (x, z)
    
    if nearest_tree and min_distance < 2.0:
        if watering_gauge >= 10:
            watering_gauge -= 10
            
            init_riddles(nearest_tree[0], nearest_tree[1])
            riddle_active = True
            print(f"Riddle: {current_riddle}")
            print("Right-click on tiles in the correct order to solve the riddle!")
            print(f"You have {riddle_time_limit} seconds!")
        else:
            print("Not enough water to grow fruit! Need at least 10 water.")
    else:
        print("No trees nearby to water!")

def update_watering():
    global watering_gauge
    if holding_p and check_river_collision():
        watering_gauge = min(max_gauge, watering_gauge + 2)
    elif not holding_p and watering_gauge > 0:
        watering_gauge = max(0, watering_gauge - 1)

def feed_dragon():
    global golden_apples, dragon_healed
    distance = math.sqrt((player["x"] - dragon_pos[0]) ** 2 +
                         (player["y"] - dragon_pos[1]) ** 2 +
                         (player["z"] - dragon_pos[2]) ** 2)
    if distance < 3.0:
        if golden_apples > 0:
            golden_apples -= 1
            dragon_healed = True
            print("Dragon healed! Thank you for the golden apple!")
        else:
            print("You have no golden apples to feed the dragon!")
    else:
        print("You are too far from the dragon to feed it!")

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glClearColor(0.5, 0.7, 0.9, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W / float(WINDOW_H), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    set_isometric_camera()
    
    draw_ground()
    draw_river()
    draw_trees()
    draw_fruits()

    update_watering()
    check_dragon_collision()
    
    draw_player()
    draw_dragon()

    draw_minimap()
    draw_gauge()
    
    draw_text(10, 770, f"Apples: {golden_apples} | Lives: {lives} | Water: {watering_gauge}")
    
    if dragon_healed:
        draw_text(10, 740, "Dragon healed! Quest complete! Press N for next level!")
    
    if check_river_collision():
        draw_text(10, 680, "Standing in river - collecting water!")
    
    dragon_distance = math.sqrt((player["x"] - dragon_pos[0]) ** 2 +
                                 (player["y"] - dragon_pos[1]) ** 2 +
                                 (player["z"] - dragon_pos[2]) ** 2)
    if dragon_distance < 5.0:
        if golden_apples > 0:
            draw_text(10, 650, "Press F to feed dragon a golden apple!")
        else:
            draw_text(10, 650, "Dragon needs golden apples to heal!")
    
    time_up = update_riddle_timer()
    if time_up:
        pass
    
    if riddle_active:
        draw_riddle_tiles()
        
        draw_text(300, 430, f"RIDDLE: {current_riddle}")
        draw_text(300, 400, f"Your answer: {''.join(selected_tiles)}")
        draw_text(300, 370, f"Attempts: {riddle_attempts}/3")
        draw_text(300, 340, f"Time: {int(riddle_timer)} seconds")
        draw_text(300, 310, "Right-click or press E on tiles")
        draw_text(300, 280, "Tiles change when selected!")

    glutSwapBuffers()
    
def mouse(button, state, x, y):
    global selected_tiles, riddle_attempts, riddle_score, riddle_active, golden_apples, fruits
    
    if riddle_active and button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        for tile in riddle_tiles:
            if tile["collected"]:
                continue
                
            dx = tile["x"] - player["x"]
            dz = tile["z"] - player["z"]
            distance = math.sqrt(dx * dx + dz * dz)
            
            if distance < 2.0:
                selected_tiles.append(tile["letter"])
                tile["collected"] = True
                
                new_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                tile["letter"] = new_letter
                tile["collected"] = False
                
                if len(selected_tiles) == len(current_answer):
                    check_riddle_answer()
                break

def main():
    global quad
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Dragon Quest: Are You Worthy?")
    quad = gluNewQuadric()

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutKeyboardUpFunc(keyboard_up)
    glutMouseFunc(mouse)

    print("DRAGON QUEST GAME")
    print("=" * 40)
    print("CONTROLS:")
    print("Arrow Keys: Move around")
    print("P: Collect water (in river) or water plants")
    print("I/K: Zoom camera In/Out")
    print("J/L: Rotate camera view")
    print("R: Reset player position")
    print("ESC: Quit game")
    print("\nGAMEPLAY:")
    print("1. Go to the river (blue area) and press P to collect water")
    print("2. Find trees and press P near them to water and grow golden apples")
    print("3. Feed golden apples to the dragon to heal it!")
    print("\nGOOD LUCK, HERO!")

    glutMainLoop()
    
if __name__ == "__main__":
    main()
