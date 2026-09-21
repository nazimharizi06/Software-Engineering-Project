import pygame
import random

pygame.init()
window_width = 1280
window_height = 720
grid_size = 3

screen = pygame.display.set_mode((window_width, window_height))

clock = pygame.time.Clock()
running = True
dt = 0

map = pygame.image.load('tiles/poly_map.png')
map = pygame.transform.scale(map, (window_width, window_height))

cell_width = window_width / grid_size
cell_height = window_height / grid_size

road = pygame.image.load('tiles/road.jpg')
road = pygame.transform.scale(road, (cell_width, cell_height))
grass = pygame.image.load('tiles/grass.jpg')
grass = pygame.transform.scale(grass, (cell_width, cell_height))
building = pygame.image.load('tiles/building.jpg')
building = pygame.transform.scale(building, (cell_width, cell_height))
wood_floor = pygame.image.load('tiles/wood_floor.jpg')
wood_floor = pygame.transform.scale(wood_floor, (cell_width, cell_height))

tile_dictionary = {
    0: grass,
    1: road,
    2: building,
    3: wood_floor
}

tile_map = [
    [0, 0, 2],
    [1, 1, 1],
    [0, 0, 0],
]

interior_map = [
    [3, 3, 3],
    [3, 3, 3],
    [3, 3, 3]
]

def draw_background(map):
    for row_index, row in enumerate(map):
        for col_index, tile_type in enumerate(row):
            tile_image = tile_dictionary[tile_type]
            
            x_coord = col_index * cell_width
            y_coord = row_index * cell_height
            
            screen.blit(tile_image, (x_coord, y_coord))

player_x = grid_size//2
player_y = grid_size//2

lucky_x = random.randint(0, grid_size-1)
lucky_y = random.randint(0, grid_size-1)

player_grid_pos = [player_x, player_y]
lucky_grid_pos = [lucky_x, lucky_y] 

player_in_building = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_x, mouse_y = event.pos
    
        column = int(mouse_x // cell_width)
        row = int(mouse_y // cell_height)
        column = max(0, min(column, grid_size - 1))
        row = max(0, min(row, grid_size - 1))
    
        if [column, row] != player_grid_pos:
            player_grid_pos = [column, row]
        
            lucky_grid_pos[0] += 1
        
            if lucky_grid_pos[0] >= grid_size:
                lucky_grid_pos[0] = 0
                lucky_grid_pos[1] += 1
        
            if lucky_grid_pos[1] >= grid_size:
                lucky_grid_pos[1] = 0  
                
            if tile_map[player_grid_pos[1]][player_grid_pos[0]] == 2:
                player_in_building = True
                print("Entered Buidling")
            else:
                player_in_building = False        
    
    screen.fill("white")
    
    if player_in_building:
        draw_background(interior_map)
    else:
        draw_background(tile_map)
    
    #draw_background(tile_map)
    #screen.blit(map, (0,0))
    #pygame.display.update()

    for i in range(grid_size + 1):
        x = int(i * cell_width)
        y = int(i * cell_height)
        
        pygame.draw.line(screen, "black", (x,0), (x, window_height), 2)
        pygame.draw.line(screen, "black", (0,y), (window_width, y), 2)
        
    player_x = (player_grid_pos[0] + 0.5) * cell_width
    player_y = (player_grid_pos[1] + 0.5) * cell_height

    lucky_x = (lucky_grid_pos[0] + 0.5) * cell_width
    lucky_y = (lucky_grid_pos[1] + 0.5) * cell_height

    pygame.draw.circle(screen, "blue", (int(player_x), int(player_y)), 16)
    pygame.draw.circle(screen, "green", (int(lucky_x), int(lucky_y)), 16)

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        
    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()