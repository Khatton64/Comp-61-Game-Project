import pygame
import os
from os.path import join
from settings import *
from settings import (
    GUN_COOLDOWN,
    COLOR_RED, COLOR_WHITE,
    LAYER_GROUND, LAYER_ENEMY, LAYER_PLAYER, LAYER_GUN, LAYER_BULLET, LAYER_UI,
    TILE_SIZE
)


# Absolute paths for image loading
BASE_PATH = os.path.dirname(__file__)
GUN_PATH = os.path.join(BASE_PATH, 'images', 'gun', 'gun.png')
BULLET_PATH = os.path.join(BASE_PATH, 'images', 'gun', 'bullet.png')

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, dt, keys=None):
        pass

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups):
        super().__init__(*groups)
        try:
            self.image = pygame.image.load(BULLET_PATH).convert_alpha()
            print("✅ Bullet image loaded successfully.")
        except Exception as e:
            print(f"❌ Bullet image load failed: {e}")
            self.image = pygame.Surface((10, 4))
            self.image.fill((255, 255, 0))  # Bright yellow fallback

        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = 600

    def update(self, dt, keys=None):
        self.rect.center += self.direction * self.speed * dt
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            print("💀 Bullet killed (off-screen)")
            self.kill()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups, bullet_group, all_sprites_group):
        super().__init__(*groups)
        self.player = player
        self.bullet_group = bullet_group
        self.all_sprites_group = all_sprites_group

        try:
            self.original_image = pygame.image.load(GUN_PATH).convert_alpha()
            print("✅ Gun image loaded successfully.")
        except pygame.error as e:
            print(f"❌ Error loading gun image: {e}")
            self.original_image = pygame.Surface((40, 20))
            self.original_image.fill((100, 100, 100))

        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.offset = pygame.Vector2(30, 0)
        self.last_shot_time = 0
        self.cooldown = GUN_COOLDOWN
        self.direction = pygame.Vector2(1, 0)

    def update(self, dt, keys=None):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center = self.player.rect.center
        direction = pygame.Vector2(mouse_x - player_center[0], mouse_y - player_center[1])
        if direction.length() > 0:
            self.direction = direction.normalize()

        angle = -self.direction.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=player_center + self.offset.rotate(-angle))

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.cooldown:
            self.last_shot_time = current_time

            # Calculate bullet start position (at gun tip)
            angle = -self.direction.angle_to(pygame.Vector2(1, 0))
            bullet_offset = self.offset.rotate(-angle)
            bullet_start = pygame.Vector2(self.player.rect.center) + bullet_offset

            # Create and spawn bullet
            bullet = Bullet(bullet_start, self.direction, [self.all_sprites_group, self.bullet_group])
            self.all_sprites_group.change_layer(bullet, LAYER_BULLET)

            # Optional debug log
            print(f"🔫 Bullet fired at {bullet_start}")


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(*groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        self.player = player
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 100
        self.health = 3

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def move_toward_player(self, dt):
        if not self.player.alive():
            return
        self.direction = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed * dt

    def update(self, dt, keys=None):
        self.animate(dt)
        self.move_toward_player(dt)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

print("✅ sprites.py loaded with Bullet, Gun, Enemy, and CollisionSprite")
