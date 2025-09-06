import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Destiny Quest")

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 32)
font_large = pygame.font.SysFont('Arial', 48)

# Game states
WATERING_TREE = 0
SOLVING_RIDDLE = 1
TRAVELING = 2
HEALING_DRAGON = 3
MAZE = 4
CONSTELLATION = 5
GAME_OVER = 6
GAME_WON = 7

# Player properties
player_lives = 10
player_score = 0
current_state = WATERING_TREE
apples_collected = 0

# Timer properties
current_time = 0
timer_max = 60  # seconds
timer_active = False

# Watering game properties
water_level = 0
target_water_level = random.randint(30, 70)
tree_health = 100

# Riddle game properties
current_riddle = ""
current_answer = ""
scrambled_answer = ""
selected_tiles = []
answer_tiles = []

# Travel game properties
player_x = WIDTH // 2
player_y = HEIGHT - 100
fireballs = []
rocks = []
dragons = []
dragon_cooldown = 0

# Maze properties
maze = []
maze_size = 15
maze_cell_size = 40
player_maze_x = 1
player_maze_y = 1
maze_rewards = []
maze_traps = []

# Constellation properties
stars = []
lines = []
constellation_complete = False

# Initialize game elements
def init_game():
    global player_lives, player_score, current_state, apples_collected
    global current_time, timer_active, water_level, target_water_level, tree_health
    global current_riddle, current_answer, scrambled_answer, selected_tiles, answer_tiles
    global player_x, player_y, fireballs, rocks, dragons, dragon_cooldown
    global maze, player_maze_x, player_maze_y, maze_rewards, maze_traps
    global stars, lines, constellation_complete
    
    player_lives = 10
    player_score = 0
    current_state = WATERING_TREE
    apples_collected = 0
    
    current_time = 0
    timer_active = False
    
    water_level = 0
    target_water_level = random.randint(30, 70)
    tree_health = 100
    
    init_riddle()
    init_travel()
    generate_maze()
    init_constellation()

# Initialize riddle game
def init_riddle():
    global current_riddle, current_answer, scrambled_answer, selected_tiles, answer_tiles
    
    riddles = [
        {"question": "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?", "answer": "ECHO"},
        {"question": "The more you take, the more you leave behind. What am I?", "answer": "FOOTSTEPS"},
        {"question": "What has keys but can't open locks?", "answer": "PIANO"}
    ]
    
    riddle = random.choice(riddles)
    current_riddle = riddle["question"]
    current_answer = riddle["answer"]
    
    # Scramble the answer
    scrambled = list(current_answer)
    random.shuffle(scrambled)
    scrambled_answer = ''.join(scrambled)
    
    selected_tiles = []
    answer_tiles = []
    
    for i, char in enumerate(scrambled_answer):
        answer_tiles.append({
            "char": char,
            "x": 200 + i * 60,
            "y": 500,
            "width": 50,
            "height": 50
        })

# Initialize travel game
def init_travel():
    global player_x, player_y, fireballs, rocks, dragons, dragon_cooldown
    
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    fireballs = []
    rocks = []
    dragons = []
    dragon_cooldown = 0
    
    # Create some initial dragons
    for i in range(3):
        dragons.append({
            "x": random.randint(100, WIDTH - 100),
            "y": random.randint(100, 300),
            "speed": random.uniform(1, 3)
        })

# Generate maze
def generate_maze():
    global maze, maze_rewards, maze_traps, player_maze_x, player_maze_y
    
    # Initialize maze with all walls
    maze = [[1 for _ in range(maze_size)] for _ in range(maze_size)]
    
    # Generate a simple maze (primitive algorithm)
    for i in range(1, maze_size - 1):
        for j in range(1, maze_size - 1):
            if random.random() > 0.3:  # 70% chance of being a path
                maze[i][j] = 0
    
    # Ensure start and end are clear
    maze[1][1] = 0  # Start
    maze[maze_size-2][maze_size-2] = 0  # End
    
    player_maze_x = 1
    player_maze_y = 1
    
    # Generate rewards and traps
    maze_rewards = []
    maze_traps = []
    
    for i in range(5):  # 5 rewards
        x, y = random.randint(1, maze_size-2), random.randint(1, maze_size-2)
        if maze[y][x] == 0 and (x != 1 or y != 1) and (x != maze_size-2 or y != maze_size-2):
            maze_rewards.append({"x": x, "y": y, "collected": False})
    
    for i in range(8):  # 8 traps
        x, y = random.randint(1, maze_size-2), random.randint(1, maze_size-2)
        if maze[y][x] == 0 and (x != 1 or y != 1) and (x != maze_size-2 or y != maze_size-2):
            maze_traps.append({"x": x, "y": y, "active": True})

# Initialize constellation game
def init_constellation():
    global stars, lines, constellation_complete
    
    stars = []
    lines = []
    constellation_complete = False
    
    # Create stars in a dragon shape
    dragon_shape = [
        (100, 200), (150, 250), (200, 200), (250, 150), (300, 200),
        (350, 250), (400, 300), (450, 250), (500, 200), (550, 150),
        (600, 200), (650, 250), (700, 300), (750, 250), (800, 200)
    ]
    
    for i, (x, y) in enumerate(dragon_shape):
        stars.append({
            "x": x,
            "y": y,
            "connected": False,
            "index": i
        })
    
    # Define connections between stars to form a dragon
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5),
        (5, 6), (6, 7), (7, 8), (8, 9), (9, 10),
        (10, 11), (11, 12), (12, 13), (13, 14)
    ]
    
    for from_idx, to_idx in connections:
        lines.append({
            "from": from_idx,
            "to": to_idx,
            "connected": False
        })

# Draw watering mini-game
def draw_watering_game():
    # Draw sky and ground
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 200, WIDTH, 200))
    
    # Draw river
    pygame.draw.rect(screen, (0, 120, 255), (0, HEIGHT - 180, WIDTH, 30))
    
    # Draw tree
    pygame.draw.rect(screen, BROWN, (WIDTH // 2 - 30, HEIGHT - 350, 60, 150))
    pygame.draw.circle(screen, GRASS_GREEN, (WIDTH // 2, HEIGHT - 400), 100)
    
    if tree_health > 0:
        # Draw apples if tree is healthy
        for i in range(apples_collected):
            pygame.draw.circle(screen, GOLD, (WIDTH // 2 - 40 + i * 40, HEIGHT - 450), 15)
    
    # Draw water gauge
    pygame.draw.rect(screen, BLACK, (50, 100, 40, 200), 2)
    pygame.draw.rect(screen, (0, 120, 255), (50, 100 + (200 - water_level * 2), 40, water_level * 2))
    
    # Draw target indicator
    target_y = 100 + (200 - target_water_level * 2)
    pygame.draw.line(screen, RED, (40, target_y), (90, target_y), 3)
    
    # Draw instructions
    text = font_medium.render("Collect water from the river and water the tree", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))
    
    text = font_medium.render("Press SPACE to collect water, UP to pour water", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 500))
    
    # Draw tree health
    text = font_small.render(f"Tree Health: {tree_health}%", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 60, HEIGHT - 250))
    
    # Draw timer if active
    if timer_active:
        text = font_medium.render(f"Time: {int(timer_max - current_time)}", True, BLACK)
        screen.blit(text, (WIDTH - 150, 50))

# Draw riddle mini-game
def draw_riddle_game():
    screen.fill((200, 230, 255))
    
    # Draw riddle text
    text = font_medium.render("Solve the riddle to get a golden apple:", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
    
    # Wrap riddle text
    riddle_lines = []
    words = current_riddle.split()
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font_medium.size(test_line)[0] < WIDTH - 100:
            current_line = test_line
        else:
            riddle_lines.append(current_line)
            current_line = word + " "
    if current_line:
        riddle_lines.append(current_line)
    
    for i, line in enumerate(riddle_lines):
        text = font_medium.render(line, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 40))
    
    # Draw answer tiles
    for tile in answer_tiles:
        pygame.draw.rect(screen, (200, 200, 200), (tile["x"], tile["y"], tile["width"], tile["height"]))
        text = font_medium.render(tile["char"], True, BLACK)
        screen.blit(text, (tile["x"] + tile["width"] // 2 - text.get_width() // 2, 
                          tile["y"] + tile["height"] // 2 - text.get_height() // 2))
    
    # Draw selected tiles
    for i, char in enumerate(selected_tiles):
        pygame.draw.rect(screen, (150, 150, 250), (200 + i * 60, 400, 50, 50))
        text = font_medium.render(char, True, BLACK)
        screen.blit(text, (200 + i * 60 + 25 - text.get_width() // 2, 
                          400 + 25 - text.get_height() // 2))
    
    # Draw instructions
    text = font_small.render("Click on the letters to form the answer", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 350))
    
    # Draw submit button
    pygame.draw.rect(screen, (0, 150, 0), (WIDTH // 2 - 60, 600, 120, 50))
    text = font_medium.render("Submit", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 610))
    
    # Draw timer
    if timer_active:
        text = font_medium.render(f"Time: {int(timer_max - current_time)}", True, BLACK)
        screen.blit(text, (WIDTH - 150, 50))

# Draw travel mini-game
def draw_travel_game():
    screen.fill(SKY_BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 100, WIDTH, 100))
    
    # Draw cliff
    pygame.draw.rect(screen, (100, 100, 100), (WIDTH // 2 - 200, HEIGHT - 300, 400, 200))
    
    # Draw player
    pygame.draw.circle(screen, (0, 0, 255), (player_x, player_y), 20)
    
    # Draw dragons
    for dragon in dragons:
        pygame.draw.circle(screen, RED, (dragon["x"], dragon["y"]), 30)
    
    # Draw fireballs
    for fireball in fireballs:
        pygame.draw.circle(screen, (255, 165, 0), (fireball["x"], fireball["y"]), 10)
    
    # Draw rocks
    for rock in rocks:
        pygame.draw.circle(screen, (100, 100, 100), (rock["x"], rock["y"]), 15)
    
    # Draw instructions
    text = font_medium.render("Use arrow keys to move, SPACE to shoot", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))
    
    # Draw goal
    text = font_medium.render("Reach the top of the cliff to continue", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 350))

# Draw healing mini-game
def draw_healing_game():
    screen.fill(SKY_BLUE)
    
    # Draw divine dragon
    pygame.draw.circle(screen, (0, 191, 255), (WIDTH // 2, HEIGHT // 2), 100)
    
    # Draw apples
    for i in range(3):
        color = GOLD if i < apples_collected else (150, 150, 150)
        pygame.draw.circle(screen, color, (WIDTH // 2 - 100 + i * 100, HEIGHT // 2 - 150), 25)
    
    # Draw instructions
    if apples_collected < 3:
        text = font_medium.render("You need 3 golden apples to heal the dragon", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
    else:
        text = font_medium.render("Press SPACE to heal the dragon", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
    
    # Draw dragon status
    if apples_collected < 3:
        text = font_medium.render("The dragon is weak and needs your help", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))
    else:
        text = font_medium.render("The dragon is waiting for your healing apples", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))

# Draw maze mini-game
def draw_maze_game():
    screen.fill((50, 50, 50))
    
    # Draw maze
    for y in range(maze_size):
        for x in range(maze_size):
            cell_x = x * maze_cell_size
            cell_y = y * maze_cell_size
            
            if maze[y][x] == 1:  # Wall
                pygame.draw.rect(screen, (100, 100, 100), 
                                (cell_x, cell_y, maze_cell_size, maze_cell_size))
            else:  # Path
                pygame.draw.rect(screen, (200, 200, 200), 
                                (cell_x, cell_y, maze_cell_size, maze_cell_size))
    
    # Draw player
    pygame.draw.circle(screen, (0, 0, 255), 
                      (player_maze_x * maze_cell_size + maze_cell_size // 2, 
                       player_maze_y * maze_cell_size + maze_cell_size // 2), 
                      maze_cell_size // 3)
    
    # Draw rewards
    for reward in maze_rewards:
        if not reward["collected"]:
            pygame.draw.circle(screen, GOLD, 
                              (reward["x"] * maze_cell_size + maze_cell_size // 2, 
                               reward["y"] * maze_cell_size + maze_cell_size // 2), 
                              maze_cell_size // 4)
    
    # Draw traps
    for trap in maze_traps:
        if trap["active"]:
            pygame.draw.rect(screen, RED, 
                            (trap["x"] * maze_cell_size + 5, 
                             trap["y"] * maze_cell_size + 5, 
                             maze_cell_size - 10, maze_cell_size - 10))
    
    # Draw goal (center of maze)
    pygame.draw.rect(screen, (0, 255, 0), 
                    ((maze_size-2) * maze_cell_size + 5, 
                     (maze_size-2) * maze_cell_size + 5, 
                     maze_cell_size - 10, maze_cell_size - 10))
    
    # Draw instructions
    text = font_medium.render("Use arrow keys to navigate the maze", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))
    
    text = font_medium.render("Collect gold rewards and avoid red traps", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))

# Draw constellation mini-game
def draw_constellation_game():
    screen.fill((0, 0, 50))  # Dark blue background for night sky
    
    # Draw stars
    for star in stars:
        color = (255, 255, 100) if star["connected"] else (255, 255, 255)
        pygame.draw.circle(screen, color, (star["x"], star["y"]), 8)
    
    # Draw lines between connected stars
    for line in lines:
        if line["connected"]:
            from_star = stars[line["from"]]
            to_star = stars[line["to"]]
            pygame.draw.line(screen, (255, 255, 100), 
                            (from_star["x"], from_star["y"]), 
                            (to_star["x"], to_star["y"]), 3)
    
    # Draw instructions
    text = font_medium.render("Connect the stars to form the dragon constellation", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))
    
    text = font_medium.render("Click on stars to connect them in order", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
    
    # Draw complete button if constellation is complete
    if constellation_complete:
        pygame.draw.rect(screen, (0, 150, 0), (WIDTH // 2 - 60, HEIGHT - 100, 120, 50))
        text = font_medium.render("Complete", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 90))

# Draw game over screen
def draw_game_over():
    screen.fill((50, 0, 0))
    text = font_large.render("GAME OVER", True, RED)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    
    text = font_medium.render("Press R to restart", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))

# Draw game won screen
def draw_game_won():
    screen.fill((0, 50, 0))
    text = font_large.render("YOU WIN!", True, GOLD)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    
    text = font_medium.render(f"Final Score: {player_score}", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 20))
    
    text = font_medium.render("Press R to play again", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 80))

# Draw HUD with lives and score
def draw_hud():
    # Draw lives
    text = font_medium.render(f"Lives: {player_lives}", True, BLACK)
    screen.blit(text, (20, 20))
    
    # Draw score
    text = font_medium.render(f"Score: {player_score}", True, BLACK)
    screen.blit(text, (20, 60))
    
    # Draw apples collected
    for i in range(apples_collected):
        pygame.draw.circle(screen, GOLD, (WIDTH - 40 - i * 30, 40), 15)

# Update watering mini-game
def update_watering_game(keys, dt):
    global water_level, tree_health, current_state, timer_active, current_time, player_score, player_lives, apples_collected
    
    # Collect water from river
    if keys[pygame.K_SPACE] and water_level < 100:
        water_level += 0.5
    
    # Pour water on tree
    if keys[pygame.K_UP] and water_level > 0:
        water_level -= 0.5
        tree_health -= abs(water_level - target_water_level) * 0.1
        
        # Check if watering is correct
        if abs(water_level - target_water_level) < 5:
            player_score += 20
        else:
            player_score -= 5
    
    # Check if tree is dead
    if tree_health <= 0:
        player_lives -= 1
        player_score -= 50
        tree_health = 100
        target_water_level = random.randint(30, 70)
    
    # Check if tree is fully grown
    if tree_health >= 100:
        current_state = SOLVING_RIDDLE
        timer_active = True
        current_time = 0
    
    # Update timer
    if timer_active:
        current_time += dt / 1000
        if current_time >= timer_max:
            timer_active = False
            player_lives -= 1
            player_score -= 50
            tree_health = 100
            target_water_level = random.randint(30, 70)

# Update riddle mini-game
def update_riddle_game(events, dt):
    global current_state, timer_active, current_time, player_score, player_lives, apples_collected, selected_tiles
    
    # Handle tile selection
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            # Check if submit button was clicked
            if WIDTH // 2 - 60 <= x <= WIDTH // 2 + 60 and 600 <= y <= 650:
                # Check if answer is correct
                player_answer = ''.join(selected_tiles)
                if player_answer == current_answer:
                    player_score += 50
                    apples_collected += 1
                    
                    if apples_collected >= 3:
                        current_state = TRAVELING
                        init_travel()
                    else:
                        current_state = WATERING_TREE
                        tree_health = 100
                        target_water_level = random.randint(30, 70)
                else:
                    player_lives -= 1
                    player_score -= 50
                    selected_tiles = []
            
            # Check if a tile was clicked
            for tile in answer_tiles:
                if tile["x"] <= x <= tile["x"] + tile["width"] and \
                   tile["y"] <= y <= tile["y"] + tile["height"]:
                    if tile["char"] not in selected_tiles:
                        selected_tiles.append(tile["char"])
    
    # Update timer
    if timer_active:
        current_time += dt / 1000
        if current_time >= timer_max:
            timer_active = False
            player_lives -= 1
            player_score -= 50
            selected_tiles = []
            current_state = WATERING_TREE
            tree_health = 100
            target_water_level = random.randint(30, 70)

# Update travel mini-game
def update_travel_game(keys, dt):
    global player_x, player_y, fireballs, rocks, dragons, dragon_cooldown
    global current_state, player_score, player_lives
    
    # Move player
    if keys[pygame.K_LEFT] and player_x > 30:
        player_x -= 5
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 30:
        player_x += 5
    if keys[pygame.K_UP] and player_y > 30:
        player_y -= 5
    if keys[pygame.K_DOWN] and player_y < HEIGHT - 30:
        player_y += 5
    
    # Shoot fireballs
    dragon_cooldown -= dt
    if keys[pygame.K_SPACE] and dragon_cooldown <= 0:
        fireballs.append({"x": player_x, "y": player_y, "speed": 10})
        dragon_cooldown = 500  # 500ms cooldown
    
    # Update fireballs
    for fireball in fireballs[:]:
        fireball["y"] -= fireball["speed"]
        if fireball["y"] < 0:
            fireballs.remove(fireball)
    
    # Update dragons
    for dragon in dragons[:]:
        dragon["x"] += dragon["speed"]
        if dragon["x"] > WIDTH or dragon["x"] < 0:
            dragon["speed"] *= -1
        
        # Check if dragon hits player
        if math.sqrt((dragon["x"] - player_x)**2 + (dragon["y"] - player_y)**2) < 50:
            player_lives -= 1
            player_score -= 50
            dragons.remove(dragon)
    
    # Generate rocks
    if random.random() < 0.02:
        rocks.append({"x": random.randint(100, WIDTH - 100), "y": 0, "speed": random.uniform(2, 5)})
    
    # Update rocks
    for rock in rocks[:]:
        rock["y"] += rock["speed"]
        if rock["y"] > HEIGHT:
            rocks.remove(rock)
        
        # Check if rock hits player
        if math.sqrt((rock["x"] - player_x)**2 + (rock["y"] - player_y)**2) < 35:
            player_lives -= 1
            player_score -= 50
            rocks.remove(rock)
    
    # Check if player reached the top of the cliff
    if player_y < HEIGHT - 300 and WIDTH // 2 - 200 < player_x < WIDTH // 2 + 200:
        player_score += 100
        current_state = HEALING_DRAGON

# Update healing mini-game
def update_healing_game(keys):
    global current_state, player_score
    
    if apples_collected >= 3 and keys[pygame.K_SPACE]:
        player_score += 20
        current_state = MAZE

# Update maze mini-game
def update_maze_game(keys):
    global player_maze_x, player_maze_y, current_state, player_score, player_lives, maze_rewards, maze_traps
    
    # Move player
    new_x, new_y = player_maze_x, player_maze_y
    
    if keys[pygame.K_LEFT]:
        new_x -= 1
    if keys[pygame.K_RIGHT]:
        new_x += 1
    if keys[pygame.K_UP]:
        new_y -= 1
    if keys[pygame.K_DOWN]:
        new_y += 1
    
    # Check if movement is valid
    if 0 <= new_x < maze_size and 0 <= new_y < maze_size and maze[new_y][new_x] == 0:
        player_maze_x, player_maze_y = new_x, new_y
        
        # Check for rewards
        for reward in maze_rewards:
            if not reward["collected"] and reward["x"] == player_maze_x and reward["y"] == player_maze_y:
                reward["collected"] = True
                player_score += random.randint(10, 20)
        
        # Check for traps
        for trap in maze_traps:
            if trap["active"] and trap["x"] == player_maze_x and trap["y"] == player_maze_y:
                player_lives -= 1
                player_score -= 50
                trap["active"] = False
        
        # Check if player reached the center
        if player_maze_x == maze_size - 2 and player_maze_y == maze_size - 2:
            player_score += 100
            current_state = CONSTELLATION

# Update constellation mini-game
def update_constellation_game(events):
    global current_state, player_score, player_lives, stars, lines, constellation_complete
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            # Check if complete button was clicked
            if constellation_complete and WIDTH // 2 - 60 <= x <= WIDTH // 2 + 60 and HEIGHT - 100 <= y <= HEIGHT - 50:
                current_state = GAME_WON
                return
            
            # Check if a star was clicked
            for star in stars:
                if math.sqrt((star["x"] - x)**2 + (star["y"] - y)**2) < 15:
                    if not star["connected"]:
                        star["connected"] = True
                        
                        # Check if this completes any lines
                        for line in lines:
                            if not line["connected"]:
                                from_star = stars[line["from"]]
                                to_star = stars[line["to"]]
                                
                                if from_star["connected"] and to_star["connected"]:
                                    line["connected"] = True
                        
                        # Check if all lines are connected
                        constellation_complete = all(line["connected"] for line in lines)
                    break

# Main game loop
def main():
    global current_time, timer_active, player_lives, player_score, current_state
    
    clock = pygame.time.Clock()
    running = True
    
    init_game()
    
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (current_state == GAME_OVER or current_state == GAME_WON):
                    init_game()
        
        keys = pygame.key.get_pressed()
        
        # Update game state based on current state
        if current_state == WATERING_TREE:
            update_watering_game(keys, dt)
        elif current_state == SOLVING_RIDDLE:
            update_riddle_game(events, dt)
        elif current_state == TRAVELING:
            update_travel_game(keys, dt)
        elif current_state == HEALING_DRAGON:
            update_healing_game(keys)
        elif current_state == MAZE:
            update_maze_game(keys)
        elif current_state == CONSTELLATION:
            update_constellation_game(events)
        
        # Check for game over
        if player_lives <= 0:
            current_state = GAME_OVER
        
        # Draw everything
        if current_state == WATERING_TREE:
            draw_watering_game()
        elif current_state == SOLVING_RIDDLE:
            draw_riddle_game()
        elif current_state == TRAVELING:
            draw_travel_game()
        elif current_state == HEALING_DRAGON:
            draw_healing_game()
        elif current_state == MAZE:
            draw_maze_game()
        elif current_state == CONSTELLATION:
            draw_constellation_game()
        elif current_state == GAME_OVER:
            draw_game_over()
        elif current_state == GAME_WON:
            draw_game_won()
        
        # Draw HUD if game is not over
        if current_state not in [GAME_OVER, GAME_WON]:
            draw_hud()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()