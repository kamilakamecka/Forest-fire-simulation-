import pygame
import numpy as np
import random

pygame.init()


WINDOW_WIDTH, WINDOW_HEIGHT = 800, 500
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Symulacja Rozprzestrzeniania Ognia")

COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_GRAY = (169, 169, 169)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)

COLOR_WHITE = (255, 255, 255)

GRID_SIZE = 3
GRID_WIDTH = (WINDOW_WIDTH - 200) // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

SPREAD_CHANCE = 0.85
humidity = 0.75

MODE_FIRE = 1
MODE_WATER = 2
MODE_ROAD = 3
current_mode = MODE_FIRE

wind_direction = (0,-1)


def load_map(image_path):
    try:
        map_image = pygame.image.load(image_path)
        map_image = pygame.transform.scale(map_image, (WINDOW_WIDTH - 200, WINDOW_HEIGHT))
        map_data = pygame.surfarray.array3d(map_image).swapaxes(0, 1)
        grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                r, g, b = map_data[y * GRID_SIZE, x * GRID_SIZE]
                if r < 150:
                    grid[y, x] = -1
                elif r > 215:
                    grid[y, x] = 0
                else:
                    grid[y, x] = 1
        return grid
    except pygame.error as e:
        print(f"Błąd podczas wczytywania obrazu: {e}")
        return None

grid = load_map("Map.JPG")

fire_points = []

def draw_map():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 0:
                color = COLOR_BLACK  # Niedostępny teren
            elif grid[y, x] == 1:
                color = COLOR_GREEN  # Zielony
            elif grid[y, x] == 2:
                color = COLOR_RED  # Płonący
            elif grid[y, x] == 3:
                color = COLOR_GRAY  # Wypalony
            elif grid[y, x] == -1:
                color = COLOR_BLUE  # Woda
            pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))


def spread_fire():
    global grid, fire_points, wind_direction, humidity
    new_fire_points = []
    for y, x in fire_points:
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH:
                if grid[ny, nx] == 1 and random.random() < SPREAD_CHANCE * humidity:
                    if wind_direction == (0, 0):
                        spread_factor = 0.8
                    elif (dy, dx) == wind_direction:
                        spread_factor = 1.5
                    else:
                        spread_factor = 0.5
                    if random.random() < spread_factor * SPREAD_CHANCE:
                        grid[ny, nx] = 2
                        new_fire_points.append((ny, nx))
        grid[y, x] = 3
    fire_points = new_fire_points



def extinguish_fire():
    global grid, wind_direction
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == -1:
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH and grid[ny, nx] == 2:
                            #  jeśłi ogień jest w sąsiedztwie wody, to gasimy go
                            grid[ny, nx] = 1

                            if wind_direction == (0, 0):
                                continue
                            elif wind_direction == (0, -1) and dy == 1:
                                grid[ny, nx] = 2
                            elif wind_direction == (0, 1) and dy == -1:
                                grid[ny, nx] = 2
                            elif wind_direction == (1, 0) and dx == -1:
                                grid[ny, nx] = 2
                            elif wind_direction == (-1, 0) and dx == 1:
                                grid[ny, nx] = 2


def handle_click(mouse_x, mouse_y):
    grid_x = mouse_x // GRID_SIZE
    grid_y = mouse_y // GRID_SIZE
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        if current_mode == MODE_FIRE and grid[grid_y, grid_x] == 1:
            grid[grid_y, grid_x] = 2  #zmien na ogien
            fire_points.append((grid_y, grid_x))
        elif current_mode == MODE_WATER:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    ny, nx = grid_y + dy, grid_x + dx
                    if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH:
                        grid[ny, nx] = -1  #zmien na wode
        elif current_mode == MODE_ROAD and grid[grid_y, grid_x] == 1:
            grid[grid_y, grid_x] = 0  # Zmień na drogę



def calculate_fire_percentage():
    total_green_cells = 0
    burned_cells = 0
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                total_green_cells += 1
            if grid[y, x] == 3:
                burned_cells += 1
    if total_green_cells == 0:
        return 0
    return (burned_cells / total_green_cells) * 100

mouse_pressed = False


def handle_mouse_motion(mouse_x, mouse_y):
    if mouse_pressed:
        grid_x = mouse_x // GRID_SIZE
        grid_y = mouse_y // GRID_SIZE
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if current_mode == MODE_ROAD and grid[grid_y, grid_x] == 1:
                grid[grid_y, grid_x] = 0
            elif current_mode == MODE_FIRE and grid[grid_y, grid_x] == 1:
                grid[grid_y, grid_x] = 2
                fire_points.append((grid_y, grid_x))
            elif current_mode == MODE_WATER:
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = grid_y + dy, grid_x + dx
                        if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH:
                            grid[ny, nx] = -1

def draw_side_panel(fire_percentage, fire_spread_speed):
    global wind_direction
    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(WINDOW_WIDTH - 200, 0, 200, WINDOW_HEIGHT))
    font = pygame.font.Font(None, 16)
    text2 = font.render(f"Suwak wilgotności", True, COLOR_WHITE)
    screen.blit(text2, (WINDOW_WIDTH - 190, 40))



    fire_button_rect = pygame.Rect(WINDOW_WIDTH - 190, 100, 150, 40)
    water_button_rect = pygame.Rect(WINDOW_WIDTH - 190, 150, 150, 40)
    road_button_rect = pygame.Rect(WINDOW_WIDTH - 190, 200, 150, 40)
    no_wind_button_rect = pygame.Rect(WINDOW_WIDTH - 190, 250, 150, 40)

    pygame.draw.rect(screen, (0, 128, 0), fire_button_rect)
    pygame.draw.rect(screen, (0, 128, 0), water_button_rect)
    pygame.draw.rect(screen, (0, 128, 0), road_button_rect)

    # Rysowanie suwaka
    slider_rect = pygame.Rect(WINDOW_WIDTH - 190, 50, 150, 20)
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)


    slider_pos = int(fire_spread_speed * (slider_rect.width - 20))
    pygame.draw.circle(screen, (0, 255, 0), (slider_rect.x + slider_pos + 10, slider_rect.y + 10), 10)  # Suwak


    speed_text = font.render(f"Prędkość ognia: {fire_spread_speed:.2f}", True, COLOR_WHITE)
    screen.blit(speed_text, (WINDOW_WIDTH - 190, 370))


    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if slider_rect.collidepoint(mouse_x, mouse_y):

            fire_spread_speed = (mouse_x - slider_rect.x) / (slider_rect.width - 20)
            if fire_spread_speed < 0.2:
                fire_spread_speed = 0.2
            if fire_spread_speed > 4:
                fire_spread_speed = 4


    if wind_direction == (0, 0):
        no_wind_button_color = (255, 255, 0)
    else:
        no_wind_button_color = (0, 255, 0)

    pygame.draw.rect(screen, no_wind_button_color, no_wind_button_rect)

    fire_text = font.render("Dodaj ogień", True, (0, 0, 255))
    water_text = font.render("Dodaj wodę", True, (0,0, 255))
    road_text = font.render("Dodaj drogę", True, (0, 0, 255))
    no_wind_text = font.render("Brak wiatru", True, (0, 0, 255))

    screen.blit(fire_text, (fire_button_rect.x + 10, fire_button_rect.y + 5))
    screen.blit(water_text, (water_button_rect.x + 10, water_button_rect.y + 5))
    screen.blit(no_wind_text, (no_wind_button_rect.x + 10, no_wind_button_rect.y + 5))
    screen.blit(road_text, (road_button_rect.x + 10, road_button_rect.y + 5))


    north_button = pygame.Rect(WINDOW_WIDTH - 190, 300, 150, 40)
    south_button = pygame.Rect(WINDOW_WIDTH - 190, 350, 150, 40)
    east_button = pygame.Rect(WINDOW_WIDTH - 190, 400, 150, 40)
    west_button = pygame.Rect(WINDOW_WIDTH - 190, 450, 150, 40)


    if wind_direction == (0, -1):
        north_button_color = (255, 255, 0)
    else:
        north_button_color = (0, 255, 0)

    if wind_direction == (0, 1):
        south_button_color = (255, 255, 0)
    else:
        south_button_color = (0, 255, 0)

    if wind_direction == (1, 0):
        east_button_color = (255, 255, 0)
    else:
        east_button_color = (0, 255, 0)

    if wind_direction == (-1, 0):
        west_button_color = (255, 255, 0)
    else:
        west_button_color = (0, 255, 0)

    pygame.draw.rect(screen, north_button_color, north_button)
    pygame.draw.rect(screen, south_button_color, south_button)
    pygame.draw.rect(screen, east_button_color, east_button)
    pygame.draw.rect(screen, west_button_color, west_button)

    screen.blit(font.render("Wiatr wieje na zachód", True, (0, 0, 255)), (north_button.x + 10, north_button.y + 5))
    screen.blit(font.render("Wiatr wieje na wschód", True, (0, 0, 255)), (south_button.x + 10, south_button.y + 5))
    screen.blit(font.render("Wiatr wieje na południe", True, (0, 0, 255)), (east_button.x + 10, east_button.y + 5))
    screen.blit(font.render("Wiatr wieje na północ", True, (0, 0, 255)), (west_button.x + 10, west_button.y + 5))


    if north_button.collidepoint(pygame.mouse.get_pos()):
        wind_direction = (0, -1)
    if south_button.collidepoint(pygame.mouse.get_pos()):
        wind_direction = (0, 1)
    if east_button.collidepoint(pygame.mouse.get_pos()):
        wind_direction = (1, 0)
    if west_button.collidepoint(pygame.mouse.get_pos()):
        wind_direction = (-1, 0)
    if no_wind_button_rect.collidepoint(pygame.mouse.get_pos()):
        wind_direction = (0, 0)

    return fire_button_rect, water_button_rect, no_wind_button_rect, road_button_rect


running = True
clock = pygame.time.Clock()

while running:
    screen.fill((255, 255, 255))
    draw_map()
    fire_percentage = calculate_fire_percentage()
    draw_side_panel(fire_percentage, humidity)

    pygame.display.flip()

   #suwak
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:

        slider_rect = pygame.Rect(WINDOW_WIDTH - 190, 100, 150, 20)
        if slider_rect.collidepoint(mouse_x, mouse_y):
            humidity = (mouse_x - slider_rect.x) / (slider_rect.width - 20)
            humidity = max(0, min(humidity, 1))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pressed = True
            # Inside the main loop:
            fire_button_rect, water_button_rect, no_wind_button_rect, road_button_rect = draw_side_panel(
                fire_percentage, humidity)

            if fire_button_rect.collidepoint(mouse_x, mouse_y):
                current_mode = MODE_FIRE
            elif water_button_rect.collidepoint(mouse_x, mouse_y):
                current_mode = MODE_WATER
            elif road_button_rect.collidepoint(mouse_x, mouse_y):
                current_mode = MODE_ROAD
            elif no_wind_button_rect.collidepoint(mouse_x, mouse_y):
                wind_direction = (0, 0)
            else:
                handle_click(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            handle_mouse_motion(mouse_x, mouse_y)

    spread_fire()
    extinguish_fire()
    clock.tick(30)

pygame.quit()
