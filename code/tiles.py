import pygame
from support import import_folder


class Tile(pygame.sprite.Sprite):
    def __init__(self,size,x,y):
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.rect = self.image.get_rect(topleft = (x,y))

    def update(self, shift):
        self.rect.x += shift

class StaticTile(Tile):
    def __init__(self,size,x,y,surface):
        super().__init__(size,x,y)
        self.image = surface

class AnimatedTile(Tile):
    def __init__(self,size,x,y,path):
        super().__init__(size,x,y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.frame_speed = 0.15

    def animate(self):
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, shift):
        self.animate()
        self.rect.x += shift

class Lootbox(AnimatedTile):
    def __init__(self,size,x,y,path):
        super().__init__(size,x,y,path)
        self.rect = self.image.get_rect(topleft = (x,y))

class BillyBomb(StaticTile):
    def __init__(self,size,x,y,surface):
        super().__init__(size,x,y,surface)
        self.image = surface
        self.can_shoot = False

class Coin(AnimatedTile):
    def __init__(self,size,x,y,path,value):
        super().__init__(size,x,y,path)
        center_x = x + int(size / 2)
        center_y = y + int(size / 2)
        self.rect = self.image.get_rect(center = (center_x,center_y))
        self.value = value

class Palm(AnimatedTile):
    def __init__(self,size,x,y,path,offset):
        super().__init__(size,x,y,path)
        offset_y = y - offset
        self.rect.topleft = (x,offset_y)



