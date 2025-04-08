import pygame
import sys
import random
import os
import pickle

# Inicializacija Pygame
pygame.init()

# Dimenzije zaslona
map_x = 30
map_y = 20
width, height = map_x*32, map_y*32
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Explorer Game")

tile_size = 32
map_width, map_height = map_x, map_y

# Barve
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# FPS
clock = pygame.time.Clock()
FPS = 165

# Funkcija za pridobitev prave poti do datoteke
def resource_path(relative_path):
    try:
        # Ko teče kot .exe datoteka
        base_path = sys._MEIPASS
    except Exception:
        # Ko teče kot običajna Python datoteka
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, relative_path)

# Naloži slike pokrajine
grass_img = pygame.image.load(resource_path("images/grass.png"))
water_img = pygame.image.load(resource_path("images/water.png"))
forest_img = pygame.image.load(resource_path("images/forest.png"))
mountain_img = pygame.image.load(resource_path("images/mountain.png"))


# Naloži lik igralca
player_size = {
    "x" : tile_size // 4,
    "y" : tile_size // 2
}
try:
    player = pygame.image.load(resource_path("images/player.png"))
except FileNotFoundError:
    player = pygame.Surface((player_size["x"], player_size["y"]))
    player.fill(WHITE)
normal_speed = 4

mountian_speed = normal_speed * 0.5
player_speed = normal_speed


# generiranje chunka
def generate_chunk(chunk):
    if chunk not in map_data:
        chunk_data = []
        for row in range(map_height):
            map_row = ""
            for col in range(map_width):
                tile_type = random.choices(
                    [".", "#", "^", "~"],  # Gozd, trava, gora, voda
                    [0.50, 0.30, 0.10, 0.10]
                )[0]
                map_row += tile_type
            chunk_data.append(map_row)
        map_data[chunk] = chunk_data

# Funkcija za risanje mape
def draw_map():
    chunk_data = map_data[current_chunk]
    for row_idx, row in enumerate(chunk_data):
        for col_idx, tile in enumerate(row):
            x, y = col_idx * tile_size, row_idx * tile_size
            if tile == "#":
                screen.blit(forest_img, (x, y))  # Gozd
            elif tile == ".":
                screen.blit(grass_img, (x, y))  # Trava
            elif tile == "~":
                screen.blit(water_img, (x, y))  # Voda
            elif tile == "^":
                screen.blit(mountain_img, (x, y))  # Gora

# Shranjevanje zemljevida v datoteko
def save_map():
    with open("map_data.pkl", "wb") as f:
        pickle.dump(map_data, f)

# Funkcija za preverjanje ali je tile prehodno (ni voda)
def can_move(new_x, new_y, passthrou, direction):
    # Preverimo vse vogale igralca, da zagotovimo, da ne stopi na vodo
    player_rect = pygame.Rect(new_x, new_y, player_size["x"], player_size["y"])
    
    # Ugotovimo kateri tile igralec prekriva
    top_left_col = player_rect.left // tile_size
    if top_left_col >= map_x:
        top_left_col = 0
        passthrou = True

    top_right_col = player_rect.right // tile_size
    if top_right_col >= map_x:
        top_right_col = 0
        passthrou = True

    top_right_row = player_rect.top // tile_size
    if top_right_row >= map_y:
        top_right_row = 0
        passthrou = True

    top_left_row = player_rect.top // tile_size
    if top_left_row >= map_y:
        top_left_row = 0
        passthrou = True

    bottom_left_col = player_rect.left // tile_size
    if bottom_left_col >= map_x:
        bottom_left_col = 0
        passthrou = True

    bottom_right_col = player_rect.right // tile_size
    if bottom_right_col >= map_x:
        bottom_right_col = 0
        passthrou = True

    bottom_left_row = player_rect.bottom // tile_size
    if bottom_left_row >= map_y:
        bottom_left_row = 0
        passthrou = True

    bottom_right_row = player_rect.bottom // tile_size
    if bottom_right_row >= map_y:
        bottom_right_row = 0
        passthrou = True
    # Poskusimo dostopati do zemljevida in preverimo ali je kakšen tile voda ali gora
    chunk_data = map_data[current_chunk]

    if passthrou: # Če je igralec na robu mape
        match direction:
            case "UP":
                top_left_row = map_y - 1
                top_right_row = map_y - 1 
                next_chunk = (current_chunk[0], current_chunk[1] - 1)
                generate_chunk(next_chunk)
                chunk_data_next = map_data[next_chunk]
                # Preverimo vsak kot igralca, ali je tam voda
                if (chunk_data_next[top_left_row][top_left_col] == "~" or 
                    chunk_data_next[top_right_row][top_right_col] == "~" or 
                    chunk_data[bottom_left_row][bottom_left_col] == "~" or 
                    chunk_data[bottom_right_row][bottom_right_col] == "~"):
                    return False, "1"  # Ne more premikati čez vodo
                # Preverimo, ali je igralec na gori
                if (chunk_data_next[top_left_row][top_left_col] == "^" or 
                    chunk_data_next[top_right_row][top_right_col] == "^" or 
                    chunk_data[bottom_left_row][bottom_left_col] == "^" or 
                    chunk_data[bottom_right_row][bottom_right_col] == "^"):
                    return True, "2"  # Premik je dovoljen, vendar je na gori (upočasnitev)
                return True, "0"  # Premik je dovoljen, vendar ni na gori
            
            case "DOWN":
                bottom_left_row = 0
                bottom_right_row = 0
                next_chunk = (current_chunk[0], current_chunk[1] + 1)
                generate_chunk(next_chunk)
                chunk_data_next = map_data[next_chunk]
                # Preverimo vsak kot igralca, ali je tam voda
                if (chunk_data[top_left_row][top_left_col] == "~" or 
                    chunk_data[top_right_row][top_right_col] == "~" or 
                    chunk_data_next[bottom_left_row][bottom_left_col] == "~" or 
                    chunk_data_next[bottom_right_row][bottom_right_col] == "~"):
                    return False, "1"  # Ne more premikati čez vodo
                # Preverimo, ali je igralec na gori
                if (chunk_data[top_left_row][top_left_col] == "^" or 
                    chunk_data[top_right_row][top_right_col] == "^" or 
                    chunk_data_next[bottom_left_row][bottom_left_col] == "^" or 
                    chunk_data_next[bottom_right_row][bottom_right_col] == "^"):
                    return True, "2"  # Premik je dovoljen, vendar je na gori (upočasnitev)
                return True, "0"  # Premik je dovoljen, vendar ni na gori
            
            case "LEFT":
                bottom_left_col = map_x - 1 
                top_right_col = map_x -1 
                next_chunk = (current_chunk[0] - 1, current_chunk[1])
                generate_chunk(next_chunk)
                chunk_data_next = map_data[next_chunk]
                # Preverimo vsak kot igralca, ali je tam voda
                if (chunk_data_next[top_left_row][top_left_col] == "~" or 
                    chunk_data[top_right_row][top_right_col] == "~" or 
                    chunk_data_next[bottom_left_row][bottom_left_col] == "~" or 
                    chunk_data[bottom_right_row][bottom_right_col] == "~"):
                    return False, "1"  # Ne more premikati čez vodo
                # Preverimo, ali je igralec na gori
                if (chunk_data_next[top_left_row][top_left_col] == "^" or 
                    chunk_data[top_right_row][top_right_col] == "^" or 
                    chunk_data_next[bottom_left_row][bottom_left_col] == "^" or 
                    chunk_data[bottom_right_row][bottom_right_col] == "^"):
                    return True, "2"  # Premik je dovoljen, vendar je na gori (upočasnitev)
                return True, "0"  # Premik je dovoljen, vendar ni na gori
            
            case "RIGHT":
                top_left_col = 0
                bottom_right_col = 0
                next_chunk = (current_chunk[0] + 1, current_chunk[1])
                generate_chunk(next_chunk)
                chunk_data_next = map_data[next_chunk]
                # Preverimo vsak kot igralca, ali je tam voda
                if (chunk_data[top_left_row][top_left_col] == "~" or 
                    chunk_data_next[top_right_row][top_right_col] == "~" or 
                    chunk_data[bottom_left_row][bottom_left_col] == "~" or 
                    chunk_data_next[bottom_right_row][bottom_right_col] == "~"):
                    return False, "1"  # Ne more premikati čez vodo
                # Preverimo, ali je igralec na gori
                if (chunk_data[top_left_row][top_left_col] == "^" or 
                    chunk_data_next[top_right_row][top_right_col] == "^" or 
                    chunk_data[bottom_left_row][bottom_left_col] == "^" or 
                    chunk_data_next[bottom_right_row][bottom_right_col] == "^"):
                    return True, "2"  # Premik je dovoljen, vendar je na gori (upočasnitev)
                return True, "0"  # Premik je dovoljen, vendar ni na gori
    else: # Če ni na robu mape
        # Preverimo vsak kot igralca, ali je tam voda
        if (chunk_data[top_left_row][top_left_col] == "~" or 
            chunk_data[top_right_row][top_right_col] == "~" or 
            chunk_data[bottom_left_row][bottom_left_col] == "~" or 
            chunk_data[bottom_right_row][bottom_right_col] == "~"):
            return False, "1"  # Ne more premikati čez vodo
        # Preverimo, ali je igralec na gori
        if (chunk_data[top_left_row][top_left_col] == "^" or 
            chunk_data[top_right_row][top_right_col] == "^" or 
            chunk_data[bottom_left_row][bottom_left_col] == "^" or 
            chunk_data[bottom_right_row][bottom_right_col] == "^"):
            return True, "2"  # Premik je dovoljen, vendar je na gori (upočasnitev)
    return True, "0"  # Premik je dovoljen, vendar ni na gori


# Funkcija za iskanje varnega mesta za začetno pozicijo igralca da se ne spawna na vodi
def find_safe_start_position():
    while True:
        start_x = random.randint(0, map_width - 1)
        start_y = random.randint(0, map_height - 1)
        chunk_data = map_data[current_chunk]
        if chunk_data[start_y][start_x] != "~":  # Preveri, ali ni voda
            return start_x * tile_size, start_y * tile_size

# Generiraj mapo ali jo naloži iz datoteke
current_chunk = (0, 0)
if os.path.exists("map_data.pkl"):
    with open("map_data.pkl", "rb") as f:
        map_data = pickle.load(f)
else:
    map_data = {}
    generate_chunk(current_chunk)

# Na začetku igre najdi varno mesto za igralca
player_x, player_y = find_safe_start_position()

# Zanka igre
running = True
while running:
    screen.fill(BLACK)
    passthrou = False # Ali je igralec na robu mape
    direction = "None" 

    # Dogodki
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_map()
            running = False

    # Premik igralca
    keys = pygame.key.get_pressed()
    prev_chunk = current_chunk
    new_x, new_y = player_x, player_y

    if keys[pygame.K_UP]:
        new_y -= player_speed
        if new_y < 0:
            new_y = height - tile_size
            current_chunk = (current_chunk[0], current_chunk[1] - 1)
            passthrou = True
            direction = "UP"
    if keys[pygame.K_DOWN]:
        new_y += player_speed
        if new_y >= height:
            new_y = 0
            current_chunk = (current_chunk[0], current_chunk[1] + 1)
            passthrou = True
            direction = "DOWN"
    if keys[pygame.K_LEFT]:
        new_x -= player_speed
        if new_x < 0:
            new_x = width - tile_size
            current_chunk = (current_chunk[0] - 1, current_chunk[1])
            passthrou = True
            direction = "LEFT"
    if keys[pygame.K_RIGHT]:
        new_x += player_speed
        if new_x >= width:
            new_x = 0
            current_chunk = (current_chunk[0] + 1, current_chunk[1])
            passthrou = True
            direction = "RIGHT"

    if current_chunk != prev_chunk:
        generate_chunk(current_chunk)
    
    # Preverimo ali lahko igralec gre na novo pozicijo
    can_move_result, terrain = can_move(new_x, new_y, passthrou, direction)

    if can_move_result:
        player_x, player_y = new_x, new_y

        # Upočasnitev hitrosti, če je igralec na gori
        if terrain == "2" :
            player_speed = mountian_speed # Zmanjšana hitrost za 25%
        else:
            player_speed = normal_speed # Običajna hitrost
    passthrou = False
    direction = "None"
    

    # Izris
    generate_chunk(current_chunk) # Če je igralec na robu mape, generiraj nov chunk
    draw_map() 
    screen.blit(player, (player_x, player_y)) 
    pygame.display.set_caption(f"Explorer game, Location: {current_chunk}")
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

#KONČANO