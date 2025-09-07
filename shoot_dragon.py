from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
import sys

# Define GLUT_BITMAP_HELVETICA_18 for compatibility
try:
    GLUT_BITMAP_HELVETICA_18
except NameError:
    GLUT_BITMAP_HELVETICA_18 = None

# ---------------------------
# Window config
# ---------------------------
WINDOW_W, WINDOW_H = 1000, 800

# ---------------------------
# Environment config
# ---------------------------
ENV_SIZE = 30.0
RIVER_X_END = -ENV_SIZE/2 + 3 # Width of river

# ---------------------------
# River
# ---------------------------
RIVER_X_START = -ENV_SIZE/2
RIVER_X_END = -ENV_SIZE/2 + 3  # Width of river
RIVER_Z_START = -ENV_SIZE/2
RIVER_Z_END = ENV_SIZE/2
    y = random.uniform(3, 8) # Flying height
# Dragon positions
dragons = []
for _ in range(DRAGON_COUNT):
        (0.1, 0.7, 0.1),  # Green
        (0.1, 0.1, 0.7),  # Blue
        (0.8, 0.8, 0.1),  # Yellow
        (0.7, 0.1, 0.7),  # Purple
        (0.1, 0.7, 0.7)   # Cyan
    colors = [
        (0.1, 0.7, 0.1),   # Green
        (0.1, 0.1, 0.7),   # Blue
        (0.8, 0.8, 0.1),   # Yellow
        (0.7, 0.1, 0.7),   # Purple
        (0.1, 0.7, 0.7)    # Cyan
    ]
    color = colors[len(dragons) % len(colors)]
    
    dragons.append({
        "x": x, 
        "z": z,
        "y": y,
        "color": color,
        "health": 100,
        "fire_cooldown": random.uniform(2, 5),
        "last_fire": 0,
        "speed": random.uniform(0.5, 1.5)
    })

# ---------------------------
# Fireballs
# ---------------------------
fireballs = []
player_fireballs = []

# ---------------------------
# Camera & Isometric view
# ---------------------------
isometric_angle = 45
player = {"x": 0.0, "z": 0.0, "yaw": 0.0, "y": 0.0} # y = height
camera_distance = 20.0

# ---------------------------
# Player
# ---------------------------
player = {"x": 0.0, "z": 0.0, "yaw": 0.0, "y": 0.0}  # y = height
m_speed = 0.5
player_fire_cooldown = 0.5
player_last_fire = 0

# ---------------------------
# Game state
# ---------------------------
lives = 3
all_dragons_dead = False
game_over = False

# ---------------------------
# GL quadric
# ---------------------------
quad = None

# ---------------------------
# Drawing functions
# ---------------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen in 2D overlay."""
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
    """Draws the green ground plane and grid lines."""
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
    glTranslatef(dragon["x"], dragon["y"], dragon["z"]) # dragon position

def draw_dragon(dragon, scale=1.0):
    """Draws a dragon model at its position."""
    global quad
    glPushMatrix()
    glTranslatef(dragon["x"], dragon["y"], dragon["z"])  # dragon position
    glScalef(scale, scale, scale)
    glScalef(1.2, 0.8, 2.0) # width, height, depth
    # Use the dragon's assigned color
    glColor3f(*dragon["color"])

    # Main body
    glPushMatrix()
    glScalef(1.2, 0.8, 2.0)  # width, height, depth
    glutSolidCube(1.0)
    glPopMatrix()

    # Neck and head
    glPushMatrix()
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
    glColor3f(dragon["color"][0] + 0.2, dragon["color"][1] + 0.2, dragon["color"][2] + 0.2)
    glTranslatef(0, 0.1, 1.3)
    glRotatef(-30, 1, 0, 0)
    glScalef(0.3, 0.3, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Horns
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glTranslatef(-0.2, 0.4, 1.0)
    glPopMatrix() # End of neck/head group
    glutSolidCone(0.08, 0.3, 10, 10)
    glTranslatef(0.4, 0, 0)
    glutSolidCone(0.08, 0.3, 10, 10)
    glPopMatrix()
    
    glPopMatrix()  # End of neck/head group

    # Tail
    glPushMatrix()
    glTranslatef(0, 0.2, -1.2)
    glRotatef(180, 0, 1, 0)
    glutSolidCone(0.3, 1.2, 12, 12)
    glPopMatrix()

    # Wings
    glPushMatrix()
    
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

    # Legs with claws
    # Front left leg
    glPushMatrix()
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
    glColor3f(1, 1, 1) # White part
    glPopMatrix()
    glPopMatrix()

    # Eyes
    glPushMatrix()
    glColor3f(1, 1, 1)  # White part
    glColor3f(0, 0, 0) # Black pupils
    glutSolidSphere(0.1, 12, 12)
    glTranslatef(0.6, 0, 0)
    glutSolidSphere(0.1, 12, 12)
    
    # Pupils
    glColor3f(0, 0, 0)  # Black pupils
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

def draw_gun():
    """Draws a simple gun model."""
    global quad
    # Gun barrel
    glColor3f(0.3, 0.3, 0.3) 
    glPushMatrix()
    glTranslatef(0.15, 0.4, 0.3)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 0.05, 0.05, 0.5, 12, 1)
    glPopMatrix()
    
    # Gun handle
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0.15, 0.2, 0.3)
    glRotatef(-90, 1, 0, 0)
    glScalef(0.1, 0.1, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Gun body
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0.15, 0.25, 0.4)
    glScalef(0.1, 0.2, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    glRotatef(player["yaw"], 0, 1, 0) # Rotate the player model
def draw_player():
    """Draws the player model with a gun."""
    glColor3f(0.2, 0.6, 0.8)
    glPushMatrix()
    glTranslatef(player["x"], player["y"], player["z"])
    glRotatef(player["yaw"], 0, 1, 0)  # Rotate the player model

    # Body
    glColor3f(0.2, 0.6, 0.8)  
    glColor3f(1.0, 0.8, 0.6)
    glScalef(0.5, 1.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # Head
    glColor3f(1.0, 0.8, 0.6)  
    glPushMatrix()
    glTranslatef(0, 0.75, 0)
    glutSolidSphere(0.25, 20, 20)
    glPopMatrix()

    # Eyes
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(-0.1, 0.85, 0.12)
    glColor3f(0.2, 0.2, 0.6)
    glTranslatef(0.2, 0, 0)
    glutSolidSphere(0.05, 10, 10)
    glPopMatrix()

    # Legs
    glColor3f(0.2, 0.2, 0.6)  
    for offset in [-0.15, 0.15]:
        glPushMatrix()
        glTranslatef(offset, -0.75, 0)
        glScalef(0.1, 0.5, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

    # Hands
    glColor3f(1.0, 0.8, 0.6)  
    # Right hand holding the gun
    glPushMatrix()
    glTranslatef(0.15, 0.25, 0.2)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(quad, 0.08, 0.08, 0.4, 12, 1)
    glPopMatrix()
    # Left hand
    glPushMatrix()
    glTranslatef(-0.3, 0.25, 0)
    glColor3f(0.8, 0.1, 0.1)
    glRotatef(-20, 1, 0, 0)
    gluCylinder(quad, 0.08, 0.08, 0.4, 12, 1)
    glPopMatrix()

    # Cape
    glColor3f(0.8, 0.1, 0.1)  
    glPushMatrix()
    glTranslatef(0, 0, -0.2)
    glRotatef(10, 1, 0, 0)
    glScalef(0.6, 1.0, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw the gun as a separate part
    glColor3f(0.0, 0.4, 0.8) # Blue water

    glPopMatrix()

def draw_river():
    """Draws the river on the ground."""
    glColor3f(0.0, 0.4, 0.8)  # Blue water
    glBegin(GL_QUADS)
    glVertex3f(RIVER_X_START, 0.01, RIVER_Z_START)
    glVertex3f(RIVER_X_END, 0.01, RIVER_Z_START)
    glVertex3f(RIVER_X_END, 0.01, RIVER_Z_END)
    glVertex3f(RIVER_X_START, 0.01, RIVER_Z_END)
    glEnd()
        glColor3f(1.0, 0.3, 0.1) # Orange-red dragon fireball
def draw_fireballs():
    """Draws the fireballs for both dragons and player."""
    for fireball in fireballs:
        glPushMatrix()
        glTranslatef(fireball["x"], fireball["y"], fireball["z"])
        glColor3f(1.0, 0.3, 0.1)  # Orange-red dragon fireball
        glColor3f(0.1, 0.8, 0.1) # Green player projectile
        glPopMatrix()
    
    for fireball in player_fireballs:
        glPushMatrix()
        glTranslatef(fireball["x"], fireball["y"], fireball["z"])
        glColor3f(0.1, 0.8, 0.1)  # Green player projectile
        glutSolidSphere(0.2, 10, 10)
        glPopMatrix()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H) # 2D overlay
def draw_minimap():
    """Draws a minimap overlay on the bottom left."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)  # 2D overlay
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Minimap background
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
    if dragon["health"] > 0: # Only show living dragons
       glVertex2f(20, 150)
    glEnd()

    # Dragons
    for i, dragon in enumerate(dragons):
        if dragon["health"] > 0:  # Only show living dragons
            map_x = 20 + (dragon["x"] + ENV_SIZE/2) * 130/ENV_SIZE
            map_y = 20 + (dragon["z"] + ENV_SIZE/2) * 130/ENV_SIZE
            glColor3f(*dragon["color"])
            glBegin(GL_QUADS)
            glVertex2f(map_x-3, map_y-3)
            glVertex2f(map_x+3, map_y-3)
            glVertex2f(map_x+3, map_y+3)
            glVertex2f(map_x-3, map_y+3)
            glEnd()

    # Player
    map_x = 20 + (player["x"] + ENV_SIZE/2) * 130/ENV_SIZE
    map_y = 20 + (player["z"] + ENV_SIZE/2) * 130/ENV_SIZE
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
              player["x"], player["y"], player["z"], 
              0, 1, 0)

def check_collision(x,z):
    """Checks for collision with environment bounds."""
    if abs(x) > ENV_SIZE/2-1 or abs(z) > ENV_SIZE/2-1:
        return True
    return False

def check_river_collision():
    """Checks if the player is in the river."""
    if RIVER_X_START <= player["x"] <= RIVER_X_END and RIVER_Z_START <= player["z"] <= RIVER_Z_END:
        return True
    return False

def check_fireball_collision():
    """Checks for collisions between fireballs and the player/dragons."""
    global lives, game_over, all_dragons_dead
        if distance < 1.0: # Collision radius
    # Check if player is hit by dragon fireballs
    for fireball in fireballs[:]:
        distance = math.sqrt((player["x"] - fireball["x"])**2 + 
                             (player["y"] - fireball["y"])**2 + 
                             (player["z"] - fireball["z"])**2)
        if distance < 1.0:  # Collision radius
            fireballs.remove(fireball)
            lives -= 1
            print(f"Hit by a fireball! Lives left: {lives}")
            if lives <= 0:
                game_over = True
            if dragon["health"] > 0: # Only check living dragons
            return True
    
    # Check if player fireballs hit dragons
                if distance < 2.0: # Collision radius
                    dragon["health"] -= 25 # Reduce dragon health
            if dragon["health"] > 0:  # Only check living dragons
                distance = math.sqrt((dragon["x"] - fireball["x"])**2 + 
                                     (dragon["y"] - fireball["y"])**2 + 
                                     (dragon["z"] - fireball["z"])**2)
                if distance < 2.0:  # Collision radius
                    dragon["health"] -= 25  # Reduce dragon health
                    if fireball in player_fireballs:
                        player_fireballs.remove(fireball)
                    print(f"Dragon hit! Health: {dragon['health']}%")
                    
                    if dragon["health"] <= 0:
                        print("Dragon defeated!")
                    
                    all_dragons_dead = all(d["health"] <= 0 for d in dragons)
                    return True
    return False

# ---------------------------
# Input
# ---------------------------
def keyboard(key, x, y):
    """Handles keyboard input for player actions."""
    global isometric_angle, camera_distance, player_last_fire, game_over
    try:
        key_char = key.decode('utf-8')
    except UnicodeDecodeError:
        key_char = ''
    
    if key_char=='\x1b':
        glutLeaveMainLoop()
    elif key_char=='r':
        player["x"]=0.0
        player["z"]=0.0
        player["y"]=0.0
    elif key_char=='i':
        camera_distance=max(5.0,camera_distance-2.0)
    elif key_char==' ': # Space key to shoot
        camera_distance=min(40.0,camera_distance+2.0)
    elif key_char=='j':
        isometric_angle=(isometric_angle-5)%360
    elif key_char=='l':
        isometric_angle=(isometric_angle+5)%360
    elif key_char==' ':  # Space key to shoot
        current_time = time.time()
        if current_time - player_last_fire > player_fire_cooldown and not game_over:
            player_last_fire = current_time
            # Create a fireball from the player's gun
            angle_rad = math.radians(isometric_angle)
            player_fireballs.append({
                "x": player["x"] + 0.15 * math.cos(angle_rad) * 0.5,
                "y": player["y"] + 0.25, # Gun height
                "z": player["z"] - 0.15 * math.sin(angle_rad) * 0.5,
                "dx": math.cos(angle_rad) * 1.5,
                "dz": -math.sin(angle_rad) * 1.5,
                "dy": 0.1  # Slight upward trajectory
            })
            print("Player fired!")

def special_keys(key,x,y):
    """Handles special key input for movement."""
    if game_over:
        return
    angle_rad=math.radians(isometric_angle)
    dx=dz=0
    # The direction of movement is now corrected to feel natural with the camera angle.
    if key==GLUT_KEY_UP:
        dx = m_speed * math.cos(angle_rad)
        dz = -m_speed * math.sin(angle_rad)
    elif key==GLUT_KEY_DOWN:
        dx = -m_speed * math.cos(angle_rad)
        dz = m_speed * math.sin(angle_rad)
    elif key==GLUT_KEY_LEFT:
        dx = -m_speed * math.sin(angle_rad)
        dz = -m_speed * math.cos(angle_rad)
    elif key==GLUT_KEY_RIGHT:
        dx = m_speed * math.sin(angle_rad)
        dz = m_speed * math.cos(angle_rad)
    
    new_x = player["x"] + dx
    new_z = player["z"] + dz
    
    if not check_collision(new_x, new_z):
        player["x"] = new_x
        player["z"] = new_z
        # Also update player yaw for model rotation
        player["yaw"] = -math.degrees(math.atan2(-dz, dx)) if (dx or dz) else player["yaw"]

        if dragon["health"] > 0: # Only update living dragons
    """Updates dragon positions and makes them fire at the player."""
    global fireballs
    current_time = time.time()
    
    for dragon in dragons:
        if dragon["health"] > 0:  # Only update living dragons
            # Move dragon randomly
            dragon["x"] += random.uniform(-0.1, 0.1) * dragon["speed"]
            dragon["z"] += random.uniform(-0.1, 0.1) * dragon["speed"]
            dragon["y"] += random.uniform(-0.05, 0.05) * dragon["speed"]
            
            # Keep dragon within bounds
            dragon["x"] = max(-ENV_SIZE/2 + 2, min(ENV_SIZE/2 - 2, dragon["x"]))
            dragon["z"] = max(-ENV_SIZE/2 + 2, min(ENV_SIZE/2 - 2, dragon["z"]))
            dragon["y"] = max(3, min(8, dragon["y"]))
            
            # Fire at player if cooldown is over
            if current_time - dragon["last_fire"] > dragon["fire_cooldown"]:
                dragon["last_fire"] = current_time
                
                # Calculate direction to player
                dx = player["x"] - dragon["x"]
                dz = player["z"] - dragon["z"]
                dy = player["y"] - dragon["y"]
                dist = math.sqrt(dx*dx + dz*dz + dy*dy)
                
                if dist > 0:  # Avoid division by zero
                    dx /= dist
                    dz /= dist
                    dy /= dist
                    
                    fireballs.append({
                        "x": dragon["x"],
                        "y": dragon["y"],
                        "z": dragon["z"],
                        "dx": dx * 1.0,
                        "dz": dz * 1.0,
                        "dy": dy * 1.0
                    })

def update_fireballs():
    """Updates the position of all fireballs."""
    # Update dragon fireballs
    for fireball in fireballs[:]:
        fireball["x"] += fireball["dx"]
        fireball["y"] += fireball["dy"]
        fireball["z"] += fireball["dz"]
        
        # Remove fireballs that go out of bounds
        if (abs(fireball["x"]) > ENV_SIZE or 
            abs(fireball["z"]) > ENV_SIZE or
            fireball["y"] < 0 or fireball["y"] > 15):
            fireballs.remove(fireball)
    
    # Update player fireballs
    for fireball in player_fireballs[:]:
        fireball["x"] += fireball["dx"]
        fireball["y"] += fireball["dy"]
        fireball["z"] += fireball["dz"]
        
        # Remove fireballs that go out of bounds
        if (abs(fireball["x"]) > ENV_SIZE or 
            abs(fireball["z"]) > ENV_SIZE or
            fireball["y"] < 0 or fireball["y"] > 15):
            player_fireballs.remove(fireball)

# ---------------------------
# Display
# ---------------------------
def display():
    """Main display loop function."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glClearColor(0.5, 0.7, 0.9, 1.0)
    glEnable(GL_DEPTH_TEST)

    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    set_isometric_camera()

    # Environment
    draw_ground()
    draw_river()

    # Update game elements
    if not game_over and not all_dragons_dead:
        update_dragons()
        update_fireballs()
        check_fireball_collision()

    # Draw all dragons
    for dragon in dragons:
        if dragon["health"] > 0:
            draw_dragon(dragon)

    # Draw fireballs
    draw_fireballs()

    # Player
    draw_player()

    # HUD
    glDisable(GL_DEPTH_TEST)
    draw_minimap()

    # Status text
    defeated_count = sum(1 for dragon in dragons if dragon["health"] <= 0)
    draw_text(10, 770, f"Lives: {lives} | Dragons: {defeated_count}/{DRAGON_COUNT}")
    
    global all_dragons_dead
    all_dragons_dead = all(dragon["health"] <= 0 for dragon in dragons)
    
    if all_dragons_dead:
        draw_text(WINDOW_W/2 - 150, WINDOW_H/2, "You defeated all dragons! Quest complete!")
    
    if game_over:
        draw_text(WINDOW_W/2 - 100, WINDOW_H/2, "GAME OVER! You were defeated by the dragons.")
    
    if check_river_collision():
        draw_text(10, 710, "Standing in river")
    
    glEnable(GL_DEPTH_TEST)
    
    glutSwapBuffers()

# ---------------------------
# Main
# ---------------------------
def main():
    """Initializes and runs the game loop."""
    global quad
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W,WINDOW_H)
    glutCreateWindow(b"Dragon Battle: Defeat the Dragons!")
    quad = gluNewQuadric()

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)

    print("DRAGON BATTLE GAME")
    print("=" * 40)
    print("CONTROLS:")
    print("Arrow Keys: Move around")
    print("Space: Shoot at dragons")
    print("I/K: Zoom camera In/Out")
    print("J/L: Rotate camera view")
    print("R: Reset player position")
    print("ESC: Quit game")
    print("\nGAMEPLAY:")
    print("1. Dodge the fireballs shot by dragons")
    print("2. Shoot back at dragons to defeat them")
    print("3. Defeat all dragons to complete the quest")
    print(f"4. You have {lives} lives - don't get hit by too many fireballs!")
    print("\nGOOD LUCK, DRAGON SLAYER!")

    glutMainLoop()
    
if __name__=="__main__":
    main()
