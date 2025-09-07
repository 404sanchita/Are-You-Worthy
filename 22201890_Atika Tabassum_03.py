from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math



cam_pos = [300,500, 350]
fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines


first_person_mode = False
third_person_mode = False


cheat_mode = False
v_cheat_mode = False
cheat_r_speed = 1.5
prev_fire_ang = None
en_in_front = 5


player_pos = [300, 300, 30]
p_angle = 0
life = 5
score = 0
bullets_missed = 0
game_over = False


enemies = []
en_max = 5
en_size = 1.0
en_size_inc = True
en_size_chng = 0.01
en_speed = .05

bullets = []
bullet_speed = 10




def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):

    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
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


def draw_grid():

    g_size = GRID_LENGTH
    cell = g_size/13
 
    glBegin(GL_QUADS)

    for i in range(13):  # 13*13 cells in total
        for j in range(13):
            x1 = i * cell
            x2 = (i+1) * cell
            y1 = j * cell            
            y2 = (j+1) * cell

            if (i+j)%2 == 0:
                glColor3f(0.8, 0.5, 1.0)  #purple
                
            else:
                glColor3f(1.0, 1.0, 1.0) 

            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
            
    glEnd()


def draw_wall():

    g_size = GRID_LENGTH
    w_height = 50
   
    # cyan (front)
    glBegin(GL_QUADS)
    glColor3f(0, 1, 1) 

    glVertex3f(0, 0, 0)
    glVertex3f(g_size, 0, 0)
    glVertex3f(g_size, 0, w_height)
    glVertex3f(0, 0, w_height)
    
    
    glEnd()

    # white (back)
    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    glVertex3f(0, g_size, 0)
    glVertex3f(g_size, g_size, 0)
    glVertex3f(g_size, g_size, w_height)
    glVertex3f(0, g_size, w_height)
    glEnd()

    # green (right)
    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(0, g_size, 0)
    glVertex3f(0, g_size, w_height)
    glVertex3f(0, 0, w_height)
    glEnd()    

    # blue (left)    
    glColor3f(0, 0, 1) 
    glBegin(GL_QUADS)
    glVertex3f(g_size, 0, 0)
    glVertex3f(g_size, g_size, 0)
    glVertex3f(g_size, g_size, w_height)
    glVertex3f(g_size, 0, w_height)
    glEnd()


def draw_player():

    glPushMatrix()
    glColor3f(0.2, 0.4, 0.2) 
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])

    if game_over:
        glRotatef(p_angle+270, 0, 1, 0)
    else:
        glRotatef(p_angle, 0, 0, 1)


    #body
    glTranslatef(0, 0, 20 )
    glScalef(.5,.5,1.5) 
    glutSolidCube(30)


    #head
    if not third_person_mode:
       glPushMatrix()
       glColor3f(0, 0, 0)
       glTranslatef(0, 0, 25)        
       gluSphere(gluNewQuadric(), 10, 15, 15)
       glPopMatrix()


    #hands
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.6)
    glTranslatef(10, 15, 0)
    glRotatef(90, 0, 1, 0)     
    gluCylinder(gluNewQuadric(), 10, 2, 30, 15, 10)
    glPopMatrix()


    glPushMatrix()
    glColor3f(0.8, 0.6, 0.6) 
    glTranslatef(10, -15, 0)
    glRotatef(90, 0, 1, 0)    
    gluCylinder(gluNewQuadric(), 10, 2, 30, 15, 10)
    glPopMatrix()


    # Left leg
    glPushMatrix()
    glColor3f(0, 0, 1) 
    glTranslatef(0, 15, -10)     
    glRotatef(180, 0, 1, 0) 
    gluCylinder(gluNewQuadric(), 10, 5, 30, 15, 10)
    glPopMatrix()


    # Right leg
    glPushMatrix()
    glColor3f(0, 0, 1)  
    glTranslatef(0, -15, -10)    
    glRotatef(180, 0, 1, 0) 
    gluCylinder(gluNewQuadric(), 10, 5, 30, 15, 10)
    glPopMatrix()


    #gun 
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glTranslatef(10, 0, 0)
    glRotatef(90, 0, 1, 0)    
    gluCylinder(gluNewQuadric(), 10, 7, 40, 15, 10)
    glPopMatrix()
    glPopMatrix()    



def draw_enemies():

    for en in enemies:
        glPushMatrix()
        glTranslatef(en[0], en[1], en[2])
       
       #red sphere
        glColor3f(1, 0, 0) 
        gluSphere(gluNewQuadric(), 20 * en_size, 20, 20)

        #black sphere
        glColor3f(0, 0, 0) 
        glTranslatef(0, 0, 30 * en_size)
        gluSphere(gluNewQuadric(), 10 * en_size, 10, 10)

        glPopMatrix()


def enemy_spawn():

    global enemies
    enemies = []
    for i in range(en_max):
        x = random.randint(30, GRID_LENGTH - 30)
        y = random.randint(30, GRID_LENGTH - 30)
        enemies.append([x, y, 30])

def enemy_respawn(enemy_index):

    x = random.randint(30, GRID_LENGTH - 30)
    y = random.randint(30, GRID_LENGTH - 30)
    while math.hypot(x - player_pos[0] , y - player_pos[1]) < 100:
        x = random.randint(30, GRID_LENGTH - 30)
        y = random.randint(30, GRID_LENGTH - 30)
    enemies[enemy_index] = [x, y, 30]
    
def enemies_update():
    global enemies, en_size, en_size_inc, life

    if en_size_inc:
        en_size += en_size_chng
        if en_size >= 1:
            en_size_inc = False
    else:
        en_size -= en_size_chng
        if en_size <= 0.5:
            en_size_inc = True
   
    for i, en in enumerate(enemies):
        dx = player_pos[0]-en[0]
        dy = player_pos[1]-en[1]
        space = math.hypot(dx + dy)

        if space > 0:
            en[0] += en_speed*(dx/space)
            en[1] += en_speed*(dy/space)

            if space < 50:
                life -= 1
                print(f" Remaining Player Life: {life}")
                enemy_respawn(i)
                if life <= 0:
                    game_end()


def draw_bullet():

    for bullet in bullets:
        glPushMatrix()
        glColor3f(1, 0, 0) 
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glutSolidCube(8)
        glPopMatrix()

def bullet_firing():

    if game_over:
        return None

    angle_rad = math.radians(p_angle)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    gun_len = 8
    fire_x = player_pos[0] + dx * gun_len
    fire_y = player_pos[1] + dy * gun_len
    fire_z = player_pos[2] + 10 
    bullets.append([fire_x, fire_y, fire_z, dx, dy])

def collision(x1, y1, z1, w1, h1, d1, x2, y2, z2, w2, h2, d2):

    return (x1 < x2+w2 and x1+w1 > x2 and
            y1 < y2+h2 and y1+h1 > y2 and
            z1 < z2+d2 and z1+d1 > z2)

def collision_check(bullet, enemy):

    b_w = 8
    b_h = 8
    b_d = 8
    
    b_x = bullet[0] - b_w/2
    b_y = bullet[1] - b_h/2
    b_z = bullet[2] - b_d/2

    en_w = 50
    en_h = 50
    en_d = 50

    en_x = enemy[0] - en_w/2
    en_y = enemy[1] - en_h/2
    en_z = enemy[2] - en_d/2
    
    return collision(b_x, b_y, b_z, b_w, b_h, b_d,
                    en_x, en_y, en_z, en_w, en_h, en_d)


def bullets_update():
    global bullets, enemies, bullets_missed, score

    bullets_clear = []
    if bullets_missed >= 10:
        game_end()

    for i, bullet in enumerate(bullets):
        bullet[0] += bullet[3] * bullet_speed
        bullet[1] += bullet[4] * bullet_speed
        hit = False

        for j, en in enumerate(enemies):
             if collision_check(bullet, en):
                hit = True
                enemy_respawn(j)
                score += 1
                break

        if not(0 <= bullet[0] <= GRID_LENGTH and 0 <= bullet[1] <= GRID_LENGTH):
            bullets_clear.append(i)            
            bullets_missed += 1
            print(f"Player Bullet Missed: {bullets_missed}")
        elif hit:
             bullets_clear.append(i)   

    for i in reversed(bullets_clear):     
            bullets.pop(i)
   


def cheat_mode_on():  

    global p_angle, prev_fire_ang, en_in_front

    if cheat_mode and not game_over:
        p_angle = (p_angle + cheat_r_speed) % 360

        target_en = None
        target_angle_diff = 360

        for en in enemies:
            dx = en[0] - player_pos[0]
            dy = en[1] - player_pos[1]

            en_angle = math.degrees(math.atan2(dy, dx)) % 360
            angle_diff = (en_angle - p_angle + 180) % 360 - 180

            if abs(angle_diff) < abs(target_angle_diff):
                target_angle_diff = angle_diff
                target_en = en
              
        if target_en and target_angle_diff < en_in_front:
            if prev_fire_ang is None or abs((p_angle - prev_fire_ang + 180) % 360 - 180) > en_in_front:
                bullet_firing()
                prev_fire_ang = p_angle
           



def game_end():

    global game_over

    game_over = True
    bullets.clear()

def game_reset():

    global player_pos, p_angle,bullets, cheat_mode, v_cheat_mode, life, score, bullets_missed, game_over

    player_pos = [300, 300, 30]
    p_angle = 0

    game_over = False

    life = 5
    score = 0
    bullets_missed = 0
    
    enemy_spawn()
    bullets = []
    cheat_mode = False
    v_cheat_mode = False
    
    
    
    
    


def keyboardListener(key, x, y):

    global player_pos, p_angle, cheat_mode, v_cheat_mode

    m_speed = 8
    r_speed = 3

    # Move forward (w key)
    if key == b'w' and not game_over:
        angle_rad = math.radians(p_angle)        
        front_x = player_pos[0] + m_speed * math.cos(angle_rad)
        front_y = player_pos[1] + m_speed * math.sin(angle_rad)

        if 30 < front_x < GRID_LENGTH - 30 and 30 < front_y < GRID_LENGTH - 30:
            player_pos[0] = front_x
            player_pos[1] = front_y

    # Move backward (s key)
    if key == b's' and not game_over:
        angle_rad = math.radians(p_angle)        
        back_x = player_pos[0] - m_speed * math.cos(angle_rad)
        back_y = player_pos[1] - m_speed * math.sin(angle_rad)

        if 30 < back_x < GRID_LENGTH - 30 and 30 < back_y < GRID_LENGTH - 30:
            player_pos[0] = back_x
            player_pos[1] = back_y

    # rotate gun left (a key)
    if key == b'a' and not game_over and not cheat_mode:
        p_angle = (p_angle + r_speed) % 360

    # rotate gun right (d key)
    if key == b'd' and not game_over and not cheat_mode:
        p_angle = (p_angle - r_speed) % 360


    # toggle cheat mode (c key)
    if key == b'c':
        cheat_mode = not cheat_mode
        if not cheat_mode:
            v_cheat_mode = False

    # toggle cheat vision (v key)
    if key == b'v'and cheat_mode:
        v_cheat_mode = not v_cheat_mode
    if v_cheat_mode:
        cam_pos[0] = 100;
        cam_pos[1] = 100;
        cam_pos[2] = 50
    else:
        cam_pos[0] = 300;
        cam_pos[1] = 500;
        cam_pos[2] = 350

    # reset game (r key)
    if key == b'r' and game_over:
        game_reset()
    

    glutPostRedisplay()
    

def specialKeyListener(key, x, y):

    global cam_pos
    
    if key == GLUT_KEY_UP:
        cam_pos[1] += 1
    elif key == GLUT_KEY_DOWN:
        cam_pos[1] -= 1
    elif key == GLUT_KEY_LEFT:
        cam_pos[0] -= 1
    elif key == GLUT_KEY_RIGHT:
        cam_pos[0] += 1

def mouseListener(button, state, x, y):

    global first_person_mode, third_person_mode

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        bullet_firing()
        print(f"Player Bullet Fired!")
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode
        third_person_mode= first_person_mode


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


    if first_person_mode:
        angle_rad = math.radians(p_angle)
        cam_x = player_pos[0] + 2
        cam_y = player_pos[1]
        cam_z = player_pos[2] + 50  
        l_x = cam_x + math.cos(angle_rad)
        l_y = cam_y + math.sin(angle_rad)
        l_z = cam_z
        gluLookAt(cam_x, cam_y, cam_z,
                  l_x, l_y, l_z,
                  0, 0, 1)
        
    elif v_cheat_mode: # when v key is pressed
        cam_x = player_pos[0] + 5
        cam_y = player_pos[1]
        cam_z = player_pos[2] + 150  
        l_x = player_pos[0] + 100 
        l_y = player_pos[1]
        l_z = player_pos[2] + 50
        gluLookAt(cam_x, cam_y, cam_z,
                l_x, l_y, l_z,
                0, 0, 1)
    else:
        # defalut/ third-person
        x, y, z = cam_pos
        gluLookAt(x, y, z,
                  300, 180, 0,
                  0, 0, 1)
        



def idle():
    if not game_over:
        enemies_update()
        bullets_update()
        cheat_mode_on()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size
    setupCamera()  # Configure camera perspective
    draw_grid()
    draw_wall()
    draw_player()
    draw_enemies()
    draw_bullet()

    if game_over:
        draw_text(15, 730, f"GAME OVER. Your Score is {score}")
        draw_text(15, 700, "Press "R" to Restart the Game")
    else:
        draw_text(15, 760, f"Player Life Remaining: {life}")
        draw_text(15, 730, f"Game Score: {score}")
        draw_text(15, 700, f"Player Bullet Missed: {bullets_missed}")
        
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    window = glutCreateWindow(b"Bullet Frenzy")  # Create the window
    enemy_spawn()
    game_reset()
    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically
    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()    