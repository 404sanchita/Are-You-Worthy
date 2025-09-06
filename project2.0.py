from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# ---------------------------
# Window config
# ---------------------------
WINDOW_W, WINDOW_H = 1000, 800

# ---------------------------
# Environment config
# ---------------------------
ENV_SIZE = 30.0
TREE_COUNT = 20

trees = []
for _ in range(TREE_COUNT):
    x = random.uniform(-ENV_SIZE/2 + 2, ENV_SIZE/2 - 2)
    z = random.uniform(-ENV_SIZE/2 + 2, ENV_SIZE/2 - 2)
    trees.append((x, z))

# ---------------------------
# River & watering system
# ---------------------------
RIVER_X_START = -ENV_SIZE/2
RIVER_X_END = -ENV_SIZE/2 + 3  # Width of river
RIVER_Z_START = -ENV_SIZE/2
RIVER_Z_END = ENV_SIZE/2
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
max_gauge = 100
golden_apples = 0
lives = 3
dragon_healed = False

# ---------------------------
# Dragon
# ---------------------------
dragon_pos = [MOUNTAIN_POS[0], MOUNTAIN_HEIGHT, MOUNTAIN_POS[2]]
dragon_healed = False

# ---------------------------
# Mountain
# ---------------------------
MOUNTAIN_HEIGHT = 15
MOUNTAIN_RADIUS = 8
MOUNTAIN_POS = [10, 0, 5]

# ---------------------------
# Dragon
# ---------------------------
dragon_pos = [MOUNTAIN_POS[0], MOUNTAIN_HEIGHT, MOUNTAIN_POS[2]]
dragon_healed = False
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

    # Body (green)
    glPushMatrix()
    glColor3f(0.2, 0.6, 0.8)  # Blue body
    glScalef(0.5, 1.0, 0.3)  # width, height, depth
    glutSolidCube(1.0)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(1, 0.8, 0.6)  # Skin tone
    glTranslatef(0, 0.75 + 0.25, 0)  # above body
    glutSolidSphere(0.25, 20, 20)
    glPopMatrix()

    # Eyes
    glPushMatrix()
    glColor3f(0, 0, 0)  # Black eyes
    glTranslatef(-0.1, 0.9, 0.15)
    glutSolidSphere(0.05, 10, 10)
    glTranslatef(0.2, 0, 0)
    glutSolidSphere(0.05, 10, 10)
    glPopMatrix()

    # Enhanced Legs with knees and feet
    # Left leg
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.6)  # Dark blue legs
    glTranslatef(-0.15, -0.25, 0)
    
    # Upper leg
    glPushMatrix()
    glScalef(0.1, 0.4, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Lower leg
    glPushMatrix()
    glTranslatef(0, -0.4, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Foot
    glPushMatrix()
    glTranslatef(0, -0.6, 0.05)
    glScalef(0.1, 0.05, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

    # Right leg
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.6)  # Dark blue legs
    glTranslatef(0.15, -0.25, 0)
    
    # Upper leg
    glPushMatrix()
    glScalef(0.1, 0.4, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Lower leg
    glPushMatrix()
    glTranslatef(0, -0.4, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Foot
    glPushMatrix()
    glTranslatef(0, -0.6, 0.05)
    glScalef(0.1, 0.05, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

    # Hands (skin-colored cylinders)
    glPushMatrix()
    glColor3f(1, 0.8, 0.6)
    glTranslatef(-0.35, 0.25, 0)  # left hand
    glRotatef(-90, 0, 0, 1)
    gluCylinder(quad, 0.08, 0.08, 0.4, 12, 1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1, 0.8, 0.6)
    glTranslatef(0.35, 0.25, 0)  # right hand
    glRotatef(90, 0, 0, 1)
    gluCylinder(quad, 0.08, 0.08, 0.4, 12, 1)
    glPopMatrix()

    # Cape
    glPushMatrix()
    glColor3f(0.8, 0.1, 0.1)  # Red cape
    glTranslatef(0, -0.2, -0.1)
    glScalef(0.6, 0.8, 0.05)
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
def draw_mountain():
    glColor3f(0.5, 0.35, 0.25)  # Brown mountain
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(MOUNTAIN_RADIUS, MOUNTAIN_HEIGHT, 20, 20)
    glPopMatrix()

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
    glVertex2f(50, 700)
    glVertex2f(350, 700)
    glVertex2f(350, 730)
    glVertex2f(50, 730)
    glEnd()

    # Fill bar
    glColor3f(0, 1, 0)
    fill = min(watering_gauge * 3, 300)
    glBegin(GL_QUADS)
    glVertex2f(50, 700)
    glVertex2f(50 + fill, 700)
    glVertex2f(50 + fill, 730)
    glVertex2f(50, 730)
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

    # Minimap background
    glColor4f(0.1,0.1,0.1,0.7)
    glBegin(GL_QUADS)
    glVertex2f(10, WINDOW_H-10)
    glVertex2f(160, WINDOW_H-10)
    glVertex(160, WINDOW_H-160)
    glVertex2f(10, WINDOW_H-160)
    glEnd()

    # Ground area
    glColor3f(0.1,0.6,0.1)
    glBegin(GL_QUADS)
    glVertex2f(20, WINDOW_H-20)
    glVertex2f(150, WINDOW_H-20)
    glVertex2f(150, WINDOW_H-150)
    glVertex2f(20, WINDOW_H-150)
    glEnd()

    # Trees
    glColor3f(0.4,0.2,0.1)
    for x,z in trees:
        map_x = 20 + (x + ENV_SIZE/2) * 130/ENV_SIZE
        map_y = WINDOW_H-20-(z+ENV_SIZE/2)*130/ENV_SIZE
        glBegin(GL_QUADS)
        glVertex2f(map_x-2, map_y-2)
        glVertex2f(map_x+2, map_y-2)
        glVertex2f(map_x+2, map_y+2)
        glVertex2f(map_x-2, map_y+2)
        glEnd()

    # Player
    map_x = 20 + (player["x"] + ENV_SIZE/2) * 130/ENV_SIZE
    map_y = WINDOW_H-20-(player["z"] + ENV_SIZE/2)*130/ENV_SIZE
    glColor3f(1,0,0)
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
    distance = math.sqrt(player["x"]**2 + player["z"]**2)
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
            print(f"💥 Hit by a rock! Lives left: {lives}")
            return True
    return False

def check_dragon_collision():
    global golden_apples, dragon_healed
    if golden_apples > 0:
        distance = math.sqrt((player["x"] - dragon_pos[0])**2 + 
                            (player["y"] - dragon_pos[1])**2 + 
                            (player["z"] - dragon_pos[2])**2)
        if distance < 3.0:
            golden_apples -= 1
            dragon_healed = True
            print("🐉 Dragon healed! Thank you for the golden apple!")
            return True
    return False

# ---------------------------
# Input
# ---------------------------
def keyboard(key, x, y):
    global isometric_angle, camera_distance, watering, is_climbing
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
    elif key=='p':  # 'p' to collect or pour water
        if check_river_collision():
            watering = True
            print("💧 Collecting water from river...")
        else:
            watering = False
            water_plant()
    elif key==' ':  # Space to climb
        if check_mountain_collision():
            is_climbing = True
            print("🧗 Climbing the mountain...")

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
    
    player["x"]+=dx
    player["z"]+=dz
    
    if check_collision(player["x"],player["z"]):
        player["x"]-=dx
        player["z"]-=dz
    
    # Check if player is still on mountain after movement
    if is_climbing and not check_mountain_collision():
        is_climbing = False
        print("Left the mountain")

# Water a nearby tree
def water_plant():
    global watering_gauge, golden_apples
    for x, z in trees:
        distance = math.sqrt((player["x"] - x)**2 + (player["z"] - z)**2)
        if distance < 1.5:
            if watering_gauge >= 10:
                watering_gauge -= 10
                fruits[(x, z)] = 1  # Grow fruit
                golden_apples += 1
                print("🌳 Tree flourished! Golden apple grown:", golden_apples)
            else:
                print("💧 Not enough water to grow fruit!")
            break

def update_watering():
    global watering_gauge
    # If player is in the river, collect water gradually
    if check_river_collision():
        watering_gauge = min(max_gauge, watering_gauge + 1)  # increase gauge slowly

def update_climbing():
    global is_climbing
    if is_climbing:
        player["y"] += climb_speed
        # Check if player reached the top
        if player["y"] >= MOUNTAIN_HEIGHT - 1:
            player["y"] = MOUNTAIN_HEIGHT - 1
            is_climbing = False
            print("🏔️ Reached the mountain top!")

def update_rocks():
    global rocks, rock_spawn_timer
    current_time = time.time()
    
    # Spawn new rocks
    if is_climbing and current_time - rock_spawn_timer > rock_spawn_interval:
        rock_spawn_timer = current_time
        # Spawn rock from random position at top of mountain
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, MOUNTAIN_RADIUS)
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        rocks.append({"x": x, "y": MOUNTAIN_HEIGHT, "z": z, "speed": random.uniform(0.1, 0.3)})
    
    # Update existing rocks
    for rock in rocks[:]:
        rock["y"] -= rock["speed"]
        # Remove rocks that hit the ground
        if rock["y"] <= 0:
            rocks.remove(rock)

# ---------------------------
# Display
# ---------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glClearColor(0.5,0.7,0.9,1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glLightfv(GL_LIGHT0,GL_POSITION,[10.0,20.0,10.0,1.0])
    glLightfv(GL_LIGHT0,GL_AMBIENT,[0.3,0.3,0.3,1.0])
    glLightfv(GL_LIGHT0,GL_DIFFUSE,[0.8,0.8,0.8,1.0])

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60,WINDOW_W/float(WINDOW_H),0.1,200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    set_isometric_camera()

    # Environment
    draw_ground()
    draw_river()      # Draw river first (behind trees)
    draw_mountain()   # Draw the mountain
    draw_trees()
    draw_fruits()     # Draw fruits on top of trees
    draw_rocks()      # Draw falling rocks
    
    update_watering()
    update_climbing()
    update_rocks()
    check_rock_collision()
    check_dragon_collision()

    # Player
    glPushMatrix()
    glTranslatef(player["x"], player["y"], player["z"])
    draw_player()
    glPopMatrix()

    # Dragon
    draw_dragon()

    # HUD
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    draw_minimap()
    draw_gauge()  # Draw the watering gauge
    draw_text(10,770,f"Apples: {golden_apples} | Lives: {lives} | Water: {watering_gauge}")
    if dragon_healed:
        draw_text(10,740,"Dragon healed! Maze unlocked ✅")
    if is_climbing:
        draw_text(10,710,"Climbing mountain - watch for rocks!")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glutSwapBuffers()
# ---------------------------
# Main
# ---------------------------
def main():
    global quad
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W,WINDOW_H)
    glutCreateWindow(b"Dragon Quest Prototype - Isometric")
    quad = gluNewQuadric()

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)

    print("Controls:")
    print("Arrow Keys: Move")
    print("Space: Climb mountain")
    print("P: Collect water (in river) or water plants")
    print("I/K: Zoom In/Out")
    print("J/L: Rotate View")
    print("R: Reset Position")
    print("ESC: Quit")
    print("\nGameplay:")
    print("1. Collect water")
    glutMainLoop()

if __name__=="__main__":
    main()