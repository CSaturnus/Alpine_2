import pygame
import math
import random
import asyncio

pygame.init()
pygame.mixer.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SNOW_WHITE =  (255, 250, 250) 
GREEN = (0, 255, 0)
RED = (155, 28, 49)
VIOLET = (42, 0, 115)

skiier_sprite = pygame.image.load('assets/sprites/Skiier.png')
flag_sprite = pygame.image.load('assets/sprites/flag.png')
wall_1 = pygame.image.load('assets/sprites/side_1.png')
wall_2 = pygame.image.load('assets/sprites/side_2.png')

font = pygame.font.Font(None, 100)
fontsmall = pygame.font.Font(None, 20)
fontborg9 = pygame.font.Font('assets/font/Borg9.ttf', 150)
fontborg9_2 = pygame.font.Font('assets/font/Borg9.ttf', 155)

clapping =  pygame.mixer.Sound('assets/musik/clapping.ogg')
pygame.mixer.Sound.set_volume(clapping, 0.5)


WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alpine_2")

clock = pygame.time.Clock() 
FPS = 30

def generate_infinity():
    flag_pos_x = []
    flag_pos_y = []
    finish = 0
    start = 100
    for i in range(random.randint(20, 25)):
        flag_pos_x.append(random.randint(160, WIDTH - 260 - 65))
        if i == 0:
            flag_pos_y.append(1200)
        else:
            flag_pos_y.append(flag_pos_y[i - 1] + random.randint(500, 600))
    finish = flag_pos_y[-1] + 500
    return flag_pos_x, flag_pos_y, finish, start

def format_time(seconds):
    minutes = int(seconds) // 60  # Extract whole minutes
    remaining_seconds = int(seconds) % 60  # Extract whole seconds
    milliseconds = round((seconds - int(seconds)) * 1000)  # Calculate and round milliseconds
    return f"{minutes:02}:{remaining_seconds:02}:{milliseconds:03}"  # Format with leading zeroes

def get_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), (x, y, width, height))
    return sprite

def generate_map(random_seed):
    random.seed(random_seed)
    flag_pos_x = []
    flag_pos_y = []
    finish = 0
    start = 1000
    for i in range(random.randint(20, 25)):
        flag_pos_x.append(random.randint(160, WIDTH - 260 - 65))
        if i == 0:
            flag_pos_y.append(1800)
        else:
            flag_pos_y.append(flag_pos_y[i - 1] + random.randint(500, 600))
    finish = flag_pos_y[-1] + 500
    return flag_pos_x, flag_pos_y, finish, start

class Map:
    def __init__(self, random_seed, infinity_mode = False):
        self.image = flag_sprite
        self.flag_sprite_number = 0
        if infinity_mode == False:
            self.flag_pos_x, self.flag_pos_y, self.finish, self.goal = generate_map(random_seed)
        else:
            self.flag_pos_x, self.flag_pos_y, self.finish, self.goal = generate_infinity()

        self.rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
                      for x, y in zip(self.flag_pos_x, self.flag_pos_y)]
        self.rects2 = [pygame.Rect(x+150, y, self.image.get_width(), self.image.get_height())
                      for x, y in zip(self.flag_pos_x, self.flag_pos_y)]

        self.danger_zone_Left = [pygame.Rect(0, y + self.image.get_height() - 7, x, 14)
                         for x, y in zip(self.flag_pos_x, self.flag_pos_y)]
        
        self.danger_zone_Right = [pygame.Rect(x+150, y + self.image.get_height() - 7, WIDTH, 14)
                         for x, y in zip(self.flag_pos_x, self.flag_pos_y)]

        self.safe_zone = [pygame.Rect(x, y + self.image.get_height() - 7, 150, 14)
                            for x, y in zip(self.flag_pos_x, self.flag_pos_y)]
        
        self.finish_rect = pygame.Rect(0, self.finish, WIDTH, 15)
        self.start_rect = pygame.Rect(0, self.goal, WIDTH, 15)

    def display_move(self, screen, speed):
        self.flag_sprite_number += 0.3
        if self.flag_sprite_number > 3:
            self.flag_sprite_number = 0

        for i, rect in enumerate(self.rects):
            rect.y -= speed
            current_sprite = get_sprite(self.image, int(self.flag_sprite_number) * 45, 0, 45, 90)
            screen.blit(current_sprite, rect.topleft)

        for i, rect in enumerate(self.rects2):
            rect.y -= speed
            current_sprite = get_sprite(self.image, int(self.flag_sprite_number) * 45, 0, 45, 90)
            screen.blit(current_sprite, rect.topleft)

        for i, rect in enumerate(self.danger_zone_Left):
            rect.y -= speed
        for i, rect in enumerate(self.danger_zone_Right):
            rect.y -= speed
        for i, rect in enumerate(self.safe_zone):
            rect.y -= speed

    def display_start_goal(self, speed):
        self.finish -= speed
        self.goal -= speed
        self.finish_rect = pygame.Rect(0, self.finish, WIDTH, 15)
        self.start_rect = pygame.Rect(0, self.goal, WIDTH, 15)
        pygame.draw.rect(screen, (155,28,49), self.finish_rect)
        pygame.draw.rect(screen, (155,28,49), self.start_rect)
   
class Walls:
    def __init__(self, posx, posy, width, height, wall_image):
        self.posx = posx
        self.posy = posy 
        self.width = width
        self.height = height
        self.wall_image = wall_image
        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)
    
    def display(self):
        pygame.draw.rect(screen, BLACK, self.rect)
        screen.blit(self.wall_image, self.rect)

class skiier:
    def __init__(self, posx, posy, speed, angle):
        self.image = skiier_sprite
        self.posx = posx
        self.posy = posy
        self.rect = self.image.get_rect()
        self.rect.y = 100
        self.rect.x = WIDTH/2 - self.rect.width / 2
        self.speed_initial = speed
        self.speed_y = speed
        self.angle = angle
        self.angle_speed = 2
        self.height = self.rect.width
        self.height = self.rect.height
        self.direction = -1
    
    def move(self):
        
        if self.direction == -1 and self.angle < 70:
            self.angle += self.angle_speed
        elif self.direction == 1 and self.angle > -70:
            self.angle -= self.angle_speed

        self.rect.x += self.speed_initial * math.sin(math.radians(self.angle))
        self.speed_y = self.speed_initial * math.cos(math.radians(self.angle))

        self.rotated_image = pygame.transform.rotate(self.image, self.angle)

        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

    def display(self):
        screen.blit(self.rotated_image, self.rotated_rect.topleft)

class Button:
    def __init__(self, posx, posy, width, height, text):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text
        self.colour = BLACK
        self.text_render = font.render(self.text, True, self.colour)
        self.rect_1 = pygame.Rect(self.posx, self.posy, self.width, self.height)
        self.rect_1.centerx = self.posx
        self.rect_2 = pygame.Rect(self.posx+5, self.posy+5, self.width-10, self.height-10)
        self.rect_2.centerx = self.posx
        self.text_rect = self.text_render.get_rect(center=self.rect_2.center)

    def display(self):
        self.text_render = font.render(self.text, True, self.colour)
        pygame.draw.rect(screen, BLACK, self.rect_1)
        pygame.draw.rect(screen, WHITE, self.rect_2)
        screen.blit(self.text_render, self.text_rect)

class Title_name:
    def __init__(self, posx, posy, width, height, text):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text
        self.colour = VIOLET
        self.text_render = fontborg9.render(self.text, True, self.colour)
        self.text_render_2 = fontborg9_2.render(self.text, True, BLACK)
        self.rect_1 = pygame.Rect(self.posx, self.posy, self.width, self.height)
        self.rect_1.centerx = self.posx
        self.rect_2 = pygame.Rect(self.posx+5, self.posy+5, self.width-10, self.height-10)
        self.rect_2.centerx = self.posx
        self.text_rect = self.text_render.get_rect(center=self.rect_2.center)

    def display(self):
        self.text_render_2 = fontborg9_2.render(self.text, True, BLACK)
        self.text_render = fontborg9.render(self.text, True, self.colour)
        screen.blit(self.text_render_2, self.text_rect)
        screen.blit(self.text_render, self.text_rect)

async def endless(random_seed=1):
    running = True
    player = skiier(0, 0, 13, 0)

    wall1 = Walls(0, 0, 150, HEIGHT, wall_1)
    wall2 = Walls(WIDTH-150, 0, 150, HEIGHT, wall_2)

    game_map = Map(random_seed)
    
    print(random_seed)

    Flags = 0
    game_over = False

    countdown_menu = 5*FPS

    debounce = 5

    pygame.mixer.music.stop()
    pygame.mixer.music.load('assets/musik/active-sport.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

    while running:
        screen.fill(SNOW_WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                     player.direction *= -1
                     print(player.direction)
                     pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.direction *= -1
                print(player.direction)
        
        player_center = player.rect.center

        if game_map.finish_rect.collidepoint(player_center):
            print("RESET!!!!")
            game_map = Map(random.randint(0, 3000), infinity_mode=True)

        if player.rect.colliderect(wall1.rect) or player.rect.colliderect(wall2.rect) and debounce == 5:
            player.angle *= -1
            player.direction *= -1
            debounce = 0
        
        if debounce < 5:
            debounce += 1

        for safe in game_map.safe_zone:
            if safe.collidepoint(player_center):
                print("SAFE")
                player.speed_initial += 0.1
                print(player.speed_initial)
                if game_over == False:
                    Flags += 1
                    game_map.safe_zone.remove(safe)

        flag_surface = font.render("Flags: " + f"{Flags}", True, BLACK)  
        flag_rect = flag_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        for danger_zone in game_map.danger_zone_Left:
            if danger_zone.collidepoint(player_center):
                print("hit")
                game_map.danger_zone_Left.remove(danger_zone)
                game_over = True
                 
        for danger_zone in game_map.danger_zone_Right:
            if danger_zone.collidepoint(player_center):
                print("hit")
                game_map.danger_zone_Right.remove(danger_zone)
                game_over = True
        
#       print(time)
        player.move()
        game_map.display_start_goal(player.speed_y)
        player.display()
        wall1.display()
        wall2.display()
        game_map.display_move(screen, player.speed_y)

        if countdown_menu == 5*FPS-1:
            pygame.mixer.Sound.play(clapping)

        if game_over == True:
            countdown_menu -= 1
            screen.blit(flag_surface, flag_rect)
            print(countdown_menu)
            if countdown_menu < 0:
                return

        clock.tick(FPS)
        pygame.display.update()
        await asyncio.sleep(0)

async def time_trial(random_seed=1):
    running = True
    player = skiier(0, 0, 13, 0)

    wall1 = Walls(0, 0, 150, HEIGHT, wall_1)
    wall2 = Walls(WIDTH-150, 0, 150, HEIGHT, wall_2)

    game_map = Map(random_seed)

    print(random_seed)

    time = 0 
    start_timer = False

    finish_return_menu = False
    countdown_menu = 5*FPS

    debounce = 5

    pygame.mixer.music.stop()
    pygame.mixer.music.load('assets/musik/real-extreme.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

    while running:
        screen.fill(SNOW_WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                     player.direction *= -1
                     print(player.direction)
                     pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.direction *= -1
                print(player.direction)
        
        player_center = player.rect.center

        if game_map.start_rect.collidepoint(player_center):
            print("Start")
            start_timer = True

        if game_map.finish_rect.collidepoint(player_center):
            print("finish")
            pygame.mixer.Sound.play(clapping)
            start_timer = False
            finish_return_menu = True
            formatted_time = format_time(time / FPS)
            time_surface = font.render(formatted_time, True, BLACK)  # Render text
            time_rect = time_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        if finish_return_menu == True:
            countdown_menu -= 1
            screen.blit(time_surface, time_rect)
            print(countdown_menu)
            if countdown_menu < 0:
                return 

        if start_timer == True:
            time += 1

        if player.rect.colliderect(wall1.rect) or player.rect.colliderect(wall2.rect) and debounce == 5:
            player.angle *= -1
            player.direction *= -1
            debounce = 0
        
        if debounce < 5:
            debounce += 1

        for danger_zone in game_map.danger_zone_Left:
            if danger_zone.collidepoint(player_center):
                print("hit")
                game_map.danger_zone_Left.remove(danger_zone)
                time += 2*FPS
                 
        for danger_zone in game_map.danger_zone_Right:
            if danger_zone.collidepoint(player_center):
                print("hit")
                game_map.danger_zone_Right.remove(danger_zone)
                time += 2*FPS 

        if countdown_menu == 5*FPS-1:
            pygame.mixer.Sound.play(clapping)
        
#       print(time)
        player.move()
        game_map.display_start_goal(player.speed_y)
        player.display()
        wall1.display()
        wall2.display()
        game_map.display_move(screen, player.speed_y)
        
        clock.tick(FPS)
        pygame.display.update()
        await asyncio.sleep(0)

async def map_select():
    running = True
    Button_rect_map_1 = Button(WIDTH//2, 400, 500, 100, "Map 1")
    Button_rect_map_2 = Button(WIDTH//2, 550, 500, 100, "Map 2")
    Button_rect_map_3 = Button(WIDTH//2, 700, 500, 100, "Map 3")
    Button_rect_back = Button(WIDTH//2, 850, 500, 100, "Back")
    Alpine_hover_rect = Title_name(WIDTH//2, 200, 850, 150, "ALPINE2")

    buttons = [Button_rect_map_1, Button_rect_map_2, Button_rect_map_3, Button_rect_back]

    mouse_pos = (0,0)

    while running:
        screen.fill(SNOW_WHITE)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if Button_rect_map_1.rect_1.collidepoint(mouse_pos):
                    print("Map 1")
                    await time_trial(47)
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musik/retro-beat.ogg')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.2)
                elif Button_rect_map_2.rect_1.collidepoint(mouse_pos):
                    print("Map 2")
                    await time_trial(31)
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musik/retro-beat.ogg')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.2)
                elif Button_rect_map_3.rect_1.collidepoint(mouse_pos):
                    print("Map 2")
                    await time_trial(21)
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musik/retro-beat.ogg')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.2)
                elif Button_rect_back.rect_1.collidepoint(mouse_pos):
                    print("back")
                    return
        
        for button in buttons:
            button.colour = VIOLET if button.rect_1.collidepoint(mouse_pos) else BLACK

        Button_rect_map_1.display()
        Button_rect_map_2.display()
        Button_rect_map_3.display()
        Button_rect_back.display()
        Alpine_hover_rect.display()
        clock.tick(FPS)
        pygame.display.update()
        await asyncio.sleep(0)

async def main():
    running = True

    Button_rect_maps = Button(WIDTH//2, 400, 500, 100, "Maps")
    Button_rect_Endless = Button(WIDTH//2, 550, 500, 100, "Endless")
    Button_rect_story = Button(WIDTH//2, 700, 500, 100, "Random Map")
    Alpine_hover_rect = Title_name(WIDTH//2, 200, 850, 150, "ALPINE2")

    buttons = [Button_rect_maps, Button_rect_Endless, Button_rect_story]

    Thanks = pygame.Rect(WIDTH-105, HEIGHT-20, 100, 100)

    mouse_pos = (0,0)
    
    pygame.mixer.music.stop()
    pygame.mixer.music.load('assets/musik/retro-beat.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

    while running:
        screen.fill(SNOW_WHITE)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if Button_rect_maps.rect_1.collidepoint(mouse_pos):
                    print("Maps button clicked")
                    await map_select()
                elif Button_rect_Endless.rect_1.collidepoint(mouse_pos):
                    print("Endless button clicked")
                    await endless(random.randint(0, 3000))
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musik/retro-beat.ogg')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.2)
                elif Button_rect_story.rect_1.collidepoint(mouse_pos):
                    print("Arcade button clicked")
                    await time_trial(random.randint(0, 3000))
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musik/retro-beat.ogg')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.2)

        for button in buttons:
            button.colour = VIOLET if button.rect_1.collidepoint(mouse_pos) else BLACK

        Button_rect_maps.display()
        Button_rect_Endless.display()
        Button_rect_story.display()
        Alpine_hover_rect.display()
        text_render = fontsmall.render("Thanks to Phyfl", True, BLACK)
        screen.blit(text_render, Thanks)

        clock.tick(FPS)
        pygame.display.update()
        await asyncio.sleep(0)

asyncio.run(main())