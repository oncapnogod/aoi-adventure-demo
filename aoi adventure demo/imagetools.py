# imagetools.py

'''
Useful module for image handling in game creation.
'''
def load_img(pygame, name, game_name):
    img = pygame.image.load("{}/graphics/{}.png".format(game_name, name))
    return img.copy()