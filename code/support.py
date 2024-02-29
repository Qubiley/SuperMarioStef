from csv import reader
from settings import *
from os import walk
import pygame
from pygame.time import get_ticks

def import_folder(path):
    surface_list = []
    for _,__,image_files in walk(path):
        for image in image_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map,delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return(terrain_map)

def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_width() / tile_size)
    tile_num_y = int(surface.get_height() / tile_size)

    cut_tiles = []

    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surf = pygame.Surface((tile_size,tile_size),flags = pygame.SRCALPHA)
            new_surf.blit(surface,(0,0),pygame.Rect(x,y,tile_size,tile_size))
            cut_tiles.append(new_surf)

    return cut_tiles

class Timer:
    def __init__(self, duration, repeat = False, autostart = False, func = None):
        self.duration = duration
        self.start_time = 0
        self.active = False
        self.repeat = repeat
        self.func = func
        if autostart:
            self.activate()

    def activate(self):
        self.active = True
        self.start_time = get_ticks()
    def deactivate(self):
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()

    def update(self):
        if self.active:
            current_time = get_ticks()
            if current_time - self.start_time >= self.duration:
                if self.func: self.func()
                self.deactivate()

