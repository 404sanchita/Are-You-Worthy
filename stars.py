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

# Isometric view settings
isometric_angle = 45  # Degrees for isometric view
isometric_elevation = 30  # Degrees for elevation
camera_distance = 20.0  # Distance from scene center

# ---------------------------
# Constellation Game Variables
# ---------------------------
constellation_active = False
stars = []
current_constellation = []
connected_stars = []
constellation_shapes = {
    "dragon": [(0, 0), (2, 1), (4, 0), (3, -2), (1, -3), (-1, -2), (-2, 0), (0, 2)],
    "bear": [(-2, 0), (0, 2), (2, 1), (3, -1), (1, -2), (-1, -1), (-3, -2), (-2, 0)],
    "swan": [(-3, 0), (-1, 2), (1, 1), (3, 0), (2, -2), (0, -3), (-2, -2), (-3, 0)]
}
current_shape = ""
game_score = 0
constellation_timer = 0
MAX_CONSTELLATION_TIME = 60  # seconds

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

def draw_player():
    # Draw player as a colored cube
    glColor3f(1.0, 0.0, 0.0)  # red player
    glPushMatrix()
    glTranslatef(player["x"], 0.5, player["z"])
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_stars():
    if not constellation_active:
        return
        
    # Draw stars in the sky (positioned high above the ground)
    for i, star in enumerate(stars):
        glPushMatrix()
        glTranslatef(star["x"], 15.0, star["z"])  # Stars are high up
        
        # Make star glow
        glDisable(GL_LIGHTING)
        if i in connected_stars:
            glColor3f(0.0, 1.0, 0.0)  # Connected stars are green
        else:
            glColor3f(1.0, 1.0, 0.8)  # Yellow-white for unconnected stars
            
        glutSolidSphere(0.3, 10, 10)
        
        # Add a glow effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 1.0, 0.5, 0.3)
        glutSolidSphere(0.5, 8, 8)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    # Draw connections between stars
    if len(connected_stars) > 1:
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.8, 1.0)  # Cyan connection lines
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        for star_idx in connected_stars:
            star = stars[star_idx]
            glVertex3f(star["x"], 15.0, star["z"])
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

def draw_sky():
    # Draw night sky background
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)
    glColor3f(0.05, 0.05, 0.2)  # Dark blue at horizon
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glColor3f(0.02, 0.02, 0.1)  # Darker blue at top
    glVertex3f(ENV_SIZE, 30, -ENV_SIZE)
    glVertex3f(-ENV_SIZE, 30, -ENV_SIZE)
    
    glColor3f(0.05, 0.05, 0.2)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glColor3f(0.02, 0.02, 0.1)
    glVertex3f(ENV_SIZE, 30, ENV_SIZE)
    glVertex3f(-ENV_SIZE, 30, ENV_SIZE)
    
    glColor3f(0.05, 0.05, 0.2)
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glColor3f(0.02, 0.02, 0.1)
    glVertex3f(-ENV_SIZE, 30, ENV_SIZE)
    glVertex3f(-ENV_SIZE, 30, -ENV_SIZE)
    
    glColor3f(0.05, 0.05, 0.2)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glColor3f(0.02, 0.02, 0.1)
    glVertex3f(ENV_SIZE, 30, ENV_SIZE)
    glVertex3f(ENV_SIZE, 30, -ENV_SIZE)
    glEnd()
    glEnable(GL_LIGHTING)

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
# Constellation Game Functions
# ---------------------------

def start_constellation_game():
    global constellation_active, stars, current_constellation, connected_stars, current_shape, constellation_timer
    
    constellation_active = True
    stars = []
    connected_stars = []
    current_shape = random.choice(list(constellation_shapes.keys()))
    current_constellation = constellation_shapes[current_shape]
    
    # Position stars based on the constellation pattern
    for i, (dx, dz) in enumerate(current_constellation):
        stars.append({
            "x": dx * 2,  # Scale the pattern
            "z": dz * 2,
            "index": i
        })
    
    constellation_timer = MAX_CONSTELLATION_TIME
    print(f"Constellation Game Started! Find the {current_shape.upper()} shape!")
    print("Click on stars in the correct order to form the constellation.")

def check_constellation_completion():
    global constellation_active, game_score
    
    if len(connected_stars) == len(stars):
        # Check if the order is correct
        correct = True
        for i, star_idx in enumerate(connected_stars):
            if star_idx != i:
                correct = False
                break
                
        if correct:
            points = int(constellation_timer * 10)  # More points for faster completion
            game_score += points
            print(f"Perfect! You formed the {current_shape} constellation! +{points} points")
        else:
            print("Almost! The constellation is formed but in the wrong order.")
            
        constellation_active = False
        return True
    return False

def find_nearest_star(x, z):
    nearest_star = None
    min_distance = float('inf')
    
    for i, star in enumerate(stars):
        if i in connected_stars:
            continue  # Skip already connected stars
            
        distance = math.sqrt((star["x"] - x)**2 + (star["z"] - z)**2)
        if distance < min_distance and distance < 3.0:  # Only select if close enough
            min_distance = distance
            nearest_star = i
            
    return nearest_star

# ---------------------------
# Scene Rendering
# ---------------------------

def check_collision(x, z):
    # Check if player is out of bounds
    if abs(x) > ENV_SIZE/2 - 1 or abs(z) > ENV_SIZE/2 - 1:
        return True
    return False

def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_isometric_camera()

    glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark blue for night sky

    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Enable lighting for better visibility
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light (moonlight)
    light_position = [10.0, 15.0, 10.0, 1.0]
    light_ambient = [0.1, 0.1, 0.2, 1.0]
    light_diffuse = [0.4, 0.4, 0.6, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    draw_sky()
    draw_ground()
    draw_player()
    draw_stars()

    # Draw boundary
    glColor3f(0.5, 0.5, 0.7)
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
    
    # Draw UI elements
    draw_text(10, 30, f"Score: {game_score}")
    
    if constellation_active:
        draw_text(10, 50, f"Find the: {current_shape.upper()}")
        draw_text(10, 70, f"Time: {int(constellation_timer)}s")
        draw_text(10, 90, "Click on stars in order to form the constellation")
    else:
        draw_text(10, 50, "Press SPACE to start constellation game")
        
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glutSwapBuffers()

# ---------------------------
# Controls & Movement
# ---------------------------

def keyboard(key, x, y):
    global isometric_angle, camera_distance, constellation_active
    
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
    elif key == ' ' and not constellation_active:  # Space to start game
        start_constellation_game()

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

def mouse(button, state, x, y):
    global connected_stars, constellation_timer
    
    if constellation_active and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convert mouse coordinates to world coordinates
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Convert y coordinate to OpenGL format
        y = viewport[3] - y
        
        # Get world coordinates at ground level (y=0)
        win_x, win_y = x, y
        win_z = 0.0
        
        # Get near and far points
        near_point = gluUnProject(win_x, win_y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(win_x, win_y, 1.0, modelview, projection, viewport)
        
        # Find intersection with y=15 plane (where stars are)
        if far_point[1] - near_point[1] != 0:
            t = (15.0 - near_point[1]) / (far_point[1] - near_point[1])
            intersect_x = near_point[0] + t * (far_point[0] - near_point[0])
            intersect_z = near_point[2] + t * (far_point[2] - near_point[2])
            
            # Find the nearest star to the click position
            star_idx = find_nearest_star(intersect_x, intersect_z)
            if star_idx is not None and star_idx not in connected_stars:
                connected_stars.append(star_idx)
                print(f"Star {star_idx+1} connected!")
                check_constellation_completion()

def update_timer(value):
    global constellation_timer, constellation_active
    
    if constellation_active:
        constellation_timer -= 0.1
        if constellation_timer <= 0:
            print("Time's up! Constellation game ended.")
            constellation_active = False
        
    glutTimerFunc(100, update_timer, 0)  # Update every 100ms
    glutPostRedisplay()

# ---------------------------
# Main
# ---------------------------

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Constellation Game - Connect the Stars")
    
    # Set initial player position
    player["x"] = 0.0
    player["z"] = 0.0

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutTimerFunc(100, update_timer, 0)  # Start timer

    print("Constellation Game")
    print("Controls:")
    print("Arrow Keys: Move in the isometric view directions")
    print("I/K: Zoom in/out")
    print("J/L: Rotate the isometric view")
    print("R: Reset position")
    print("SPACE: Start constellation game")
    print("LEFT CLICK: Connect stars in the correct order")
    print("ESC: Quit")

    glutMainLoop()

if __name__ == "__main__":
    main()
