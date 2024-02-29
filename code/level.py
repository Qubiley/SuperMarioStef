import pygame
from support import import_csv_layout, import_cut_graphics, Timer
from settings import *
from tiles import Tile, StaticTile, Coin, Lootbox, AnimatedTile, BillyBomb
from enemy import Enemy, Thwomp, FireBullet, IceBullet, Bowser, BowserBullet, BillyBullet
from decoration import Sky, Water, Clouds
from player import Player
from particles import ParticleEffect
from game_data import levels
from random import randint


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health, create_dungeon):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None
        self.create_dungeon = create_dungeon

        self.timers = {
            'bowser_shoot': Timer(1500, repeat=True, autostart=True, func=self.bowser_shoot),
            'billy_bomb_shoot': Timer(1500, repeat=True, autostart=True, func=self.billy_bomb_shoot)
        }

        # audio
        self.coin_sound = pygame.mixer.Sound('../audio/effects/coin.wav')
        self.coin_sound.set_volume(0.3)
        self.stomp_sound = pygame.mixer.Sound('../audio/effects/stomp.wav')
        self.stomp_sound.set_volume(0.6)
        self.lootbox_sound = pygame.mixer.Sound('../audio/effects/lootbox.wav')
        self.lootbox_sound.set_volume(0.8)
        self.power_up_1_sound = pygame.mixer.Sound('../audio/effects/power_up_1.wav')
        self.power_up_1_sound.set_volume(0.5)
        self.power_up_2_sound = pygame.mixer.Sound('../audio/effects/power_up_2.wav')
        self.power_up_2_sound.set_volume(0.5)
        self.shoot_sound = pygame.mixer.Sound('../audio/effects/shoot.wav')
        self.shoot_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound('../audio/effects/explosion.wav')
        self.explosion_sound.set_volume(0.3)

        # overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # player setup
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.can_dungeon = False

        # bowser setup
        bowser_layout = import_csv_layout(level_data['bowser'])
        self.bowser = pygame.sprite.GroupSingle()

        self.goal = pygame.sprite.GroupSingle()
        self.activated_lootbox = pygame.sprite.Group()
        self.power_mushroom = pygame.sprite.Group()
        self.fire_flower = pygame.sprite.Group()
        self.fire_bullets = pygame.sprite.Group()
        self.ice_flower = pygame.sprite.Group()
        self.ice_bullets = pygame.sprite.Group()
        self.iced_enemy = pygame.sprite.Group()
        self.iced_thwomp = pygame.sprite.Group()
        self.iced_billy_bomb_bullet = pygame.sprite.Group()
        self.player_setup(player_layout, change_health)
        self.bowser_setup(bowser_layout)
        self.bowser_bullets = pygame.sprite.Group()
        self.iced_bowser_bullet = pygame.sprite.Group()
        self.billy_bomb_bullets = pygame.sprite.Group()
        self.key = pygame.sprite.GroupSingle()
        self.lock = pygame.sprite.Group()

        # user interface
        self.change_coins = change_coins

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # explosion particles
        self.explosion_sprites = pygame.sprite.Group()
        self.fire_bullet_explosion_sprites = pygame.sprite.Group()
        self.ice_bullet_explosion_sprites = pygame.sprite.Group()

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprite = self.create_tile_group(terrain_layout, 'terrain')

        billy_bomb_layout = import_csv_layout(level_data['billy_bomb'])
        self.billy_bomb_sprite = self.create_tile_group(billy_bomb_layout, 'billy_bomb')

        # crates
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprite = self.create_tile_group(crates_layout, 'crates')

        lock_layout = import_csv_layout(level_data['lock'])
        self.lock_sprite = self.create_tile_group(lock_layout, 'lock')

        # coins
        coins_layout = import_csv_layout(level_data['coins'])
        self.coins_sprite = self.create_tile_group(coins_layout, 'coins')

        # lootbox
        lootbox_layout = import_csv_layout(level_data['lootbox'])
        self.lootbox_sprite = self.create_tile_group(lootbox_layout, 'lootbox')

        # boobytrap
        boobytrap_layout = import_csv_layout(level_data['boobytrap'])
        self.boobytrap_sprite = self.create_tile_group(boobytrap_layout, 'boobytrap')

        # thwomp
        thwomp_layout = import_csv_layout(level_data['thwomp'])
        self.thwomp_sprite = self.create_tile_group(thwomp_layout, 'thwomp')

        # enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # constraint
        constraints_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraints_layout, 'constraints')

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 25, level_width)
        self.clouds = Clouds(400, level_width, 30)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'billy_bomb':
                        bomb_tile_list = import_cut_graphics('../graphics/billy_bomb/billy_bomb.png')
                        if val in ['0', '1', '2', '3']:
                            tile_surface = bomb_tile_list[int(val)]
                            sprite = BillyBomb(tile_size, x, y, tile_surface)
                        if val in ['4', '5', '6', '7', '8', '9', '10', '11']:
                            tile_surface = bomb_tile_list[int(val)]
                            sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('../graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'crates':
                        crates_tile_list = import_cut_graphics('../graphics/terrain/crate.png')
                        tile_surface = crates_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'lock':
                        lock_tile_list = import_cut_graphics('../graphics/lock/lock.png')
                        tile_surface = lock_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'lootbox':
                        if val == '0':
                            sprite = Lootbox(tile_size, x, y, '../graphics/lootbox')

                    if type == 'boobytrap':
                        if val == '0':
                            sprite = Lootbox(tile_size, x, y, '../graphics/boobytrap')

                    if type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size, x, y, '../graphics/coins/gold', 5)
                        if val == '1':
                            sprite = Coin(tile_size, x, y, '../graphics/coins/silver', 1)

                    if type == 'enemies':
                        sprite = Enemy(tile_size, x, y)

                    if type == 'thwomp':
                        sprite = Thwomp(tile_size, x, y   )

                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)
        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':  # player
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health, 'ice                                             ',
                                    'sonic')
                    self.player.add(sprite)
                if val == '1':  # goal
                    hat_surface = pygame.image.load('../graphics/character/peach.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, (y - 20), hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def thwomp_collision_reverse(self):
        for thwomp in self.thwomp_sprite.sprites():
            if pygame.sprite.spritecollide(thwomp, self.constraint_sprites, False):
                thwomp.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 15)
        else:
            pos += pygame.math.Vector2(10, -15)
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprite.sprites() + self.crates_sprite.sprites() + self.lootbox_sprite.sprites() + self.activated_lootbox.sprites() + self.iced_enemy.sprites() + self.iced_thwomp.sprites() + self.thwomp_sprite.sprites() + self.boobytrap_sprite.sprites() + self.bowser.sprites() + self.billy_bomb_sprite.sprites() + self.lock_sprite.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprite.sprites() + self.lootbox_sprite.sprites() + self.activated_lootbox.sprites() + self.iced_enemy.sprites() + self.iced_thwomp.sprites() + self.thwomp_sprite.sprites() + self.boobytrap_sprite.sprites() + self.billy_bomb_sprite.sprites() + self.lock_sprite.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        for sprite in self.crates_sprite.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                self.can_dungeon = True
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
            self.can_dungeon = False

    def enemy_vertical_movement(self):
        for enemy in self.enemy_sprites.sprites():
            for sprite in self.terrain_sprite.sprites():
                if sprite.rect.colliderect(enemy.rect):
                    enemy.boobytrap = False
                    enemy.can_move = True
                    enemy.rect.bottom = sprite.rect.top + 15

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 2 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 2) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False) and not self.bowser:
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coins_sprite, True)
        if collided_coins:
            self.coin_sound.play()
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_lootbox_collisions(self):
        collided_lootbox = pygame.sprite.spritecollide(self.player.sprite, self.lootbox_sprite, False)
        if collided_lootbox:
            for lootbox in collided_lootbox:
                lootbox_bottom = lootbox.rect.bottom
                player_top = self.player.sprite.rect.top
                if lootbox_bottom > player_top:
                    if self.player.sprite.direction.x == 0:
                        self.lootbox_sound.play()
                        if self.player.sprite.power == '0':
                            self.activated_lootbox.add(StaticTile(tile_size, lootbox.rect.x, lootbox.rect.y,
                                                                  pygame.image.load(
                                                                      '../graphics/lootbox_activated/1.png')))
                            self.power_mushroom.add(StaticTile(tile_size, lootbox.rect.x, lootbox.rect.y - tile_size,
                                                               pygame.image.load('../graphics/powermushroom/1.png')))
                            lootbox.kill()
                        if self.player.sprite.power == '1':
                            flower_choice = randint(1, 2)
                            self.activated_lootbox.add(StaticTile(tile_size, lootbox.rect.x, lootbox.rect.y,
                                                                  pygame.image.load(
                                                                      '../graphics/lootbox_activated/1.png')))
                            if flower_choice == 1:
                                self.fire_flower.add(AnimatedTile(tile_size, lootbox.rect.x, lootbox.rect.y - tile_size,
                                                                  '../graphics/flower/fire'))
                            if flower_choice == 2:
                                self.ice_flower.add(AnimatedTile(tile_size, lootbox.rect.x, lootbox.rect.y - tile_size,
                                                                 '../graphics/flower/ice'))

                            lootbox.kill()
                        if self.player.sprite.power in ['fire', 'ice']:
                            self.activated_lootbox.add(StaticTile(tile_size, lootbox.rect.x, lootbox.rect.y,
                                                                  pygame.image.load(
                                                                      '../graphics/lootbox_activated/1.png')))
                            if self.player.sprite.has_key == False:
                                self.key.add(StaticTile(tile_size, lootbox.rect.x, lootbox.rect.y - tile_size,
                                                        pygame.image.load(
                                                            '../graphics/key/key.png')))

                            lootbox.kill()

    def check_boobytrap_collisions(self):
        collided_boobytrap = pygame.sprite.spritecollide(self.player.sprite, self.boobytrap_sprite, False)
        for boobytrap in collided_boobytrap:
            boobytrap_bottom = boobytrap.rect.bottom
            player_top = self.player.sprite.rect.top
            if boobytrap_bottom > player_top:
                if self.player.sprite.direction.y <= 1 and self.player.sprite.direction.x == 0:
                    self.lootbox_sound.play()
                    boobytrap.kill()

                    self.activated_lootbox.add(StaticTile(tile_size, boobytrap.rect.x, boobytrap.rect.y,
                                                          pygame.image.load('../graphics/lootbox_activated/1.png')))

                    self.enemy_sprites.add(Enemy(tile_size, boobytrap.rect.x + 8, boobytrap.rect.top - tile_size))

                boobytrap_enemy = self.enemy_sprites.sprites()[-1]
                boobytrap_enemy.can_move = False
                boobytrap_enemy.boobytrap = True

    def check_mushroom_collision(self):
        collided_mushroom = pygame.sprite.spritecollide(self.player.sprite, self.power_mushroom, False)
        if collided_mushroom:
            self.player.sprite.power = '1'
            self.power_up_1_sound.play()
            for mushroom in collided_mushroom:
                mushroom.kill()

    def check_lock_collision(self):
        collided_lock = pygame.sprite.spritecollide(self.player.sprite, self.lock_sprite, False)
        if collided_lock:
            if self.player.sprite.has_key == True:
                self.lock_sprite.empty()

    def check_key_collision(self):
        collided_key = pygame.sprite.spritecollide(self.player.sprite, self.key, True)
        if collided_key:
            self.player.sprite.has_key = True
            self.coin_sound.play()

    def check_flower_collision(self):
        collided_fire_flower = pygame.sprite.spritecollide(self.player.sprite, self.fire_flower, False)
        collided_ice_flower = pygame.sprite.spritecollide(self.player.sprite, self.ice_flower, False)
        if collided_fire_flower:
            self.player.sprite.power = 'fire'
            for flower in collided_fire_flower:
                flower.kill()
        if collided_ice_flower:
            self.player.sprite.power = 'ice'
            for flower in collided_ice_flower:
                flower.kill()

    def check_dungeon(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LCTRL]:
            if self.can_dungeon:
                self.create_dungeon(self.current_level, self.player.sprite.power)

    def check_shoot(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_RCTRL] and (
                self.player.sprite.power == 'fire' or self.player.sprite.power == 'ice') and not self.shoot_pressed:
            self.shoot_pressed = True
            self.shoot_sound.play()
            if self.player.sprite.facing_right == True:
                if self.player.sprite.power == 'fire':
                    self.fire_bullets.add(
                        FireBullet(32, self.player.sprite.rect.centerx, self.player.sprite.rect.centery))
                if self.player.sprite.power == 'ice':
                    self.ice_bullets.add(
                        IceBullet(32, self.player.sprite.rect.centerx, self.player.sprite.rect.centery))
            if self.player.sprite.facing_right == False:
                if self.player.sprite.power == 'fire':
                    self.fire_bullets.add(
                        FireBullet(32, self.player.sprite.rect.centerx, self.player.sprite.rect.centery))
                    last_fire_bullet = self.fire_bullets.sprites()[-1]
                    last_fire_bullet.speed *= -1
                if self.player.sprite.power == 'ice':
                    self.ice_bullets.add(
                        IceBullet(32, self.player.sprite.rect.centerx, self.player.sprite.rect.centery))
                    last_ice_bullet = self.ice_bullets.sprites()[-1]
                    last_ice_bullet.speed *= -1

        elif not key[pygame.K_RCTRL]:
            self.shoot_pressed = False

    def check_fire_bullet_collision(self):
        for spritegroup in [self.enemy_sprites, self.terrain_sprite, self.thwomp_sprite,
                            self.crates_sprite, self.lootbox_sprite, self.boobytrap_sprite, self.billy_bomb_sprite,
                            self.lock_sprite, self.billy_bomb_bullets]:
            for bullet in self.fire_bullets.sprites():
                if pygame.sprite.spritecollide(bullet, spritegroup, False):
                    self.explosion_sound.play()
                    bullet_explosion = ParticleEffect(bullet.rect.midtop, 'fire_bullet_explosion')
                    self.fire_bullet_explosion_sprites.add(bullet_explosion)
                    bullet.kill()
                    pygame.sprite.spritecollide(bullet, self.enemy_sprites, True)
                    collided_thwomp = pygame.sprite.spritecollideany(bullet, self.thwomp_sprite)
                    if collided_thwomp:
                        collided_thwomp.speed = randint(-1, 1)

                    collided_billy_bomb_bullet = pygame.sprite.spritecollideany(bullet, self.billy_bomb_bullets)
                    if collided_billy_bomb_bullet:
                        collided_billy_bomb_bullet.kill()

        for bullet in self.fire_bullets.sprites():
            if pygame.sprite.spritecollide(bullet, self.bowser, False):
                self.explosion_sound.play()
                bullet_explosion = ParticleEffect(bullet.rect.midtop, 'fire_bullet_explosion')
                self.fire_bullet_explosion_sprites.add(bullet_explosion)
                self.bowser.sprite.get_damage(2)
                bullet.kill()

    def check_ice_bullet_collision(self):
        for spritegroup in [self.enemy_sprites, self.terrain_sprite, self.thwomp_sprite,
                            self.crates_sprite, self.lootbox_sprite, self.bowser_bullets, self.billy_bomb_sprite,
                            self.lock_sprite, self.billy_bomb_bullets]:
            for bullet in self.ice_bullets.sprites():
                if pygame.sprite.spritecollide(bullet, spritegroup, False):
                    self.explosion_sound.play()
                    bullet_explosion = ParticleEffect(bullet.rect.midtop, 'ice_bullet_explosion')
                    self.ice_bullet_explosion_sprites.add(bullet_explosion)
                    bullet.kill()

                    collided_thwomp = pygame.sprite.spritecollideany(bullet, self.thwomp_sprite)
                    collided_enemy = pygame.sprite.spritecollideany(bullet, self.enemy_sprites)
                    collided_bowser_bullet = pygame.sprite.spritecollideany(bullet, self.bowser_bullets)
                    collided_billy_bomb_bullet = pygame.sprite.spritecollideany(bullet, self.billy_bomb_bullets)

                    if collided_enemy:
                        collided_enemy.kill()
                        self.iced_enemy.add(StaticTile((tile_size - 13), collided_enemy.rect.x, collided_enemy.rect.y,
                                                       pygame.image.load('../graphics/enemy/1.png')))

                    if collided_thwomp:
                        collided_thwomp.speed = 0
                        self.iced_thwomp.add(StaticTile(tile_size, collided_thwomp.rect.x, collided_thwomp.rect.y,
                                                        pygame.image.load('../graphics/thwomp/iced_thwomp.png')))

                    if collided_bowser_bullet:
                        collided_bowser_bullet.kill()
                        self.iced_bowser_bullet.add(
                            StaticTile(tile_size, collided_bowser_bullet.rect.x, collided_bowser_bullet.rect.y,
                                       pygame.image.load('../graphics/bowser/iced/1.png')))

                    if collided_billy_bomb_bullet:
                        collided_billy_bomb_bullet.kill()

                        self.iced_billy_bomb_bullet.add(StaticTile(tile_size, collided_billy_bomb_bullet.rect.x,
                                                                   collided_billy_bomb_bullet.rect.y,
                                                                   pygame.image.load('../graphics/billy_bomb/iced_bomb.png')))



        for bullet in self.ice_bullets.sprites():
            if pygame.sprite.spritecollide(bullet, self.bowser, False):
                self.explosion_sound.play()
                bullet_explosion = ParticleEffect(bullet.rect.midtop, 'ice_bullet_explosion')
                self.ice_bullet_explosion_sprites.add(bullet_explosion)
                self.bowser.sprite.get_damage(2)
                bullet.kill()

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
        bowser_collisions = pygame.sprite.spritecollide(self.player.sprite, self.bowser, False)

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 1:
                    self.stomp_sound.play()
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

        if bowser_collisions:
            bowser_center = self.bowser.sprite.rect.centery - 32
            bowser_top = self.bowser.sprite.rect.top
            player_bottom = self.player.sprite.rect.bottom
            if bowser_top < player_bottom < bowser_center and self.player.sprite.direction.y >= 1:
                self.stomp_sound.play()
                self.player.sprite.direction.y = -15
            else:
                self.player.sprite.get_damage()

    def check_thwomp_collisions(self):
        thwomp_collisions = pygame.sprite.spritecollideany(self.player.sprite, self.thwomp_sprite)
        if thwomp_collisions:
            if thwomp_collisions.speed != 0:
                self.player.sprite.get_damage()

    def bowser_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':  # player
                    sprite = Bowser(tile_size * 2, x, y)
                    self.bowser.add(sprite)

    def check_bowser_health(self):
        if self.bowser.sprite.health <= 0:
            self.bowser.sprite.kill()

    def bowser_shoot(self):
        if self.bowser.sprite.rect.x - self.player.sprite.rect.x <= tile_size * 6 and self.bowser.sprite.rect.x >= self.player.sprite.rect.x:
            self.bowser.sprite.can_move = True
            self.bowser_bullets.add(
                BowserBullet(32, self.bowser.sprite.rect.x - tile_size, self.bowser.sprite.rect.centery))
        if pygame.sprite.spritecollide(self.bowser.sprite, self.constraint_sprites, False):
            self.bowser.sprite.reverse()

    def billy_bomb_shoot(self):
        for sprite in self.billy_bomb_sprite:
            if isinstance(sprite, BillyBomb):
                if sprite.rect.x - self.player.sprite.rect.x <= tile_size * 6 and sprite.rect.x >= self.player.sprite.rect.x:
                    self.billy_bomb_bullets.add(BillyBullet(64, sprite.rect.x, sprite.rect.y + (tile_size - 8)))

    def check_billy_bomb_collisions(self):
        for spritegroup in [self.terrain_sprite, self.thwomp_sprite,
                            self.crates_sprite, self.lootbox_sprite, self.boobytrap_sprite]:
            for bomb in self.billy_bomb_bullets.sprites():
                if pygame.sprite.spritecollide(bomb, spritegroup, False):
                    self.explosion_sound.play()
                    bullet_explosion = ParticleEffect(bomb.rect.midtop, 'fire_bullet_explosion')
                    self.fire_bullet_explosion_sprites.add(bullet_explosion)
                    bomb.kill()
                if pygame.sprite.spritecollide(bomb, self.player, False):
                    self.player.sprite.get_damage()

    def check_bowser_bullet_collisions(self):
        bowser_bullet_collision = pygame.sprite.spritecollide(self.player.sprite, self.bowser_bullets, False)
        if bowser_bullet_collision:
            self.create_overworld(self.current_level, 0)

    def run(self):
        # decoration
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # run entire level
        self.terrain_sprite.update(self.world_shift)
        self.terrain_sprite.draw(self.display_surface)

        # billy bomb
        self.timers['billy_bomb_shoot'].update()
        self.billy_bomb_bullets.update(self.world_shift)
        self.billy_bomb_bullets.draw(self.display_surface)

        self.billy_bomb_sprite.update(self.world_shift)
        self.billy_bomb_sprite.draw(self.display_surface)

        # enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_vertical_movement()
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)

        # bowser
        if self.bowser.sprite:
            self.timers['bowser_shoot'].update()
            self.check_bowser_health()
            self.bowser_bullets.update(self.world_shift)
            self.bowser_bullets.draw(self.display_surface)
            self.bowser.update(self.world_shift)
            self.bowser.draw(self.display_surface)
            self.check_bowser_bullet_collisions()

        # thwomp
        self.thwomp_sprite.update(self.world_shift)
        self.thwomp_collision_reverse()
        self.thwomp_sprite.draw(self.display_surface)

        # lootbox
        self.lootbox_sprite.update(self.world_shift)
        self.lootbox_sprite.draw(self.display_surface)

        self.lock_sprite.update(self.world_shift)
        self.lock_sprite.draw(self.display_surface)

        self.boobytrap_sprite.update(self.world_shift)
        self.boobytrap_sprite.draw(self.display_surface)

        self.activated_lootbox.update(self.world_shift)
        self.activated_lootbox.draw(self.display_surface)

        self.power_mushroom.update(self.world_shift)
        self.power_mushroom.draw(self.display_surface)

        self.fire_flower.update(self.world_shift)
        self.fire_flower.draw(self.display_surface)

        self.ice_flower.update(self.world_shift)
        self.ice_flower.draw(self.display_surface)

        self.key.update(self.world_shift)
        self.key.draw(self.display_surface)

        # crate
        self.crates_sprite.update(self.world_shift)
        self.crates_sprite.draw(self.display_surface)

        # coins
        self.coins_sprite.update(self.world_shift)
        self.coins_sprite.draw(self.display_surface)

        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        self.fire_bullet_explosion_sprites.update(self.world_shift)
        self.fire_bullet_explosion_sprites.draw(self.display_surface)

        self.ice_bullet_explosion_sprites.update(self.world_shift)
        self.ice_bullet_explosion_sprites.draw(self.display_surface)

        self.iced_enemy.update(self.world_shift)
        self.iced_enemy.draw(self.display_surface)

        self.iced_thwomp.update(self.world_shift)
        self.iced_thwomp.draw(self.display_surface)

        self.iced_bowser_bullet.update(self.world_shift)
        self.iced_bowser_bullet.draw(self.display_surface)

        self.iced_billy_bomb_bullet.update(self.world_shift)
        self.iced_billy_bomb_bullet.draw(self.display_surface)
        self
        # shoot
        self.fire_bullets.update(self.world_shift)
        self.fire_bullets.draw(self.display_surface)

        self.ice_bullets.update(self.world_shift)
        self.ice_bullets.draw(self.display_surface)

        # player sprite
        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.check_dungeon()

        self.vertical_movement_collision()
        self.create_landing_dust()
        self.scroll_x()
        self.player.draw(self.display_surface)

        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()
        self.check_shoot()

        self.check_fire_bullet_collision()
        self.check_ice_bullet_collision()
        self.check_coin_collisions()
        self.check_lootbox_collisions()
        self.check_boobytrap_collisions()
        self.check_thwomp_collisions()
        self.check_enemy_collisions()
        self.check_mushroom_collision()
        self.check_flower_collision()
        self.check_billy_bomb_collisions()
        self.check_key_collision()
        self.check_lock_collision()

        # water
        self.water.draw(self.display_surface, self.world_shift)
