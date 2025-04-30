import pygame
import os
from os.path import join
from pygame.locals import K_w, K_a, K_s, K_d
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_group):
        super().__init__(*groups)
        self.import_player_assets()

        # Animation state
        self.frame_index = 0
        self.status = 'down'

        # Fallback image
        self._fallback_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self._fallback_image.fill((0, 200, 0))

        # Set initial image safely
        status_frames = self.animations.get(self.status)
        if status_frames and len(status_frames) > 0:
            self.image = status_frames[0]
        else:
            print(f"⚠️ No animation frames for '{self.status}'. Using fallback.")
            self.image = self._fallback_image

        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.inflate(-TILE_SIZE * 0.4, -TILE_SIZE * 0.4)

        # Movement & Collision
        self.direction = pygame.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.collision_group = collision_group

        # Stats
        self.health = 3

    def import_player_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': []}
        base_path = join('images', 'player')  # ✅ Correct relative to main.py

        for direction in self.animations:
            full_path = join(base_path, direction)
            if os.path.exists(full_path):
                try:
                    for image_name in sorted(os.listdir(full_path)):
                        if image_name.lower().endswith('.png'):
                            image_path = join(full_path, image_name)
                            surf = pygame.image.load(image_path).convert_alpha()
                            self.animations[direction].append(surf)
                except Exception as e:
                    print(f"❌ Error loading images from {full_path}: {e}")
            else:
                print(f"⚠️ Directory not found: {full_path}")

            if not self.animations[direction]:
                print(f"⚠️ No frames found for '{direction}', fallback will be used.")

    def input(self, keys):
        self.direction = pygame.Vector2(0, 0)

        if keys[K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[K_s]:
            self.direction.y = 1
            self.status = 'down'

        if keys[K_a]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[K_d]:
            self.direction.x = 1
            self.status = 'right'

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

    def move(self, dt):
        self.hitbox.x += self.direction.x * self.speed * dt
        self.check_collisions('horizontal')
        self.hitbox.y += self.direction.y * self.speed * dt
        self.check_collisions('vertical')
        self.rect.center = self.hitbox.center

    def check_collisions(self, orientation):
        for sprite in self.collision_group:
            if self.hitbox.colliderect(sprite.rect):
                if orientation == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                    self.direction.x = 0
                elif orientation == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top
                    elif self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom
                    self.direction.y = 0

    def animate(self, dt):
        current_animation = self.animations.get(self.status)
        if current_animation and len(current_animation) > 0:
            self.frame_index += 8 * dt
            if self.frame_index >= len(current_animation):
                self.frame_index = 0
            self.image = current_animation[int(self.frame_index)]
        else:
            self.image = self._fallback_image

    def update(self, dt, keys):
        self.input(keys)
        self.move(dt)
        self.animate(dt)

    def reduce_health(self):
        self.health -= 1
        print(f"Player hit! Health: {self.health}")
        if self.health <= 0:
            self.kill()
