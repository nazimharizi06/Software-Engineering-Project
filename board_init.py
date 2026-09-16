import pygame

pygame.init()
window_width = 1280
window_height = 720
grid_size = 5

screen = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
running = True
dt = 0

map = pygame.image.load('poly_map.png')
map = pygame.transform.scale(map, (window_width, window_height))

cell_width = window_width / grid_size
cell_height = window_height / grid_size

player_x = 2
player_y = 2

lucky_x = 0
lucky_y = 0

#player_pos = pygame.Vector2(screen.get_width()/2, screen.get_height()/2)
player_grid_pos = [player_x, player_y]
lucky_grid_pos = [lucky_x, lucky_y] 

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
    
    screen.fill("white")
    screen.blit(map, (0,0))
    pygame.display.update()

    for i in range(grid_size + 1):
        x = int(i * cell_width)
        y = int(i * cell_height)
        
        pygame.draw.line(screen, "black", (x,0), (x, window_height), 2)
        pygame.draw.line(screen, "black", (0,y), (window_width, y), 2)
        
    player_x = (player_grid_pos[0] + 0.5) * cell_width
    player_y = (player_grid_pos[1] + 0.5) * cell_height

    lucky_x = (lucky_grid_pos[0] + 0.5) * cell_width
    lucky_y = (lucky_grid_pos[1] + 0.5) * cell_height

    #if keys[pygame.K_SPACE]:
    #    screen.fill("green")

    #pygame.draw.circle(screen, "black", player_pos, 10)
    pygame.draw.circle(screen, "blue", (int(player_x), int(player_y)), 16)
    pygame.draw.circle(screen, "green", (int(lucky_x), int(lucky_y)), 16)

    #if keys[pygame.K_w]:
    #    player_pos.y -= 300*dt
    #if keys[pygame.K_s]:
    #    player_pos.y += 300*dt
    #if keys[pygame.K_d]:
    #    player_pos.x += 300*dt
    #if keys[pygame.K_a]:
    #    player_pos.x -= 300*dt

    pygame.display.flip()

    dt = clock.tick(60)/1000

pygame.quit()
