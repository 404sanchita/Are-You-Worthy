from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# ---------------------------
# Window config
# ---------------------------
WINDOW_W, WINDOW_H = 800, 600

# Player
player = {"x": 0.0, "z": 0.0, "orientation": 0.0}
player_score = 0
fireball_hits = 0

# Environment size
ENV_SIZE = 30.0

# Game state
GAME_STATE = "PLAYING" # States: "PLAYING", "WIN", "LOSE"

# Dragon and projectile config
DRAGON_COUNT = 5
dragons = []
fireballs = []
player_projectiles = []
LAST_FIRE_TIME = 0.0
FIRE_INTERVAL = 1.0
MAX_FIREBALL_HITS = 10

# Isometric view settings
isometric_angle = 45 # Degrees for isometric view
isometric_elevation = 30 # Degrees for elevation
camera_distance = 40.0 # Increased distance for better initial view

# ---------------------------
# Drawing Utilities
# ---------------------------

def draw_text(text, x, y, color=(1.0, 1.0, 1.0)):
    """Draws text on the screen at specified coordinates."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(*color)
    glWindowPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_message(text, color=(1.0, 1.0, 1.0)):
    """Draws a centered message on the screen."""
    draw_text(text, WINDOW_W/2 - len(text)*4, WINDOW_H/2, color)

def draw_ground():
    """Draws a grid for the ground."""
    glColor3f(0.1, 0.6, 0.1) # green ground
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

def draw_player():
    """Draws player as a colored cube."""
    glColor3f(1.0, 0.0, 0.0) # red player
    glPushMatrix()
    glTranslatef(player["x"], 0.5, player["z"])
    glRotatef(player["orientation"], 0, 1, 0) # Apply rotation
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

# ---------------------------
# Isometric Camera
# ---------------------------

def set_isometric_camera():
    """Calculates and sets the camera for an isometric view."""
    angle_rad = math.radians(isometric_angle)
    elevation_rad = math.radians(isometric_elevation)
    
    cam_x = camera_distance * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = camera_distance * math.sin(elevation_rad)
    cam_z = camera_distance * math.sin(angle_rad) * math.cos(elevation_rad)
    
    gluLookAt(cam_x, cam_y, cam_z,
              0, 0, 0,
              0, 1, 0)

# ---------------------------
# Game Logic
# ---------------------------

def init_game():
    """Initializes or resets the game state."""
    global GAME_STATE, dragons, fireballs, player_projectiles, player, LAST_FIRE_TIME, player_score, fireball_hits
    GAME_STATE = "PLAYING"
    player_score = 0
    fireball_hits = 0
    dragons = []
    fireballs = []
    player_projectiles = []
    player["x"] = 0.0
    player["z"] = 0.0
    player["orientation"] = 0.0 # Initialize player orientation
    LAST_FIRE_TIME = time.time()
    
    spawn_dragons()

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

def check_collision(pos1, pos2, radius1, radius2):
    """Checks for collision between two circular objects."""
    distance = math.sqrt((pos1["x"] - pos2["x"])**2 + (pos1["z"] - pos2["z"])**2)
    return distance < radius1 + radius2

def update_game_state():
    """Updates the position of all entities and checks for collisions."""
    global fireballs, player_projectiles, dragons, GAME_STATE, LAST_FIRE_TIME, player_score, fireball_hits
    
    if GAME_STATE != "PLAYING":
        return

    # Check for win condition
    if len(dragons) == 0:
        GAME_STATE = "WIN"
        return

    # Check for lose condition (10 fireballs hits)
    if fireball_hits >= MAX_FIREBALL_HITS:
        GAME_STATE = "LOSE"
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
              spawn_fireball(dragons[i], player)
        LAST_FIRE_TIME = time.time()

    # Collision detection
    # Player vs. fireball collision
    fireballs_to_keep = []
    for fb in fireballs:
        if check_collision(player, fb, 0.5, 0.3):
            fireball_hits += 1 # Player hit, increment counter
        else:
            fireballs_to_keep.append(fb)
    fireballs = fireballs_to_keep
    
    # Projectile vs. dragon collision
    projectiles_to_remove = set()
    dragons_to_keep = []
    for i, pp in enumerate(player_projectiles):
        hit = False
        for d in dragons:
            if check_collision(d, pp, 1.0, 0.3):
                player_score += 1 # Dragon hit, increment score
                hit = True
                projectiles_to_remove.add(i)
                dragons.remove(d)
                break
        
    player_projectiles = [pp for i, pp in enumerate(player_projectiles) if i not in projectiles_to_remove]
    
    glutPostRedisplay()


# ---------------------------
# Scene Rendering
# ---------------------------

def display():
    """The main drawing function."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_isometric_camera()

    glClearColor(0.5, 0.7, 0.9, 1.0) # blue sky

    glEnable(GL_DEPTH_TEST)

    draw_ground()
    draw_player()
    draw_entities()
    
    glDisable(GL_DEPTH_TEST)
    
    # Display UI elements
    if GAME_STATE == "PLAYING":
        draw_text("Score: " + str(player_score), 10, WINDOW_H - 50)
        draw_text("Hits Taken: " + str(fireball_hits) + " / " + str(MAX_FIREBALL_HITS), 10, WINDOW_H - 70)
        draw_text("Dragons left: " + str(len(dragons)), 10, WINDOW_H - 30)
        draw_text("Space: Shoot | Arrow Keys: Move | I/K: Zoom | J/L: Rotate | U: Turn 90 | R: Reset", 10, 10)
    elif GAME_STATE == "WIN":
        draw_message("You Win!")
        draw_text("Final Score: " + str(player_score), WINDOW_W/2 - 50, WINDOW_H/2 - 40)
        draw_text("Press 'R' to restart", WINDOW_W/2 - 50, WINDOW_H/2 - 60)
    elif GAME_STATE == "LOSE":
        draw_message("Game Over")
        draw_text("Final Score: " + str(player_score), WINDOW_W/2 - 50, WINDOW_H/2 - 40)
        draw_text("Press 'R' to restart", WINDOW_W/2 - 50, WINDOW_H/2 - 60)
    
    glutSwapBuffers()

# ---------------------------
# Controls & Movement
# ---------------------------

def keyboard(key, x, y):
    """Handles keyboard key presses."""
    global isometric_angle, camera_distance, player_projectiles, GAME_STATE
    
    key_str = key.decode('utf-8')
    if key_str == '\x1b': # Esc
        glutLeaveMainLoop()
    elif key_str == 'r': # Reset
        init_game()
    elif GAME_STATE == "PLAYING":
        if key_str == 'i': # Zoom in
            camera_distance = max(5.0, camera_distance - 2.0)
        elif key_str == 'k': # Zoom out
            camera_distance = min(40.0, camera_distance + 2.0)
        elif key_str == 'j': # Rotate left
            isometric_angle = (isometric_angle - 5) % 360
        elif key_str == 'l': # Rotate right
            isometric_angle = (isometric_angle + 5) % 360
        elif key_str == 'u': # Turn 90 degrees
            player["orientation"] = (player["orientation"] + 90) % 360
        elif key_str == 'h': #shoot
            # Calculate projectile velocity based on player orientation
            angle_rad = math.radians(player["orientation"] - 90) # Adjust for initial orientation
            
            # The -90 degree adjustment is needed because the player's initial
            # orientation (0 degrees) corresponds to shooting along the negative
            # z-axis in the isometric view.
            
            vx = math.cos(angle_rad) * 0.5
            vz = math.sin(angle_rad) * 0.5
            
            player_projectiles.append({
                "x": player["x"],
                "z": player["z"],
                "vx": vx,
                "vz": vz
            })

    glutPostRedisplay()

def special_keys(key, x, y):
    """Handles special key presses (arrow keys)."""
    if GAME_STATE != "PLAYING":
        return
    
    move_speed = 0.5
    
    if key == GLUT_KEY_UP:
        player["z"] = max(-ENV_SIZE/2 + 1, player["z"] - move_speed)
    elif key == GLUT_KEY_DOWN:
        player["z"] = min(ENV_SIZE/2 - 1, player["z"] + move_speed)
    elif key == GLUT_KEY_LEFT:
        player["x"] = max(-ENV_SIZE/2 + 1, player["x"] - move_speed)
    elif key == GLUT_KEY_RIGHT:
        player["x"] = min(ENV_SIZE/2 - 1, player["x"] + move_speed)
    
    glutPostRedisplay()

# ---------------------------
# Main
# ---------------------------

def main():
    """Initializes OpenGL and starts the main loop."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Dragon Slayer - PyOpenGL")
    
    init_game()

    glutDisplayFunc(display)
    glutIdleFunc(update_game_state)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
