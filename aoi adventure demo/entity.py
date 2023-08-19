# entity.py

'''
Entity superclass that can be used for subclasses like player, enemy, etc.
'''

import pygame
from gamedata import *

__all__ = ["Entity", "Player"]

def load_animation(animation_images, state, path, frame_durations, colorkey):
    '''
    The animation images should be a dict, where the keys are animation IDs
    that map to their respective surface objects. The state should be a string,
    which would read "idle" or "moving" or "jumping/falling" and so on. The
    path should resemble "entityname_animations". The frame durations should
    be a list of numbers, where each element in the list represents how many
    frames each animation image should be active, and the length of the list
    is equal to the number of animation images within a state. The colorkey
    should be an RGB tuple.
    '''
    path = GAME_NAME + "/graphics/" + path
    # animation_name = path.split("/")[-1] # not needed, as state is a parameter.
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = state + "_" + str(n)
        img_loc = path + "/" + state + "/" + animation_frame_id + ".png"
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey(colorkey)
        animation_images[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


class Entity:
    def __init__(self, states, anim_info, spawn = [10,10], hp = 1, attack = 1, defense = 1, speed = 1):
        '''
        Animation info should be defined as such:\n
        anim_info = {"path" : "entityname_animations", "fd" : fd_info, "ck" = (R,G,B)}\n
        where fd_info is a dictionary as well:\n
        fd_info = {"state" : [a, b , ...], "state2" : [a2, b2, ...] . . .}
        '''
        self.states = states # self.states[0] = "idle" and so on
        self.current_state = self.states[0]
        self.anim_db = {} # state : list of anim_id
        self.anim_images = {} # anim_id : animation surface object
        for state in self.states:
            self.anim_db[state] = load_animation(self.anim_images, state, anim_info["path"], anim_info["fd"][state], anim_info["ck"])
        self.stats = {"HP" : hp, "ATK" : attack, "DEF" : defense, "SPD" : speed}
        self.spawn = spawn
        self.vel = {"x" : 0, "y" : 0, "x_max" : 3, "y_max" : 3}
        self.air_timer = 6
        self.rect = pygame.Rect(spawn[0],spawn[1],9,13)
        self.collision_types = {"top": False, "bottom": False, "left": False, "right": False}
        self.direction = 0 # 0 is not moving, -1 is moving left, 1 is moving right
        self.flip = False

    def collision_test(self, tiles):
        collisions = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                collisions.append(tile)
        return collisions

    def move(self, tiles):
        self.collision_types = {"top": False, "bottom": False, "left": False, "right": False}
        
        # x-axis collisions
        self.rect.x += self.vel["x"]
        collisions = self.collision_test(tiles)
        for tile in collisions:
            if self.vel["x"] > 0:
                self.rect.right = tile.left
                self.collision_types["right"] = True
            elif self.vel["x"] < 0:
                self.rect.left = tile.right
                self.collision_types["left"] = True
        
        # y-axis collisions
        self.rect.y += self.vel["y"]
        collisions = self.collision_test(tiles)
        for tile in collisions:
            if self.vel["y"] > 0: # if the self.rect has a downward collision with a tile
                self.rect.bottom = tile.top
                self.collision_types["bottom"] = True
            if self.vel["y"] < 0:
                self.rect.top = tile.bottom
                self.collision_types["top"] = True
        
        # gravity and horizontal acceleration
        if self.vel["y"] < self.vel["y_max"]:
            self.vel["y"] += 0.2 # 0.2 is gravity in terms of px per frame
        else:
            self.vel["y"] = self.vel["y_max"]
        if self.direction != 0:
            if (self.vel["x"] * self.direction) < self.vel["x_max"]:
                self.vel["x"] += self.stats["SPD"] * self.direction * 0.5
            else:
                self.vel["x"] = self.vel["x_max"] * self.direction
        else:
            self.vel["x"] -= self.unit_vector("x") * 0.2
            if abs(self.vel["x"]) < 0.4:
                self.vel["x"] = 0
        
        self.set_flip()

        # velocity changes caused by collision
        if self.collision_types["left"] or self.collision_types["right"]:
            self.vel["x"] = 0
        if self.collision_types["bottom"]:
            self.vel["y"] = 0
            self.air_timer = 0
            if self.vel["x"] == 0:
                self.set_state(self.states[0])
            else:
                self.set_state(self.states[1])
        else:
            self.air_timer += 1
            if self.collision_types["top"]: # only checked when entity is not grounded
                self.vel["y"] = 0.6
    
    def jump(self):
        if self.air_timer < 6:
            self.vel["y"] = -4
            self.set_state(self.states[2])

    def func(self):
        pass

    # accessors
    def get_direction(self):
        return self.direction

    def get_flip(self):
        return self.flip

    def get_this(self):
        return None

    # mutators
    def set_direction(self, direction):
        '''Sets the direction of horizontal acceleration:\n
        0 is not accelerating, -1 is left, and 1 is right.'''
        self.direction = direction

    def set_state(self, action):
        if self.current_state != action:
            self.current_state = action
            print(action)
            # change the animation frames
    
    def set_max_vel(self, axis = "x", max = 3):
        '''Description.'''
        self.vel[axis + "_max"] = max

    def set_flip(self):
        if self.vel["x"] > 0:
            self.flip = False # images will face right by default
        elif self.vel["x"] < 0:
            self.flip = True

    def set_this(self):
        pass

    # miscellaneous
    def unit_vector(self, axis):
        try:
            speed = int(self.vel[axis] / abs(self.vel[axis]))
        except ZeroDivisionError:
            speed = 0
        return speed



class Player(Entity):
    def __init__(self, states, anim_info, spawn=[10, 10], hp=1, attack=1, defense=1, speed=1):
        super().__init__(states, anim_info, spawn=spawn, hp=hp, attack=attack, defense=defense, speed=speed)
