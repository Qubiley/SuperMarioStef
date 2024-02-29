import pygame
from tiles import AnimatedTile, StaticTile
from random import randint


class Enemy(AnimatedTile):
    def __init__(self,size,x,y):
        super().__init__(size,x,y,'../graphics/enemy/run')
        self.rect.y += size - self.image.get_height()
        self.speed = randint(3,5)
        self.can_move = True
        self.boobytrap = False
        self.x = x

    def move(self):
        if self.can_move:
            self.rect.x += self.speed
        if self.boobytrap:
            hit_x = self.x + 64
            if self.rect.x < hit_x:
                self.rect.x += 4
            if self.rect.x >= hit_x:
                self.rect.y += 8

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()

class Thwomp(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load('../graphics/thwomp/thwomp.png').convert_alpha())
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.speed = randint(3, 5)
    def move(self):
        self.rect.y += self.speed

    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.move()

class Bowser(AnimatedTile):
    def __init__(self,size,x,y):
        super().__init__(size,x,y,'../graphics/bowser')
        self.rect.y -= size / 2
        self.x = x
        self.y = y

        self.speed = 2
        self.can_move = False
        self.health = 10

    def move(self):
        if self.can_move:
            self.rect.y += self.speed

    def get_damage(self, damage):
        self.health -= damage

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        #self.reverse_image()

class FireBullet(AnimatedTile):
    def __init__(self,size,x,y):
        super().__init__(size,x,y,'../graphics/bullets/fire')
        self.rect.y -= self.image.get_height()
        self.speed = 7

    def move(self):
        self.rect.x += self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()

class IceBullet(AnimatedTile):
    def __init__(self,size,x,y):
        super().__init__(size,x,y,'../graphics/bullets/ice')
        self.rect.y -= self.image.get_height()
        self.speed = 7

    def move(self):
        self.rect.x += self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()


class BowserBullet(AnimatedTile):
    def __init__(self,size,x,y):
        super().__init__(size,x,y,'../graphics/bowser/bowser_fire')
        self.rect.y -= self.image.get_height()
        self.speed = 4

    def move(self):
        self.rect.x -= self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()

class BillyBullet(AnimatedTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, '../graphics/billy_bomb/billy_bullet')
        self.rect.y -= self.image.get_height()
        self.speed = 4
    def move(self):
        self.rect.x -= self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        #self.reverse_image()