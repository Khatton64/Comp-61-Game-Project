import pygame
import os
from os.path import join
from pytmx.util_pygame import load_pygame
from sprites import CollisionSprite, Gun, Bullet, Enemy
from player import Player
from groups import AllSprites
from settings import *

from random import choice

# States
MENU = 'menu'
GAME = 'game'
STORY = 'story'

class Button:
    def __init__(self, text, pos, font, callback):
        self.text = text
        self.pos = pos
        self.callback = callback
        self.font = font
        self.image = self.font.render(self.text, True, COLOR_WHITE)
        self.rect = self.image.get_rect(center=self.pos)

        # Music setup
        music_path = os.path.join(BASE_PATH := os.path.dirname(__file__), "audio", "s")
        if os.path.exists("Vampire survivor/zxaudio/SURVIVE by Kai Hatton.wav"):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)  # Optional: lower volume
            pygame.mixer.music.play(-1)  # Loop forever
        else:
            print("⚠️ Background music file not found:", music_path)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Zombyte')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU

        self.map = load_pygame(join('../data/maps/world.tmx'))

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        font = pygame.font.Font(None, 80)
        self.buttons = [
            Button('Start Game', (WINDOW_WIDTH // 2, 300), font, self.start_game),
            Button('Story / Summary', (WINDOW_WIDTH // 2, 400), font, self.show_story),
            Button('Quit', (WINDOW_WIDTH // 2, 500), font, self.quit_game)
        ]

        self.heart_image = pygame.Surface((32, 32))
        self.heart_image.fill(COLOR_RED)

        self.enemy_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.enemy_event, 2000)

        self.damage_cooldown = 0

    def setup(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()

        # Ground tiles
        for x, y, surf in self.map.get_layer_by_name('Ground').tiles():
            if surf:
                tile = CollisionSprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
                self.all_sprites.change_layer(tile, LAYER_GROUND)

        # Static map objects
        for obj in self.map.get_layer_by_name('Objects'):
            surf = obj.image if hasattr(obj, 'image') and obj.image else pygame.Surface((TILE_SIZE, TILE_SIZE))
            if not hasattr(obj, 'image') or obj.image is None:
                surf.fill((255, 0, 0))
            sprite = CollisionSprite((obj.x, obj.y), surf, self.all_sprites, self.collision_sprites)
            self.all_sprites.change_layer(sprite, LAYER_GROUND)

        # Player spawn
        player_position = (self.map.width * TILE_SIZE // 2, self.map.height * TILE_SIZE // 2)
        for obj in self.map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                player_position = (obj.x, obj.y)

        self.player = Player(player_position, [self.all_sprites], self.collision_sprites)
        self.all_sprites.change_layer(self.player, LAYER_PLAYER)

        self.gun = Gun(self.player, [self.all_sprites], self.bullet_sprites, self.all_sprites)
        self.all_sprites.change_layer(self.gun, LAYER_GUN)

    def start_game(self):
        self.state = GAME
        self.setup()

    def show_story(self):
        self.state = STORY

    def quit_game(self):
        self.running = False

    def draw_health(self):
        for i in range(self.player.health):
            self.display_surface.blit(self.heart_image, (10 + i * 40, 10))

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == MENU and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        button.check_click(pygame.mouse.get_pos())

                if self.state == GAME:
                    if event.type == self.enemy_event:
                        spawn_positions = [
                            (0, 0),
                            (self.map.width * TILE_SIZE - 50, 0),
                            (0, self.map.height * TILE_SIZE - 50),
                            (self.map.width * TILE_SIZE - 50, self.map.height * TILE_SIZE - 50)
                        ]
                        enemy_pos = choice(spawn_positions)
                        enemy_type = choice(['bat', 'blob', 'skeleton'])

                        frames = []
                        enemy_folder = join('images/enemies', enemy_type)
                        if os.path.exists(enemy_folder):
                            for img in sorted(os.listdir(enemy_folder)):
                                if img.endswith('.png'):
                                    img_path = join(enemy_folder, img)
                                    frames.append(pygame.image.load(img_path).convert_alpha())

                        if not frames:
                            fallback = pygame.Surface((50, 50))
                            fallback.fill((255, 0, 0))
                            frames = [fallback]

                        enemy = Enemy(enemy_pos, frames, [self.all_sprites, self.enemy_sprites], self.player, self.collision_sprites)
                        self.all_sprites.change_layer(enemy, LAYER_ENEMY)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.gun.shoot()

            if self.state == MENU:
                self.display_surface.fill((0, 0, 0))
                for button in self.buttons:
                    button.draw(self.display_surface)

            elif self.state == STORY:
                self.display_surface.fill((0, 0, 0))
                font = pygame.font.Font(None, 60)
                story_text = font.render('A long time ago... zombies rose.', True, COLOR_WHITE)
                self.display_surface.blit(
                    story_text,
                    (WINDOW_WIDTH // 2 - story_text.get_width() // 2, WINDOW_HEIGHT // 2)
                )

            elif self.state == GAME:
                self.all_sprites.update(dt, keys)
                self.gun.update(dt)

                for bullet in self.bullet_sprites:
                    hit_enemies = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False)
                    for enemy in hit_enemies:
                        enemy.take_damage(1)
                        bullet.kill()

                self.all_sprites.custom_draw(self.player)
                self.draw_health()

                if self.damage_cooldown > 0:
                    self.damage_cooldown -= dt * 1000

                if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False):
                    if self.damage_cooldown <= 0:
                        self.player.reduce_health()
                        self.damage_cooldown = 1000
                        if self.player.health <= 0:
                            self.running = False

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()
