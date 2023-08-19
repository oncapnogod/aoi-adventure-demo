import pygame, random, math

from pygame.constants import K_LEFT, K_RIGHT, K_UP, KEYDOWN, KEYUP
# pygame.mixer.pre_init(44100, -16, 2, 512)
# (frequency, size, channel(1 is mono and 2 is stereo), buffer(low buffer makes sound start with minimal delay))
pygame.init()
pygame.mixer.set_num_channels(64) # basically increases number of sounds that can play at once

# common constructural conveniences
clock = pygame.time.Clock()
fps = 60
DIMENSIONS = (600,400)
gameExit = False

# screen initialization
screen = pygame.display.set_mode(DIMENSIONS)
pygame.display.set_caption("Aoi Adventure")
display = pygame.Surface((300,200))

def load_img(name):
    img = pygame.image.load("Aoi Adventure/graphics/{}.png".format(name))
    return img.copy()

def load_sound(name):
    sound = pygame.mixer.Sound("Aoi Adventure/audio/{}.wav".format(name))
    return sound

def load_map(number):
    f = open("Aoi Adventure/graphics/maps/map_{}.txt".format(number),"r")
    data = f.read()
    f.close()
    data = data.split("\n")
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

animation_database = {}
global animation_frames
animation_frames = {}
def load_animation(path,frame_durations, colorkey):
    # the path should resemble "entity_animations/state"
    path = "Aoi Adventure/graphics/" + path
    global animation_frames
    animation_name = path.split("/")[-1] # would evaluate to "state"
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + "_" + str(n)
        img_loc = path + '/' + animation_frame_id + ".png"
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey(colorkey)
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data
# animation handling (player)
animation_database["idle"] = load_animation("player_animations/idle", [15,7], (255,255,255))
animation_database["moving"] = load_animation("player_animations/moving", [7,7,7], (255,255,255))
# animation handling (ice)
animation_database["icedesign"] = load_animation("ice_animations/icedesign", [3,3,3,3], (0,0,0))

def change_action(action_var,frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame

def collision_test(rect, tiles):
    collisions = []
    for tile in tiles:
        if rect.colliderect(tile):
            collisions.append(tile)
    return collisions

def move(rect, movement, tiles):
    collision_types = {"top": False, "bottom": False, "left": False, "right": False}
    # x-axis collisions
    rect.x += movement[0]
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True
    # y-axis collisions
    rect.y += movement[1]
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[1] > 0: # if the rect has a downward collision with a tile
            rect.bottom = tile.top
            collision_types["bottom"] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True
    return rect, collision_types # returns a postcollision rectange and a list of how it collided with others 

map = load_map(1)
# template code for creating background objects
# object_i = [scroll_modifier, [x,y,width,height]]
# background_objects = [object_1, object_2, . . . object_n]
# note: objects with a larger modifier should be defined later to put them in a lower layer in order to maintain the parallax effect
object_1, object_2, object_3, object_4, object_5 = [0.25, [120,10,70,400]], [0.25, [280,30,40,400]], [0.5, [30,40,40,400]], [0.5, [130,90,100,400]], [0.5, [300,80,120,400]]
background_objects = [object_1, object_2, object_3, object_4, object_5]

# image workspace
ground_img = load_img("ground").convert()
ground_img.set_colorkey((0,0,0))
dirt_img = load_img("dirt")
TILE_SIZE = ground_img.get_width() # the width and height are equal so only 1 tile size variable is needed

# audio workspace
jump_sound = load_sound("jump")
walk_sounds = [load_sound("walk_0"),load_sound("walk_1")]
pygame.mixer.music.load("Aoi Adventure/audio/song_abyss.wav")
pygame.mixer.music.play(-1)
walk_sound_timer = 0
jump_sound.set_volume(0.5)

moving_left, moving_right = False, False
# note: this program does retain the player's location directly, but rather uses the player's rect for positioning and motion
player_momentum_y = 0
air_timer = 0
true_scroll = [0,0]
player_speed = 2
player_action = "idle"
player_frame = 0
player_flip = False
player_width, player_height = 9,13
player_rect = pygame.Rect(30,30,player_width,player_height) # width and height are 9 and 13

# game loop
while not gameExit:
    display.fill((0,0,0))

    # sound settings
    if walk_sound_timer > 0:
        walk_sound_timer -= 1

    # camera movement and parallax scrolling
    true_scroll[0] += (player_rect.x - true_scroll[0] - int(display.get_width()/2 + player_width/2)) / 10
    true_scroll[1] += (player_rect.y - true_scroll[1] - int(display.get_height()/2 + player_height/2)) / 10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    for obj in background_objects:
        obj_rect = pygame.Rect(obj[1][0] - scroll[0]*obj[0], obj[1][1] - scroll[1]*obj[0], obj[1][2], obj[1][3])
        if obj[0] == 0.25:
            pygame.draw.rect(display,(19,36,47),obj_rect)
        elif obj[0] == 0.5:
            pygame.draw.rect(display,(113,147,162),obj_rect)


    # generate map and generate a list of tiles capable of collisions
    tile_rects = []
    y = 0
    for row in map:
        x = 0
        for tile in row:
            if tile == "1":
                display.blit(dirt_img,(x*TILE_SIZE - scroll[0], y*TILE_SIZE - scroll[1]))
            if tile == "2":
                display.blit(ground_img,(x*TILE_SIZE - scroll[0], y*TILE_SIZE - scroll[1]))
            # if tile == "3": get theRightImage from animation_database["icedesign"][random.randint(0,11)]
                # display.blit(theRightImage,(x*TILE_SIZE - scroll[0], y*TILE_SIZE - scroll[1]))
            if tile != "0" and tile != "3":
                tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1


    # player movement
    player_movement = [0,0]
    if moving_left:
        player_movement[0] -= player_speed
        player_flip = True
    if moving_right:
        player_movement[0] += player_speed
        player_flip = False
    player_movement[1] += player_momentum_y
    player_momentum_y += 0.2
    if player_momentum_y > 4:
        player_momentum_y = 4

    # changes animation based on motion
    if moving_left or moving_right:
        player_action,player_frame = change_action(player_action,player_frame,"moving")
    else:
        player_action,player_frame = change_action(player_action,player_frame,"idle")

    # collision handling
    player_rect, collision_types = move(player_rect, player_movement, tile_rects)
    if collision_types["bottom"]:
        player_momentum_y = 0
        air_timer = 0
        if moving_left or moving_right:
            if walk_sound_timer == 0:
                walk_sound_timer = 20
                random.choice(walk_sounds).play()
    else:
        air_timer += 1
    if collision_types["top"]:
        player_momentum_y = 0.6

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img, player_flip, False),(player_rect.x - scroll[0],player_rect.y - scroll[1]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    player_momentum_y = -4
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    

    screen.blit(pygame.transform.scale(display,DIMENSIONS),(0,0))
    pygame.display.update()
    clock.tick(fps)