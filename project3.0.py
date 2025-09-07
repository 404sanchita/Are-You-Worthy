from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
import os
import sys
import subprocess
import random

# ---------------------------
# Window config
# ---------------------------
WINDOW_W, WINDOW_H = 1000, 800

# ---------------------------
# Environment config
# ---------------------------
ENV_SIZE = 30.0
TREE_COUNT = 20

# Riddle game variables
riddle_active = False
current_riddle = ""
current_answer = ""
scrambled_tiles = []
selected_tiles = []
riddle_attempts = 0
riddle_score = 0
riddle_tiles = []  # For position of tiles in the world

# ---------------------------
# River & watering system
# ---------------------------
RIVER_X_START = -ENV_SIZE/2
RIVER_X_END = -ENV_SIZE/2 + 3  # Width of river
RIVER_Z_START = -ENV_SIZE/2
RIVER_Z_END = ENV_SIZE/2

# --- FIX: Ensure trees do not spawn in the river ---
trees = []
while len(trees) < TREE_COUNT:
    x = random.uniform(-ENV_SIZE/2 + 2, ENV_SIZE/2 - 2)
    z = random.uniform(-ENV_SIZE/2 + 2, ENV_SIZE/2 - 2)

    # Check if the generated position is inside the river area
    is_in_river = (RIVER_X_START <= x <= RIVER_X_END)

    # If the tree is not in the river, add it to the list
    if not is_in_river:
        trees.append((x, z))
watering = False  # True if player is collecting water

# For fruits on trees
fruits = { (x,z): 0 for x,z in trees }  # 0 = no fruit, 1 = fruit grown
fruit_threshold = 100  # Gauge needed to grow fruit      

# ---------------------------
# Camera & Isometric view
# ---------------------------
isometric_angle = 45
isometric_elevation = 30
camera_distance = 20.0

# ---------------------------
# Player
# ---------------------------
player = {"x": 0.0, "z": 0.0, "yaw": 0.0, "y": 0.0}  # y = height
player_pos = [0, 0, 0]  # for old draw_player
m_speed = 0.5
is_climbing = False
climb_speed = 0.1

# ---------------------------
# Game state
# ---------------------------
watering_gauge = 0
max_gauge = 10
golden_apples = 0
lives = 3
dragon_healed = False
holding_p = False

# ---------------------------
# Mountain
# ---------------------------
MOUNTAIN_HEIGHT = 15
MOUNTAIN_RADIUS = 8
MOUNTAIN_POS = [0, 0, 0]  # Center of the map

# ---------------------------
# Dragon - positioned on top of mountain
# ---------------------------
dragon_pos = [0, 1, 0]  

# ---------------------------
# Falling rocks
# ---------------------------
rocks = []
rock_spawn_timer = 0
rock_spawn_interval = 2  # seconds

# ---------------------------
# GL quadric
# ---------------------------
quad = None

# ---------------------------
# Drawing functions
# ---------------------------
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
    # Draw green ground
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glEnd()

    # Grid lines
    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-int(ENV_SIZE/2), int(ENV_SIZE/2)+1, 2):
        glVertex3f(i, 0.01, -ENV_SIZE)
        glVertex3f(i, 0.01, ENV_SIZE)
        glVertex3f(-ENV_SIZE, 0.01, i)
        glVertex3f(ENV_SIZE, 0.01, i)
    glEnd()

def draw_tree(x, z):
    # Trunk
    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(x, 1.0, z)
    glScalef(0.3, 2.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    # Foliage
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
    glTranslatef(player["x"], player["y"], player["z"])  # player position

    # ---------------- Body ----------------
    glColor3f(0.2, 0.6, 0.8)  # blue shirt
    glPushMatrix()
    glScalef(0.5, 1.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # ---------------- Head ----------------
    glColor3f(1.0, 0.8, 0.6)  # skin tone
    glPushMatrix()
    glTranslatef(0, 0.75, 0)
    glutSolidSphere(0.25, 20, 20)
    glPopMatrix()

    # ---------------- Eyes ----------------
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(-0.1, 0.85, 0.12)
    glutSolidSphere(0.05, 10, 10)
    glTranslatef(0.2, 0, 0)
    glutSolidSphere(0.05, 10, 10)
    glPopMatrix()

    # ---------------- Legs ----------------
    glColor3f(0.2, 0.2, 0.6)  # dark blue pants
    for offset in [-0.15, 0.15]:
        glPushMatrix()
        glTranslatef(offset, -0.75, 0)
        glScalef(0.1, 0.5, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

    # ---------------- Hands ----------------
    glColor3f(1.0, 0.8, 0.6)  # skin tone
    for offset, rot in [(-0.3, 90), (0.3, -90)]:
        glPushMatrix()
        glTranslatef(offset, 0.25, 0)
        glRotatef(rot, 0, 1, 0)
        glRotatef(-20, 1, 0, 0)
        gluCylinder(quad, 0.08, 0.08, 0.4, 12, 1)
        glPopMatrix()

    # ---------------- Cape ----------------
    glColor3f(0.8, 0.1, 0.1)  # red cape
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
    glTranslatef(dragon_pos[0], dragon_pos[1], dragon_pos[2])  # dragon position

   # Main body (red)
    glPushMatrix()
    glColor3f(0.7, 0.1, 0.1)  # Dark red
    glScalef(1.2, 0.8, 2.0)  # width, height, depth
    glutSolidCube(1.0)
    glPopMatrix()

    # Neck and head
    glPushMatrix()
    glColor3f(0.8, 0.2, 0.2)
    glTranslatef(0, 0.5, 1.0)
    
    # Neck
    glPushMatrix()
    glRotatef(-30, 1, 0, 0)
    glScalef(0.4, 0.4, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0, 0.2, 0.8)
    glScalef(0.6, 0.5, 0.8)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Snout
    glPushMatrix()
    glColor3f(0.9, 0.3, 0.3)
    glTranslatef(0, 0.1, 1.3)
    glRotatef(-30, 1, 0, 0)
    glScalef(0.3, 0.3, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Horns
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glTranslatef(-0.2, 0.4, 1.0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.08, 0.3, 10, 10)
    glTranslatef(0.4, 0, 0)
    glutSolidCone(0.08, 0.3, 10, 10)
    glPopMatrix()
    
    glPopMatrix()  # End of neck/head group

    # Tail
    glPushMatrix()
    glColor3f(0.6, 0.1, 0.1)
    glTranslatef(0, 0.2, -1.2)
    glRotatef(180, 0, 1, 0)
    glutSolidCone(0.3, 1.2, 12, 12)
    glPopMatrix()

    # Wings
    glPushMatrix()
    glColor3f(0.6, 0.1, 0.1)
    
    # Left wing
    glPushMatrix()
    glTranslatef(-0.8, 0.4, 0.2)
    glRotatef(45, 0, 0, 1)
    glScalef(0.1, 1.2, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right wing
    glPushMatrix()
    glTranslatef(0.8, 0.4, 0.2)
    glRotatef(-45, 0, 0, 1)
    glScalef(0.1, 1.2, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

    # Enhanced Legs with claws
    # Front left leg
    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(-0.5, -0.4, 0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)
    
    # Foot with claws
    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)
    
    # Claws
    for i in range(3):
        glPushMatrix()
        glTranslatef(0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(30 if i == 0 else -30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

    # Front right leg
    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(0.5, -0.4, 0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)
    
    # Foot with claws
    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)
    
    # Claws
    for i in range(3):
        glPushMatrix()
        glTranslatef(-0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(-30 if i == 0 else 30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

    # Back left leg
    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(-0.4, -0.4, -0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)
    
    # Foot with claws
    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)
    
    # Claws
    for i in range(3):
        glPushMatrix()
        glTranslatef(0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(30 if i == 0 else -30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

    # Back right leg
    glPushMatrix()
    glColor3f(0.7, 0.2, 0.2)
    glTranslatef(0.4, -0.4, -0.6)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.15, 0.1, 0.8, 12, 1)
    
    # Foot with claws
    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(0.12, 12, 12)
    
    # Claws
    for i in range(3):
        glPushMatrix()
        glTranslatef(-0.1 if i == 1 else 0, 0, 0.1)
        glRotatef(-30 if i == 0 else 30 if i == 2 else 0, 0, 1, 0)
        glTranslatef(0, 0, 0.1)
        glutSolidCone(0.03, 0.15, 8, 8)
        glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

    # Eyes
    glPushMatrix()
    glColor3f(1, 1, 1)  # White part
    glTranslatef(-0.3, 0.7, 1.4)
    glutSolidSphere(0.1, 12, 12)
    glTranslatef(0.6, 0, 0)
    glutSolidSphere(0.1, 12, 12)
    
    # Pupils
    glColor3f(0, 0, 0)  # Black pupils
    glTranslatef(-0.6, 0, 0.03)
    glutSolidSphere(0.05, 8, 8)
    glTranslatef(0.6, 0, 0)
    glutSolidSphere(0.05, 8, 8)
    glPopMatrix()

    # Spikes along the back
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

# Draw the river
def draw_river():
    glColor3f(0.0, 0.4, 0.8)  # Blue water
    glBegin(GL_QUADS)
    glVertex3f(RIVER_X_START, 0.01, RIVER_Z_START)
    glVertex3f(RIVER_X_END, 0.01, RIVER_Z_START)
    glVertex3f(RIVER_X_END, 0.01, RIVER_Z_END)
    glVertex3f(RIVER_X_START, 0.01, RIVER_Z_END)
    glEnd()

# Draw fruits on trees
def draw_fruits():
    glColor3f(1.0, 0.84, 0.0)  # Yellow fruits
    for (x, z), has_fruit in fruits.items():
        if has_fruit:
            glPushMatrix()
            glTranslatef(x, 3.3, z)
            glutSolidSphere(0.2, 12, 12)
            glPopMatrix()

# Draw the mountain
#def draw_mountain():
   # glColor3f(0.5, 0.35, 0.25)  # Brown mountain
    #glPushMatrix()
    #glTranslatef(MOUNTAIN_POS[0], MOUNTAIN_POS[1], MOUNTAIN_POS[2])
    #glRotatef(-90, 1, 0, 0)
    #glutSolidCone(MOUNTAIN_RADIUS, MOUNTAIN_HEIGHT, 20, 20)
    #glPopMatrix()

# Draw falling rocks
def draw_rocks():
    glColor3f(0.3, 0.3, 0.3)  # Gray rocks
    for rock in rocks:
        glPushMatrix()
        glTranslatef(rock["x"], rock["y"], rock["z"])
        glutSolidSphere(0.3, 10, 10)
        glPopMatrix()

# Draw watering gauge
def draw_gauge():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Background bar
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(750, 700)
    glVertex2f(970, 700)
    glVertex2f(970, 730)
    glVertex2f(750, 730)
    glEnd()

    # Fill bar
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
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)  # 2D overlay
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Minimap background (bottom-left)
    glColor4f(0.1, 0.1, 0.1, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(10, 10)
    glVertex2f(160, 10)
    glVertex2f(160, 160)
    glVertex2f(10, 160)
    glEnd()

    # Ground area
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(20, 20)
    glVertex2f(150, 20)
    glVertex2f(150, 150)
    glVertex2f(20, 150)
    glEnd()

    # Mountain
    # glColor3f(0.5, 0.35, 0.25)
    # map_x = 20 + (MOUNTAIN_POS[0] + ENV_SIZE/2) * 130/ENV_SIZE
    # map_y = 20 + (MOUNTAIN_POS[2] + ENV_SIZE/2) * 130/ENV_SIZE  # no flip
    # glBegin(GL_QUADS)
    # glVertex2f(map_x-8, map_y-8)
    # glVertex2f(map_x+8, map_y-8)
    # glVertex2f(map_x+8, map_y+8)
    # glVertex2f(map_x-8, map_y+8)
    # glEnd()

    # Dragon
    # glColor3f(0.7, 0.1, 0.1)
    # glBegin(GL_QUADS)
    # glVertex2f(map_x-3, map_y-3)
    # glVertex2f(map_x+3, map_y-3)
    # glVertex2f(map_x+3, map_y+3)
    # glVertex2f(map_x-3, map_y+3)
    # glEnd()

    # Trees
    glColor3f(0.4, 0.2, 0.1)
    for x, z in trees:
        map_x = 20 + (x + ENV_SIZE/2) * 130/ENV_SIZE
        map_y = 20 + (z + ENV_SIZE/2) * 130/ENV_SIZE  # no flip
        glBegin(GL_QUADS)
        glVertex2f(map_x-2, map_y-2)
        glVertex2f(map_x+2, map_y-2)
        glVertex2f(map_x+2, map_y+2)
        glVertex2f(map_x-2, map_y+2)
        glEnd()

    # Player
    map_x = 20 + (player["x"] + ENV_SIZE/2) * 130/ENV_SIZE
    map_y = 20 + (player["z"] + ENV_SIZE/2) * 130/ENV_SIZE  # no flip
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(map_x-3, map_y-3)
    glVertex2f(map_x+3, map_y-3)
    glVertex2f(map_x+3, map_y+3)
    glVertex2f(map_x-3, map_y+3)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def init_riddles():
    global current_riddle, current_answer, scrambled_tiles, riddle_attempts, riddle_score, riddle_tiles
    
    riddles = [
        {
            "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?",
            "answer": "ECHO"
        },
        {
            "question": "The more you take, the more you leave behind. What am I?",
            "answer": "FOOTSTEPS"
        },
        {
            "question": "What has keys but can't open locks?",
            "answer": "PIANO"
        }
    ]
    
    # Select a random riddle
    riddle = random.choice(riddles)
    current_riddle = riddle["question"]
    current_answer = riddle["answer"]
    
    # Scramble the answer
    scrambled = list(current_answer)
    random.shuffle(scrambled)
    scrambled_tiles = scrambled
    selected_tiles = []
    riddle_attempts = 0
    riddle_score = 0
    
    # Position tiles in the world around the player
    riddle_tiles = []
    angle_step = 360 / len(scrambled_tiles)
    radius = 3.0  # Distance from player
    
    for i, letter in enumerate(scrambled_tiles):
        angle = math.radians(i * angle_step)
        x = player["x"] + radius * math.cos(angle)
        z = player["z"] + radius * math.sin(angle)
        riddle_tiles.append({"x": x, "z": z, "letter": letter, "collected": False})
    
def check_riddle_answer():
    global riddle_attempts, riddle_score, riddle_active, golden_apples, selected_tiles
    
    player_answer = ''.join(selected_tiles)
    if player_answer == current_answer:
        # Correct answer!
        riddle_attempts += 1
        
        # Calculate score based on attempts
        if riddle_attempts == 1:
            riddle_score = 100
            print("Perfect! +100 points!")
        elif riddle_attempts == 2:
            riddle_score = 70
            print("Good! +70 points!")
        else:
            riddle_score = 40
            print("Correct! +40 points!")
        
        # Award apple
        golden_apples += 1
        print(f"You earned a golden apple! Total: {golden_apples}")
        
        # End riddle game
        riddle_active = False
        
    else:
        # Wrong answer
        riddle_attempts += 1
        print(f"Wrong answer. Attempt {riddle_attempts}/3")
        
        if riddle_attempts >= 3:
            print("Failed to solve the riddle. Try watering another tree.")
            riddle_active = False
            selected_tiles = []  # Reset selected tiles
        else:
            # Reset for another attempt
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
        glColor3f(0.8, 0.8, 0.1)  # Yellow tiles
        glutSolidCube(0.5)
        
        # Draw letter on tile (simplified)
        glColor3f(0, 0, 0)
        glRasterPos3f(-0.1, 0.5, 0.1)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(tile["letter"]))
        glPopMatrix()

def set_isometric_camera():
    """
    Sets the camera in isometric view, but centered on the player.
    """
    angle_rad = math.radians(isometric_angle)
    elevation_rad = math.radians(isometric_elevation)
    
    # Calculate camera position relative to the player
    cam_x = player["x"] + camera_distance * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = player["y"] + camera_distance * math.sin(elevation_rad)
    cam_z = player["z"] + camera_distance * math.sin(angle_rad) * math.cos(elevation_rad)
    
    # Look at the player
    gluLookAt(cam_x, cam_y, cam_z,
              player["x"], player["y"], player["z"],  # Look at player
              0, 1, 0)


def check_collision(x,z):
    for tx,tz in trees:
        if math.sqrt((x-tx)**2 + (z-tz)**2) < 1.5:
            return True
    if abs(x) > ENV_SIZE/2-1 or abs(z) > ENV_SIZE/2-1:
        return True
    return False

def check_river_collision():
    if RIVER_X_START <= player["x"] <= RIVER_X_END and RIVER_Z_START <= player["z"] <= RIVER_Z_END:
        return True
    return False

def check_mountain_collision():
    # Check if player is on the mountain
    distance = math.sqrt((player["x"] - MOUNTAIN_POS[0])**2 + (player["z"] - MOUNTAIN_POS[2])**2)
    return distance < MOUNTAIN_RADIUS

def check_rock_collision():
    global lives
    for rock in rocks:
        distance = math.sqrt((player["x"] - rock["x"])**2 + 
                             (player["y"] - rock["y"])**2 + 
                             (player["z"] - rock["z"])**2)
        if distance < 0.8:  # Collision radius
            rocks.remove(rock)
            lives -= 1
            print(f"Hit by a rock! Lives left: {lives}")
            return True
    return False

def check_dragon_collision():
    distance = math.sqrt((player["x"] - dragon_pos[0])**2 + 
                         (player["y"] - dragon_pos[1])**2 + 
                         (player["z"] - dragon_pos[2])**2)
    return distance < 3.0


# ---------------------------
# Input
# ---------------------------
def keyboard(key, x, y):
    global isometric_angle, camera_distance, is_climbing, holding_p, golden_apples, dragon_healed
    key = key.decode('utf-8')
    if key=='\x1b':
        glutLeaveMainLoop()
    elif key=='r':
        player["x"]=0.0
        player["z"]=0.0
        player["y"]=0.0
        is_climbing = False
    elif key=='i':
        camera_distance=max(5.0,camera_distance-2.0)
    elif key=='k':
        camera_distance=min(40.0,camera_distance+2.0)
    elif key=='j':
        isometric_angle=(isometric_angle-5)%360
    elif key=='l':
        isometric_angle=(isometric_angle+5)%360
    elif key=='p':  # Hold P to fill water
        holding_p = True
    elif key=='f':  # Feed dragon
        feed_dragon()
    elif key==' ':  # Space key to climb mountain
        if check_mountain_collision():
            is_climbing = True
            print("Started climbing the mountain!")

    elif key.lower() == 'n':
     if dragon_healed:
        print("Loading next level...")
        # Replace current game with the next level
        next_file = "project2.6.py"  # Path to the next level file
        subprocess.Popen([sys.executable, next_file])
        glutLeaveMainLoop()  # Close current window
     else:
        print("You must heal the dragon first before moving to the next level!")

def keyboard_up(key, x, y):
    global holding_p
    key = key.decode('utf-8')
    if key == 'p':
        holding_p = False
        # If near a tree, water it
        water_plant()

def special_keys(key,x,y):
    global is_climbing
    angle_rad=math.radians(isometric_angle)
    dx=dz=0
    if key==GLUT_KEY_UP:
        dx=0.5*math.sin(angle_rad)
        dz=0.5*math.cos(angle_rad)
    elif key==GLUT_KEY_DOWN:
        dx=-0.5*math.sin(angle_rad)
        dz=-0.5*math.cos(angle_rad)
    elif key==GLUT_KEY_LEFT:
        dx=-0.5*math.cos(angle_rad)
        dz=0.5*math.sin(angle_rad)
    elif key==GLUT_KEY_RIGHT:
        dx=0.5*math.cos(angle_rad)
        dz=-0.5*math.sin(angle_rad)
    
    new_x = player["x"] + dx
    new_z = player["z"] + dz
    
    if not check_collision(new_x, new_z):
        player["x"] = new_x
        player["z"] = new_z
    
    # Check if player is still on mountain after movement
    if is_climbing and not check_mountain_collision():
        is_climbing = False
        player["y"] = 0  # Reset height when leaving mountain
        print("Left the mountain")

# Water a nearby tree
def water_plant():
    global watering_gauge, riddle_active, fruits
    
    # Find the nearest tree
    nearest_tree = None
    min_distance = float('inf')
    
    for x, z in trees:
        distance = math.sqrt((player["x"] - x)**2 + (player["z"] - z)**2)
        if distance < min_distance:
            min_distance = distance
            nearest_tree = (x, z)
    
    # Check if player is near a tree and has enough water
    if min_distance < 2.0:  # Increased range for easier watering
        if watering_gauge >= 10:
            watering_gauge -= 10
            # Start riddle game instead of directly growing fruit
            init_riddles()
            riddle_active = True
            print(f"Riddle: {current_riddle}")
            print("Right-click on tiles in the correct order to solve the riddle!")
        else:
            print("Not enough water to grow fruit! Need at least 10 water.")
    else:
        print("No trees nearby to water!")

    
def update_watering():
    global watering_gauge
    if holding_p and check_river_collision():
        watering_gauge = min(max_gauge, watering_gauge + 2)  # Increase gauge while holding
    elif not holding_p and watering_gauge > 0:
        watering_gauge = max(0, watering_gauge - 1)  # Water spills when not holding P


def update_climbing():
    global is_climbing
    if is_climbing and check_mountain_collision():
        player["y"] = min(player["y"] + climb_speed, MOUNTAIN_HEIGHT - 1)
        # Check if player reached the top
        if player["y"] >= MOUNTAIN_HEIGHT - 2:
            print("Reached the mountain top!")

def update_rocks():
    global rocks, rock_spawn_timer
    current_time = time.time()
    
    # Spawn new rocks only when climbing
    if is_climbing and current_time - rock_spawn_timer > rock_spawn_interval:
        rock_spawn_timer = current_time
        # Spawn rock from random position at top of mountain
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, MOUNTAIN_RADIUS - 1)
        x = MOUNTAIN_POS[0] + radius * math.cos(angle)
        z = MOUNTAIN_POS[2] + radius * math.sin(angle)
        rocks.append({"x": x, "y": MOUNTAIN_HEIGHT, "z": z, "speed": random.uniform(0.2, 0.4)})
    
    # Update existing rocks
    for rock in rocks[:]:
        rock["y"] -= rock["speed"]
        # Remove rocks that hit the ground
        if rock["y"] <= 0:
            rocks.remove(rock)
def feed_dragon():
    global golden_apples, dragon_healed
    distance = math.sqrt((player["x"] - dragon_pos[0])**2 + 
                         (player["y"] - dragon_pos[1])**2 + 
                         (player["z"] - dragon_pos[2])**2)
    if distance < 3.0:
        if golden_apples > 0:
            golden_apples -= 1
            dragon_healed = True
            print("Dragon healed! Thank you for the golden apple!")
        else:
            print("You have no golden apples to feed the dragon!")
    else:
        print("You are too far from the dragon to feed it!")

# ---------------------------
# Display
# ---------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glClearColor(0.5, 0.7, 0.9, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Disable lighting
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)  # Keep this to allow glColor to work

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    set_isometric_camera()

    # Environment
    draw_ground()
    draw_river()
    #draw_mountain()
    draw_trees()
    draw_fruits()
    draw_rocks()

    update_watering()
    update_climbing()
    update_rocks()
    check_rock_collision()
    check_dragon_collision()

    # Player
    draw_player()

    # Dragon
    draw_dragon()

    # HUD
    glDisable(GL_DEPTH_TEST)
    draw_minimap()
    draw_gauge()

    # Status text
    draw_text(10, 770, f"Apples: {golden_apples} | Lives: {lives} | Water: {watering_gauge}")
    
    if dragon_healed:
        draw_text(10, 740, "Dragon healed! Quest complete! ")
    
    if is_climbing:
        draw_text(10, 710, "Climbing mountain - watch for falling rocks!")
    
    if check_river_collision():
        draw_text(10, 680, "Standing in river - collecting water!")
    
    # Check if player is near dragon
    dragon_distance = math.sqrt((player["x"] - dragon_pos[0])**2 + 
                                (player["y"] - dragon_pos[1])**2 + 
                                (player["z"] - dragon_pos[2])**2)
    if dragon_distance < 5.0:
        if golden_apples > 0:
            draw_text(10, 650, "Press F to feed dragon a golden apple!")
        else:
            draw_text(10, 650, "Dragon needs golden apples to heal!")
    
    glEnable(GL_DEPTH_TEST)
    
    # FIX THIS PART - the if statement should be inside the function
    if riddle_active:
        draw_riddle_tiles()
        
        # Draw riddle UI
        glDisable(GL_DEPTH_TEST)
        draw_text(300, 400, f"RIDDLE: {current_riddle}")
        draw_text(300, 370, f"Your answer: {''.join(selected_tiles)}")
        draw_text(300, 340, f"Attempts: {riddle_attempts}/3")
        draw_text(300, 310, "Right-click on tiles in correct order!")
        glEnable(GL_DEPTH_TEST)
    
    glutSwapBuffers()

def mouse(button, state, x, y):
    global selected_tiles, riddle_attempts, riddle_score, riddle_active, golden_apples, fruit
    if riddle_active and button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Convert screen coordinates to world coordinates
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Get modelview and projection matrices
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        # Convert mouse Y coordinate to OpenGL coordinates
        y = viewport[3] - y
        
        # Get world coordinates under mouse
        near_point = gluUnProject(x, y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(x, y, 1.0, modelview, projection, viewport)
        
        glPopMatrix()
        
        # Check if player clicked on a tile
        for tile in riddle_tiles:
            if tile["collected"]:
                continue
                
            # Simple distance check (could be improved with ray casting)
            dx = tile["x"] - player["x"]
            dz = tile["z"] - player["z"]
            distance = math.sqrt(dx*dx + dz*dz)
            
            if distance < 2.0:  # If player is close to tile
                selected_tiles.append(tile["letter"])
                tile["collected"] = True
                print(f"Selected: {''.join(selected_tiles)}")
                
                # Check if answer is complete
                if len(selected_tiles) == len(current_answer):
                    check_riddle_answer()
                break

# ---------------------------
# Main
# ---------------------------
def main():
    global quad
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W,WINDOW_H)
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
    print("Space: Climb mountain (when near)")
    print("P: Collect water (in river) or water plants")
    print("I/K: Zoom camera In/Out")
    print("J/L: Rotate camera view")
    print("R: Reset player position")
    print("ESC: Quit game")
    print("\nGAMEPLAY:")
    print("1. Go to the river (blue area) and press P to collect water")
    print("2. Find trees and press P near them to water and grow golden apples")
    print("3. Climb the mountain (center) to reach the dragon")
    print("4. Feed golden apples to the dragon to heal it!")
    print("5. Watch out for falling rocks while climbing!")
    print("\nGOOD LUCK, HERO!")

    glutMainLoop()
    
if __name__=="__main__":
    main()
