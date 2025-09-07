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

# Player and game state
player = {"x": 0.0, "y": 0.5, "z": 5.0}
game_over = False
win = False
score = 0
start_time = time.time()
last_update_time = time.time()
countdown_time = 15.0

# Stone settings
stones = []
STONE_SPEED = 0.5
STONE_SPAWN_INTERVAL = 0.5  # Spawn a new stone every 0.5 seconds
last_spawn_time = 0

# Environment size
ENV_SIZE = 60.0 # Increased size for a longer course
GOAL_Z = -50.0 # Moved the goal farther away

# ---------------------------
# Drawing
# ---------------------------

def draw_ground():
    """Draws a grid for the ground."""
    glColor3f(0.1, 0.6, 0.1)  # green ground
    glBegin(GL_QUADS)
    glVertex3f(-ENV_SIZE / 2, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE / 2, 0, -ENV_SIZE)
    glVertex3f(ENV_SIZE / 2, 0, ENV_SIZE)
    glVertex3f(-ENV_SIZE / 2, 0, ENV_SIZE)
    glEnd()
    
    # Draw grid lines
    glColor3f(0.2, 0.5, 0.2)
    glBegin(GL_LINES)
    for i in range(-int(ENV_SIZE / 2), int(ENV_SIZE / 2) + 1, 2):
        glVertex3f(i, 0.01, -ENV_SIZE)
        glVertex3f(i, 0.01, ENV_SIZE)
        glVertex3f(-ENV_SIZE, 0.01, i)
        glVertex3f(ENV_SIZE, 0.01, i)
    glEnd()

    # Draw the finish line
    glColor3f(1.0, 1.0, 1.0) # White finish line
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3f(-ENV_SIZE / 2, 0.02, GOAL_Z)
    glVertex3f(ENV_SIZE / 2, 0.02, GOAL_Z)
    glEnd()
    glLineWidth(1.0)

def draw_player():
    """Draws the player as a colored cube."""
    glColor3f(1.0, 0.0, 0.0)  # red player
    glPushMatrix()
    glTranslatef(player["x"], 0.5, player["z"])
    glScalef(0.5, 1.0, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_stones():
    """Draws the rolling stones as solid spheres with different colors."""
    for stone in stones:
        if stone["type"] == "yellow":
            glColor3f(1.0, 1.0, 0.0)  # yellow stone
        else:
            glColor3f(0.5, 0.5, 0.5)  # gray stone
        glPushMatrix()
        glTranslatef(stone["x"], 0.5, stone["z"])
        glutSolidSphere(0.8, 16, 16)
        glPopMatrix()

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
# Game Logic
# ---------------------------

def spawn_stone():
    """Spawns a new stone at the far end of the environment, with a chance to be yellow."""
    x = random.uniform(-ENV_SIZE / 2 + 2, ENV_SIZE / 2 - 2)
    z = -ENV_SIZE / 2 - 10.0  # Start far away but within view
    stone_type = "yellow" if random.random() < 0.2 else "gray"  # 20% chance for yellow stone
    stones.append({"x": x, "z": z, "type": stone_type})

def update_game_state():
    """Updates the position of all stones and handles spawning and scoring."""
    global game_over, score, last_spawn_time, win, last_update_time, countdown_time
    global stones
    if not game_over:
        # Update countdown timer
        current_time = time.time()
        delta_time = current_time - last_update_time
        last_update_time = current_time
        countdown_time -= delta_time
        
        # Check for win or lose conditions
        if player["z"] <= GOAL_Z:
            game_over = True
            win = True
        elif countdown_time <= 0:
            game_over = True
            win = False
        
        # Move stones towards the player
        for stone in stones:
            stone["z"] += STONE_SPEED

        # Remove stones that have passed the player
        
        stones = [stone for stone in stones if stone["z"] < player["z"] + 10]
        
        # Spawn new stones
        if current_time - last_spawn_time > STONE_SPAWN_INTERVAL:
            spawn_stone()
            last_spawn_time = current_time

        check_collision()
    
    glutPostRedisplay()

def check_collision():
    """Checks for collisions between the player and any stone and updates score based on stone color."""
    global score
    player_radius = 0.5
    stone_radius = 0.8
    
    for stone in stones:
        distance = math.sqrt((player["x"] - stone["x"])**2 + (player["z"] - stone["z"])**2)
        if distance < player_radius + stone_radius:
            if stone["type"] == "yellow":
                score += 1
            else:
                score -= 1
            stones.remove(stone) # Remove the stone after collision
            
def set_third_person_camera():
    """Sets the camera to a third-person perspective behind the player."""
    gluLookAt(player["x"],           # camera x
              player["y"] + 5,       # camera y (slightly elevated)
              player["z"] + 10,      # camera z (behind player)
              player["x"],           # look at x
              player["y"],           # look at y
              player["z"],           # look at z (looking at the player)
              0, 1, 0)               # up vector

# ---------------------------
# Scene Rendering
# ---------------------------

def display():
    """Main rendering function."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_W / float(WINDOW_H), 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_third_person_camera()

    glClearColor(0.5, 0.7, 0.9, 1.0)  # blue sky
    glEnable(GL_DEPTH_TEST)

    draw_ground()
    draw_stones()
    draw_player()
    
    glDisable(GL_DEPTH_TEST)

    if game_over and win:
        draw_text("You Win! Final Score: " + str(score), WINDOW_W / 2 - 100, WINDOW_H / 2)
        draw_text("Press 'R' to play again.", WINDOW_W / 2 - 70, WINDOW_H / 2 - 30)
    elif game_over:
        draw_text("Game Over! Score: " + str(score), WINDOW_W / 2 - 100, WINDOW_H / 2)
        draw_text("Press 'R' to restart.", WINDOW_W / 2 - 70, WINDOW_H / 2 - 30)
    else:
        draw_text(f"Score: {score}", 10, WINDOW_H - 30)
        draw_text(f"Time: {int(countdown_time)}", 10, WINDOW_H - 50)
        draw_text("Arrow Keys: Move, R: Reset, ESC: Quit", 10, 10)
    
    glEnable(GL_DEPTH_TEST)

    glutSwapBuffers()

# ---------------------------
# Controls & Movement
# ---------------------------

def keyboard(key, x, y):
    """Handles keyboard presses for camera control and reset."""
    global game_over, start_time, stones, win, countdown_time
    
    key = key.decode('utf-8')
    if key == '\x1b':  # Esc
        glutLeaveMainLoop()
    elif key == 'r':  # Reset game
        game_over = False
        win = False
        start_time = time.time()
        countdown_time = 15.0
        stones = []
        player["x"] = 0.0
        player["z"] = 5.0

def special_keys(key, x, y):
    """Handles player movement based on new perspective."""
    if game_over:
        return

    if key == GLUT_KEY_LEFT:
        player["x"] = max(-ENV_SIZE / 2 + 0.5, player["x"] - 0.5)
    elif key == GLUT_KEY_RIGHT:
        player["x"] = min(ENV_SIZE / 2 - 0.5, player["x"] + 0.5)
    elif key == GLUT_KEY_UP:
        player["z"] = player["z"] - 0.5
    elif key == GLUT_KEY_DOWN:
        player["z"] = player["z"] + 0.5

# ---------------------------
# Main
# ---------------------------

def main():
    """Initializes OpenGL and starts the main loop."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Rolling Stones - PyOpenGL")
    
    # Set initial player position
    player["x"] = 0.0
    player["z"] = 5.0
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)

    print("Rolling Stones")
    print("Controls:")
    print("Arrow Keys: Move the red cube")
    print("R: Reset the game")
    print("ESC: Quit")

    while True:
        update_game_state()
        time.sleep(0.016)  # Aim for 60 FPS
        glutMainLoopEvent()

if __name__ == "__main__":
    main()
