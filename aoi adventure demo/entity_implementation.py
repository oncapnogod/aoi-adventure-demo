import pygame
from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_UP, KEYDOWN, KEYUP
from entity import Entity
pygame.init()

clock = pygame.time.Clock()
fps = 60
DIMENSIONS = (900,600)
gameExit = False
screen = pygame.display.set_mode(DIMENSIONS)
pygame.display.set_caption("Aoi Adventure")
display = pygame.Surface((300,200))

def load_img(name):
    img = pygame.image.load("Aoi Adventure/graphics/{}.png".format(name))
    return img.copy()

states = ["idle","moving","jumping"]
fd_info = {"idle" : [1,3], "moving" : [7,7,7], "jumping" : [3,64]}
path, ck = "player_animations", (255,255,255)
anim_info = {"path" : path, "fd" : fd_info, "ck" : ck}

player_base_img = load_img("player_animations/idle/idle_0")

myEntity = Entity(states, anim_info, [15,10])

display.fill((255,255,255))
true_scroll = [0,0]

images = []
tile_rects = [pygame.Rect(15,65,20,20), pygame.Rect(0,102,368,67), pygame.Rect(67,24,16,35)]
for tile in tile_rects:
    image = (load_img("default"))
    images.append(pygame.transform.scale(image, (tile.width,tile.height)))


gameExit = False
while gameExit == False:
    display.fill((255,255,255))

    true_scroll[0] += (myEntity.rect.x - true_scroll[0] - int(display.get_width()/2 + myEntity.rect.width/2)) / 10
    true_scroll[1] += (myEntity.rect.y - true_scroll[1] - int(display.get_height()/2 + myEntity.rect.height/2)) / 10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    
    myEntity.move(tile_rects)

    for i in range(len(images)):
        display.blit(images[i], (tile_rects[i].x, tile_rects[i].y))
    display.blit(player_base_img, (myEntity.rect.x, myEntity.rect.y))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == KEYDOWN:
            if event.key == K_UP:
                myEntity.jump()
            if event.key == K_LEFT:
                myEntity.set_direction(-1)
            if event.key == K_RIGHT:
                myEntity.set_direction(1)
        if event.type == KEYUP:
            if event.key == K_LEFT:
                if myEntity.get_direction() == -1:
                    myEntity.set_direction(0)
            if event.key == K_RIGHT:
                if myEntity.get_direction() == 1:
                    myEntity.set_direction(0)


    screen.blit(pygame.transform.scale(display,DIMENSIONS),(0,0))
    pygame.display.update()
    clock.tick(fps)
