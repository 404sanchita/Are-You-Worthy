from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ---------------------------
# Window config
# ---------------------------
WINDOW_W, WINDOW_H = 800, 600

# Player
player = {"x": 0.0, "z": 0.0, "yaw": 0.0}

# Environment size
ENV_SIZE = 30.0
TREE_COUNT = 20  # Number of trees to generate

# Tree positions (x, z)
trees = []

# Generate random tree positions
for _ in range(TREE_COUNT):
    x = random.uniform(-ENV_SIZE/2 + 2, ENV_SIZE/2 - 2)
    z = random.uniform(-ENV_SIZE/2 + 2, ENV_SIZE/2 - 2)
    trees.append((x, z))

# Isometric view settings
isometric_angle = 45  # Degrees for isometric view
isometric_elevation = 30  # Degrees for elevation
camera_distance = 20.0  # Distance from scene center

# ---------------------------
# Drawing
# ---------------------------

def draw_ground():
    # Draw a grid for the ground
    glColor3f(0.1, 0.6, 0.1)  # green ground
    glBegin(GL_QUADS)
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glEnd()
    
    # Draw grid lines
    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-int(ENV_SIZE/2), int(ENV_SIZE/2) + 1, 2):
        glVertex3f(i, 0.01, -ENV_SIZE)
        glVertex3f(i, 0.01, ENV_SIZE)
        glVertex3f(-ENV_SIZE, 0.01, i)
        glVertex3f(ENV_SIZE, 0.01, i)
    glEnd()

def draw_tree(x, z):
    # Draw trunk
    glColor3f(0.4, 0.2, 0.1)  # brown trunk
    glPushMatrix()
    glTranslatef(x, 1.0, z)
    glScalef(0.3, 2.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw foliage (tree top)
    glColor3f(0.1, 0.5, 0.1)  # green foliage
    glPushMatrix()
    glTranslatef(x, 2.5, z)
    glutSolidSphere(0.8, 16, 16)
    glPopMatrix()

def draw_trees():
    for x, z in trees:
        draw_tree(x, z)

def draw_player():
    # Draw player as a colored cube
    glColor3f(1.0, 0.0, 0.0)  # red player
    glPushMatrix()
    glTranslatef(player["x"], 0.5, player["z"])
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

# ---------------------------
# Mini-map (top-left)
# ---------------------------

def draw_minimap():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw minimap background
    glColor4f(0.1, 0.1, 0.1, 0.7)  # dark semi-transparent
    glBegin(GL_QUADS)
    glVertex2f(10, WINDOW_H - 10)
    glVertex2f(160, WINDOW_H - 10)
    glVertex2f(160, WINDOW_H - 160)
    glVertex2f(10, WINDOW_H - 160)
    glEnd()

    # Draw ground area
    glColor3f(0.1, 0.6, 0.1)  # green
    glBegin(GL_QUADS)
    glVertex2f(20, WINDOW_H - 20)
    glVertex2f(150, WINDOW_H - 20)
    glVertex2f(150, WINDOW_H - 150)
    glVertex2f(20, WINDOW_H - 150)
    glEnd()

    # Draw trees on minimap
    glColor3f(0.4, 0.2, 0.1)  # brown for trees
    for x, z in trees:
        # Convert world coordinates to minimap coordinates
        map_x = 20 + (x + ENV_SIZE/2) * 130 / ENV_SIZE
        map_y = WINDOW_H - 20 - (z + ENV_SIZE/2) * 130 / ENV_SIZE
        glBegin(GL_QUADS)
        glVertex2f(map_x-2, map_y-2)
        glVertex2f(map_x+2, map_y-2)
        glVertex2f(map_x+2, map_y+2)
        glVertex2f(map_x-2, map_y+2)
        glEnd()

    # Draw player as red dot
    map_x = 20 + (player["x"] + ENV_SIZE/2) * 130 / ENV_SIZE
    map_y = WINDOW_H - 20 - (player["z"] + ENV_SIZE/2) * 130 / ENV_SIZE
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

# ---------------------------
# Isometric Camera
# ---------------------------

def set_isometric_camera():
    # Calculate camera position for isometric view
    angle_rad = math.radians(isometric_angle)
    elevation_rad = math.radians(isometric_elevation)
    
    cam_x = camera_distance * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = camera_distance * math.sin(elevation_rad)
    cam_z = camera_distance * math.sin(angle_rad) * math.cos(elevation_rad)
    
    # Look at the center of the scene
    gluLookAt(cam_x, cam_y, cam_z,   # camera position
              0, 0, 0,               # look at center
              0, 1, 0)               # up vector

# ---------------------------
# Scene Rendering
# ---------------------------

def check_collision(x, z):
    # Check if player is colliding with any tree
    for tree_x, tree_z in trees:
        distance = math.sqrt((x - tree_x)**2 + (z - tree_z)**2)
        if distance < 1.5:  # Collision radius
            return True
    
    # Check if player is out of bounds
    if abs(x) > ENV_SIZE/2 - 1 or abs(z) > ENV_SIZE/2 - 1:
        return True
    
    return False

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_isometric_camera()

    glClearColor(0.5, 0.7, 0.9, 1.0)  # blue sky

    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Enable lighting for better visibility
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light
    light_position = [10.0, 10.0, 10.0, 1.0]
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    draw_ground()
    draw_trees()
    draw_player()

    # Draw boundary
    glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-ENV_SIZE/2, 0.1, -ENV_SIZE/2)
    glVertex3f(ENV_SIZE/2, 0.1, -ENV_SIZE/2)
    glVertex3f(ENV_SIZE/2, 0.1, ENV_SIZE/2)
    glVertex3f(-ENV_SIZE/2, 0.1, ENV_SIZE/2)
    glEnd()

    # Mini-map overlay
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    draw_minimap()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    # Display instructions
    glColor3f(1, 1, 1)
    glWindowPos2f(10, 30)
    for c in "Arrow Keys: Move, I/K: Zoom, J/L: Rotate, R: Reset":
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

    glutSwapBuffers()

# ---------------------------
# Controls & Movement
# ---------------------------

def keyboard(key, x, y):
    global isometric_angle, camera_distance
    
    key = key.decode('utf-8')
    if key == '\x1b':  # Esc
        glutLeaveMainLoop()
    elif key == 'r':  # Reset position
        player["x"] = 0.0
        player["z"] = 0.0
    elif key == 'i':  # Zoom in
        camera_distance = max(5.0, camera_distance - 2.0)
    elif key == 'k':  # Zoom out
        camera_distance = min(40.0, camera_distance + 2.0)
    elif key == 'j':  # Rotate left
        isometric_angle = (isometric_angle - 5) % 360
    elif key == 'l':  # Rotate right
        isometric_angle = (isometric_angle + 5) % 360

def special_keys(key, x, y):
    # Movement relative to isometric view
    angle_rad = math.radians(isometric_angle)
    
    if key == GLUT_KEY_UP:
        # Move along the view direction (XZ plane)
        player["x"] += 0.5 * math.sin(angle_rad)
        player["z"] += 0.5 * math.cos(angle_rad)
    elif key == GLUT_KEY_DOWN:
        player["x"] -= 0.5 * math.sin(angle_rad)
        player["z"] -= 0.5 * math.cos(angle_rad)
    elif key == GLUT_KEY_LEFT:
        # Move perpendicular to view direction
        player["x"] -= 0.5 * math.cos(angle_rad)
        player["z"] += 0.5 * math.sin(angle_rad)
    elif key == GLUT_KEY_RIGHT:
        player["x"] += 0.5 * math.cos(angle_rad)
        player["z"] -= 0.5 * math.sin(angle_rad)
    
    # Check collision after moving
    if check_collision(player["x"], player["z"]):
        # Undo movement if collision detected
        if key == GLUT_KEY_UP:
            player["x"] -= 0.5 * math.sin(angle_rad)
            player["z"] -= 0.5 * math.cos(angle_rad)
        elif key == GLUT_KEY_DOWN:
            player["x"] += 0.5 * math.sin(angle_rad)
            player["z"] += 0.5 * math.cos(angle_rad)
        elif key == GLUT_KEY_LEFT:
            player["x"] += 0.5 * math.cos(angle_rad)
            player["z"] -= 0.5 * math.sin(angle_rad)
        elif key == GLUT_KEY_RIGHT:
            player["x"] -= 0.5 * math.cos(angle_rad)
            player["z"] += 0.5 * math.sin(angle_rad)

# ---------------------------
# Main
# ---------------------------

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"3D Environment with Isometric View - PyOpenGL")
    
    # Set initial player position
    player["x"] = 0.0
    player["z"] = 0.0

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)

    print("3D Environment with Isometric View")
    print("Controls:")
    print("Arrow Keys: Move in the isometric view directions")
    print("I/K: Zoom in/out")
    print("J/L: Rotate the isometric view")
    print("R: Reset position")
    print("ESC: Quit")

    glutMainLoop()

if __name__ == "__main__":
    main()
