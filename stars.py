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
# *** REPLACED "bear" with "house" for an easier shape ***
constellation_shapes = {
    "dragon": [(0, 0), (2, 1), (4, 0), (3, -2), (1, -3), (-1, -2), (-2, 0), (0, 2)],
    "house": [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0), (2, 6), (4, 4)], # A simple house shape
    "swan": [(-3, 0), (-1, 2), (1, 1), (3, 0), (2, -2), (0, -3), (-2, -2), (-3, 0)]
}
current_shape = ""
game_score = 0
constellation_timer = 0
MAX_CONSTELLATION_TIME = 60  # seconds

# *** NEW: Game state variables for lives and win/loss conditions ***
player_lives = 3
game_won = False
game_over = False

# ---------------------------
# Drawing
# ---------------------------

def draw_ground():
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE, 0, ENV_SIZE)
    glVertex3f(-ENV_SIZE, 0, ENV_SIZE)
    glEnd()
    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-int(ENV_SIZE), int(ENV_SIZE) + 1, 2):
        glVertex3f(i, 0.01, -ENV_SIZE); glVertex3f(i, 0.01, ENV_SIZE)
        glVertex3f(-ENV_SIZE, 0.01, i); glVertex3f(ENV_SIZE, 0.01, i)
    glEnd()

def draw_player():
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(player["x"], 0.5, player["z"])
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_stars():
    if not constellation_active: return
    for i, star in enumerate(stars):
        glPushMatrix()
        glTranslatef(star["x"], 15.0, star["z"])
        glDisable(GL_LIGHTING)
        if i in connected_stars: glColor3f(0.0, 1.0, 0.0)
        else: glColor3f(1.0, 1.0, 0.8)
        glutSolidSphere(0.3, 10, 10)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 1.0, 0.5, 0.3)
        glutSolidSphere(0.5, 8, 8)
        glDisable(GL_BLEND); glEnable(GL_LIGHTING)
        glPopMatrix()
    
    if len(connected_stars) > 1:
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.8, 1.0)
        glLineWidth(2.0)
        is_loop = current_constellation and current_constellation[0] == current_constellation[-1]
        draw_mode = GL_LINE_LOOP if is_loop else GL_LINE_STRIP
        glBegin(draw_mode)
        for star_idx in connected_stars:
            star = stars[star_idx]
            glVertex3f(star["x"], 15.0, star["z"])
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

# (Other drawing functions like draw_sky, draw_minimap, etc. remain the same)
def draw_sky():
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glBegin(GL_QUADS)
    glColor3f(0.02, 0.02, 0.1); glVertex3f(-1, 1, -1); glVertex3f(1, 1, -1)
    glColor3f(0.05, 0.05, 0.2); glVertex3f(1, -1, -1); glVertex3f(-1, -1, -1)
    glEnd()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

def draw_constellation_preview():
    if not constellation_active or not current_constellation: return
    glColor4f(0.1, 0.1, 0.1, 0.7)
    glBegin(GL_QUADS); glVertex2f(10, WINDOW_H - 140); glVertex2f(140, WINDOW_H - 140); glVertex2f(140, WINDOW_H - 270); glVertex2f(10, WINDOW_H - 270); glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20, WINDOW_H - 155)
    for char in "TARGET SHAPE:": glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
    points = current_constellation
    min_x = min(p[0] for p in points); max_x = max(p[0] for p in points)
    min_z = min(p[1] for p in points); max_z = max(p[1] for p in points)
    span_x = max_x - min_x if max_x > min_x else 1.0
    span_z = max_z - min_z if max_z > min_z else 1.0
    box_x, box_y = 15, WINDOW_H - 265; box_w, box_h = 120, 110; padding = 15
    def map_coords(p):
        norm_x = (p[0] - min_x) / span_x; norm_z = (p[1] - min_z) / span_z
        screen_x = box_x + padding + norm_x * (box_w - 2 * padding)
        screen_y = box_y + padding + norm_z * (box_h - 2 * padding)
        return screen_x, screen_y
    mapped_points = [map_coords(p) for p in points]
    glColor3f(0.0, 0.8, 1.0); glLineWidth(2.0)
    is_loop = points and points[0] == points[-1]
    draw_mode = GL_LINE_LOOP if is_loop else GL_LINE_STRIP
    glBegin(draw_mode)
    for sx, sy in mapped_points: glVertex2f(sx, sy)
    glEnd()
    glLineWidth(1.0)
    glEnable(GL_POINT_SMOOTH); glPointSize(5.0); glColor3f(1.0, 1.0, 0.8)
    glBegin(GL_POINTS)
    for sx, sy in mapped_points: glVertex2f(sx, sy)
    glEnd()
    glPointSize(1.0); glDisable(GL_POINT_SMOOTH)

def draw_minimap():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor4f(0.1, 0.1, 0.1, 0.7)
    glBegin(GL_QUADS); glVertex2f(10, WINDOW_H - 10); glVertex2f(140, WINDOW_H - 10); glVertex2f(140, WINDOW_H - 130); glVertex2f(10, WINDOW_H - 130); glEnd()
    map_size = 110; map_ox, map_oy = 15, WINDOW_H - 125
    glColor3f(0.1, 0.6, 0.1)
    glBegin(GL_QUADS); glVertex2f(map_ox, map_oy + map_size); glVertex2f(map_ox + map_size, map_oy + map_size); glVertex2f(map_ox + map_size, map_oy); glVertex2f(map_ox, map_oy); glEnd()
    map_x = map_ox + (player["x"] + ENV_SIZE) * map_size / (ENV_SIZE * 2)
    map_y = map_oy + (player["z"] + ENV_SIZE) * map_size / (ENV_SIZE * 2)
    glColor3f(1, 0, 0); glPointSize(6.0); glEnable(GL_POINT_SMOOTH)
    glBegin(GL_POINTS); glVertex2f(map_x, map_y); glEnd()
    glDisable(GL_POINT_SMOOTH); glPointSize(1.0)
    draw_constellation_preview()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

# ---------------------------
# Game State and Logic
# ---------------------------

def reset_game():
    """Resets the entire game state to the beginning."""
    global player_lives, game_score, game_won, game_over, constellation_active
    player["x"], player["z"] = 0.0, 0.0
    player_lives = 3
    game_score = 0
    game_won = False
    game_over = False
    constellation_active = False
    print("\n--- Game Reset! ---")

def set_isometric_camera():
    angle_rad, elevation_rad = math.radians(isometric_angle), math.radians(isometric_elevation)
    cam_x = player["x"] + camera_distance * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = camera_distance * math.sin(elevation_rad)
    cam_z = player["z"] + camera_distance * math.sin(angle_rad) * math.cos(elevation_rad)
    gluLookAt(cam_x, cam_y, cam_z, player["x"], 0, player["z"], 0, 1, 0)

def start_constellation_game():
    global constellation_active, stars, current_constellation, connected_stars, current_shape, constellation_timer
    if game_won or game_over: return
    constellation_active = True
    stars, connected_stars = [], []
    current_shape = random.choice(list(constellation_shapes.keys()))
    current_constellation = constellation_shapes[current_shape]
    scale_factor = 3.5
    for i, (dx, dz) in enumerate(current_constellation):
        stars.append({"x": dx * scale_factor, "z": dz * scale_factor, "index": i})
    constellation_timer = MAX_CONSTELLATION_TIME
    print(f"A new challenge appears! Find the {current_shape.upper()} shape!")

def check_constellation_completion():
    """UPDATED: Handles win, loss of life, and game over conditions."""
    global constellation_active, game_score, player_lives, game_won, game_over, connected_stars
    
    if len(connected_stars) == len(stars):
        # Correct Order - WIN!
        if connected_stars == list(range(len(stars))):
            points = int(constellation_timer * 10)
            game_score += points
            print(f"PERFECT! Quest Complete! +{points} points")
            game_won = True
            constellation_active = False
        # Incorrect Order - LOSE A LIFE
        else:
            player_lives -= 1
            print(f"Wrong order! You lost a life. {player_lives} lives remaining.")
            if player_lives <= 0:
                print("You are out of lives! Game Over.")
                game_over = True
                constellation_active = False
            else:
                # Reset for another try on the same constellation
                connected_stars = []
                print("Try connecting the stars again.")

def find_nearest_star(x, z):
    nearest_star_idx, min_distance = None, float('inf')
    for i, star in enumerate(stars):
        if star["index"] in connected_stars: continue
        distance = math.sqrt((star["x"] - x)**2 + (star["z"] - z)**2)
        if distance < min_distance and distance < 2.0:
            min_distance, nearest_star_idx = distance, star["index"]
    return nearest_star_idx
# ---------------------------
# Scene Rendering
# ---------------------------

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1, 1, 1)
    # Center text if x is None
    if x is None:
        text_width = sum(glutBitmapWidth(font, ord(c)) for c in text)
        x = (WINDOW_W - text_width) / 2
    glRasterPos2f(x, y)
    for char in text: glutBitmapCharacter(font, ord(char))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def display():
    glClearColor(0.05, 0.05, 0.15, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    set_isometric_camera()

    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL)
    light_position = [10.0, 15.0, 10.0, 1.0]; light_ambient = [0.2, 0.2, 0.3, 1.0]; light_diffuse = [0.6, 0.6, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position); glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient); glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    draw_ground(); draw_player(); draw_stars()

    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)
    
    # *** UPDATED: New UI logic for different game states ***
    if game_won:
        draw_text(None, WINDOW_H / 2, "YOU WIN! QUEST COMPLETE!", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(None, WINDOW_H / 2 - 30, "Press 'R' to play again.", GLUT_BITMAP_HELVETICA_18)
    elif game_over:
        draw_text(None, WINDOW_H / 2, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(None, WINDOW_H / 2 - 30, "Press 'R' to try again.", GLUT_BITMAP_HELVETICA_18)
    else:
        draw_minimap()
        draw_text(150, WINDOW_H - 30, f"Score: {game_score}")
        draw_text(150, WINDOW_H - 60, f"Lives: {player_lives}")
        if constellation_active:
            draw_text(150, WINDOW_H - 90, f"Find: {current_shape.upper()}")
            draw_text(150, WINDOW_H - 120, f"Time: {int(constellation_timer)}s")
        else:
            draw_text(10, WINDOW_H - 300, "Press SPACE to start the quest")
            
    glEnable(GL_DEPTH_TEST)
    glutSwapBuffers()

# ---------------------------
# Controls & Movement
# ---------------------------

def keyboard(key, x, y):
    global isometric_angle, camera_distance
    key = key.decode('utf-8')
    if key == '\x1b': glutLeaveMainLoop()
    elif key == 'r': reset_game()
    
    if game_won or game_over: return # Disable controls on win/loss

    if key == 'i': camera_distance = max(5.0, camera_distance - 2.0)
    elif key == 'k': camera_distance = min(50.0, camera_distance + 2.0)
    elif key == 'j': isometric_angle = (isometric_angle - 5) % 360
    elif key == 'l': isometric_angle = (isometric_angle + 5) % 360
    elif key == ' ' and not constellation_active: start_constellation_game()

def special_keys(key, x, y):
    if game_won or game_over: return # Disable controls on win/loss
    speed = 0.5; angle_rad = math.radians(isometric_angle)
    dx, dz = 0, 0
    if key == GLUT_KEY_UP: dx, dz = speed * math.cos(angle_rad), speed * math.sin(angle_rad)
    elif key == GLUT_KEY_DOWN: dx, dz = -speed * math.cos(angle_rad), -speed * math.sin(angle_rad)
    elif key == GLUT_KEY_LEFT: dx, dz = speed * math.sin(angle_rad), -speed * math.cos(angle_rad)
    elif key == GLUT_KEY_RIGHT: dx, dz = -speed * math.sin(angle_rad), speed * math.cos(angle_rad)
    new_x, new_z = player["x"] + dx, player["z"] + dz
    boundary = ENV_SIZE - 0.5
    if not (abs(new_x) > boundary or abs(new_z) > boundary):
        player["x"], player["z"] = new_x, new_z

def mouse(button, state, x, y):
    if game_won or game_over or not constellation_active: return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        viewport = glGetIntegerv(GL_VIEWPORT); modelview = glGetDoublev(GL_MODELVIEW_MATRIX); projection = glGetDoublev(GL_PROJECTION_MATRIX)
        ogl_y = viewport[3] - y
        near_point = gluUnProject(x, ogl_y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(x, ogl_y, 1.0, modelview, projection, viewport)
        if far_point[1] - near_point[1] != 0:
            t = (15.0 - near_point[1]) / (far_point[1] - near_point[1])
            intersect_x = near_point[0] + t * (far_point[0] - near_point[0])
            intersect_z = near_point[2] + t * (far_point[2] - near_point[2])
            star_idx = find_nearest_star(intersect_x, intersect_z)
            if star_idx is not None and star_idx not in connected_stars:
                connected_stars.append(star_idx)
                connected_stars.sort()
                print(f"Star #{star_idx + 1} connected!")
                check_constellation_completion()

def update(value):
    global constellation_timer, constellation_active, player_lives, game_over
    if constellation_active:
        constellation_timer -= 0.1
        if constellation_timer <= 0:
            constellation_active = False
            player_lives -= 1
            print(f"Time's up! You lost a life. {player_lives} lives remaining.")
            if player_lives <= 0:
                print("You are out of lives! Game Over.")
                game_over = True
            constellation_timer = 0
    glutTimerFunc(100, update, 0)
    glutPostRedisplay()

# ---------------------------
# Main
# ---------------------------

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Constellation Quest")
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutTimerFunc(100, update, 0)
    print("--- Constellation Quest ---")
    print("Complete one constellation correctly to win!")
    print("Controls:")
    print("  Arrow Keys: Move | J/L: Rotate | I/K: Zoom")
    print("  R: Reset Game | SPACE: Start Quest | ESC: Quit")
    glutMainLoop()

if __name__ == "__main__":
    main()
