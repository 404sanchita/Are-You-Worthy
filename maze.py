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

# Player - starting at a valid position (not inside a wall)
player = {"x": 0.0, "z": 0.0, "yaw": 0.0}

# More complex maze layout: 1 = wall, 0 = empty
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
score = 0
b_key_pressed = False
game_over = False
win = False
countdown_timer = 30.0
last_update_time = time.time()

# Isometric view settings
isometric_angle = 45 
isometric_elevation = 35 
camera_distance = 20.0 

# Rewards and Bombs
rewards = []
bombs = []
MAX_REWARDS = 5
MAX_BOMBS = 3

# Find a valid starting position (not in a wall)
def find_valid_start():
    for i in range(ROWS):
        for j in range(COLS):
            if maze[i][j] == 0: 
                x = (i - ROWS//2) * TILE_SIZE
                z = (j - COLS//2) * TILE_SIZE
                return x, z
    return 0, 0 

# Spawn rewards and bombs in empty spaces
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

    # Spawn rewards
    rewards = []
    for i in range(min(MAX_REWARDS, len(empty_spaces))):
        rewards.append(empty_spaces.pop())
    
    # Spawn bombs
    bombs = []
    for i in range(min(MAX_BOMBS, len(empty_spaces))):
        bombs.append(empty_spaces.pop())

# Set player to valid starting position and spawn items
player["x"], player["z"] = find_valid_start()
spawn_items()

# ---------------------------
# Drawing
# ---------------------------

def draw_ground():
    # Draw the ground
    glColor3f(0.2, 0.9, 0.2) 
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, -30)
    glVertex3f(30, 0, -30)
    glVertex3f(30, 0, 30)
    glVertex3f(-30, 0, 30)
    glEnd()
    
    # Draw grid lines
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
    # Draw a solid wall without gaps
    glColor3f(0.5, 0.5, 0.7) 
    
    # Draw the wall as a solid cube
    glPushMatrix()
    glTranslatef(x, WALL_HEIGHT/2, z)
    glScalef(TILE_SIZE, WALL_HEIGHT, TILE_SIZE)
    
    # Draw all six faces of the cube
    glBegin(GL_QUADS)
    
    # Front face
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Back face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    
    # Top face
    glColor3f(0.6, 0.2, 0.1) 
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Bottom face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    
    # Right face
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    
    # Left face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    glEnd()
    glPopMatrix()

def draw_items():
    # Draw rewards (yellow spheres)
    for rx, rz in rewards:
        glColor3f(1.0, 1.0, 0.0)
        glPushMatrix()
        glTranslatef(rx, 0.5, rz)
        glutSolidSphere(0.3, 16, 16)
        glPopMatrix()
    
    # Draw bombs (red spheres)
    for bx, bz in bombs:
        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(bx, 0.5, bz)
        glutSolidSphere(0.3, 16, 16)
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

    # Draw player as blue dot
    pi = int(round((player["x"] + (ROWS//2)*TILE_SIZE) / TILE_SIZE))
    pj = int(round((player["z"] + (COLS//2)*TILE_SIZE) / TILE_SIZE))
    glColor3f(0,0,1)
    px = offset_x + pj*tile_px + tile_px/2
    py = offset_y - pi*tile_px - tile_px/2
    glBegin(GL_QUADS)
    glVertex2f(px-3, py-3)
    glVertex2f(px+3, py-3)
    glVertex2f(px+3, py+3)
    glVertex2f(px-3, py+3)
    glEnd()

    # Draw rewards on minimap
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

    # Draw bombs on minimap
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
# Isometric Camera
# ---------------------------

def set_isometric_camera():
    # Calculate camera position for isometric view
    angle_rad = math.radians(isometric_angle)
    elevation_rad = math.radians(isometric_elevation)
    
    # Calculate center of maze
    center_x = 0
    center_z = 0
    
    cam_x = center_x + camera_distance * math.cos(angle_rad) * math.cos(elevation_rad)
    cam_y = camera_distance * math.sin(elevation_rad)
    cam_z = center_z + camera_distance * math.sin(angle_rad) * math.cos(elevation_rad)
    
    # Look at the center of the maze
    gluLookAt(cam_x, cam_y, cam_z, 
              center_x, 0, center_z, 
              0, 1, 0) 

# ---------------------------
# Scene Rendering
# ---------------------------

def draw_player():
    # Draw player as a blue sphere
    glColor3f(0.0, 0.0, 1.0) 
    glPushMatrix()
    glTranslatef(player["x"], 0.5, player["z"])
    glutSolidSphere(0.3, 16, 16)
    glPopMatrix()

def check_collision(x, z):
    # Convert world coordinates to maze grid coordinates
    i = int(round((x + (ROWS//2)*TILE_SIZE) / TILE_SIZE))
    j = int(round((z + (COLS//2)*TILE_SIZE) / TILE_SIZE))
    
    # Check if out of bounds
    if i < 0 or i >= ROWS or j < 0 or j >= COLS:
        return True
    
    # Check if colliding with a wall
    return maze[i][j] == 1

def check_item_collision():
    global score, rewards, bombs
    player_pos = (player["x"], player["z"])
    
    # Check for reward collision
    new_rewards = []
    for rx, rz in rewards:
        dist_sq = (player_pos[0] - rx)**2 + (player_pos[1] - rz)**2
        if dist_sq < 0.5**2:
            score += 1
            spawn_items()
            return
        else:
            new_rewards.append((rx, rz))
    rewards = new_rewards

    # Check for bomb collision
    new_bombs = []
    for bx, bz in bombs:
        dist_sq = (player_pos[0] - bx)**2 + (player_pos[1] - bz)**2
        if dist_sq < 0.5**2:
            if b_key_pressed:
                score += 1
            else:
                score -= 1
            spawn_items()
            return
        else:
            new_bombs.append((bx, bz))
    bombs = new_bombs

def display():
    global countdown_timer, last_update_time, game_over, win, score
    
    # Update game state if not over
    if not game_over:
        current_time = time.time()
        delta_time = current_time - last_update_time
        last_update_time = current_time
        countdown_timer -= delta_time

        # Check win/loss conditions
        if score >= 10:
            game_over = True
            win = True
        elif countdown_timer <= 0:
            game_over = True
            win = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W/float(WINDOW_H), 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_isometric_camera()

    glClearColor(0.5, 0.7, 0.9, 1.0) 

    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    draw_ground()
    draw_walls()
    draw_items()
    draw_player()

    # Mini-map overlay
    glDisable(GL_DEPTH_TEST)
    draw_minimap()
    glEnable(GL_DEPTH_TEST)

    # Display score, time and instructions
    glColor3f(1, 1, 1)
    
    if not game_over:
        score_text = f"Score: {score} | Time: {int(countdown_timer)}"
        glWindowPos2f(10, WINDOW_H - 30)
        for c in score_text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))

        glWindowPos2f(10, 10)
        instructions = "Arrow Keys: Move, I/K: Zoom, J/L: Rotate, R: Reset, B: Bomb Mode"
        for c in instructions:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
    else:
        if win:
            message = "You Win! Final Score: " + str(score)
        else:
            message = "Game Over! You didn't collect 10 items in time."
        
        glWindowPos2f(WINDOW_W/2 - 150, WINDOW_H/2)
        for c in message:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
        
        reset_msg = "Press 'R' to play again."
        glWindowPos2f(WINDOW_W/2 - 100, WINDOW_H/2 - 30)
        for c in reset_msg:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))


    glutSwapBuffers()

# ---------------------------
# Controls & Movement
# ---------------------------

def keyboard(key, x, y):
    global isometric_angle, camera_distance, b_key_pressed, score, countdown_timer, game_over, win
    
    key_str = key.decode('utf-8')
    if key_str == '\x1b': 
        glutLeaveMainLoop()
    elif key_str == 'r': 
        score = 0
        countdown_timer = 15.0
        game_over = False
        win = False
        player["x"], player["z"] = find_valid_start()
        spawn_items()
        last_update_time = time.time()
    elif key_str == 'i' and not game_over: 
        camera_distance = max(8.0, camera_distance - 2.0)
    elif key_str == 'k' and not game_over:
        camera_distance = min(35.0, camera_distance + 2.0)
    elif key_str == 'j' and not game_over: 
        isometric_angle = (isometric_angle - 5) % 360
    elif key_str == 'l' and not game_over:
        isometric_angle = (isometric_angle + 5) % 360
    elif key_str == 'b' and not game_over: 
        b_key_pressed = True

    glutPostRedisplay()

def keyboard_up(key, x, y):
    global b_key_pressed
    key_str = key.decode('utf-8')
    if key_str == 'b':
        b_key_pressed = False
    
    glutPostRedisplay()

def special_keys(key, x, y):
    if game_over:
        return
    
    new_x, new_z = player["x"], player["z"]
    
    if key == GLUT_KEY_UP:
        new_z -= 0.5 
    elif key == GLUT_KEY_DOWN:
        new_z += 0.5
    elif key == GLUT_KEY_LEFT:
        new_x -= 0.5
    elif key == GLUT_KEY_RIGHT:
        new_x += 0.5
    
    # Check collision before moving
    if not check_collision(new_x, new_z):
        player["x"] = new_x
        player["z"] = new_z
    
    check_item_collision()
    glutPostRedisplay()

# ---------------------------
# Main
# ---------------------------

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"3D Maze with Isometric View - PyOpenGL")
    
    # Set initial player position to a valid empty space
    player["x"], player["z"] = find_valid_start()

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)

    print("3D Maze with Isometric View")
    print("Controls:")
    print("Arrow Keys: Move through the maze")
    print("I/K: Zoom in/out")
    print("J/L: Rotate the isometric view")
    print("R: Reset position")
    print("B: Hold 'B' key when colliding with a bomb to score +1 instead of -1")
    print("ESC: Quit")

    glutMainLoop()

if __name__ == "__main__":
    main()
