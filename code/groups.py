import pygame

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def custom_draw(self, target):
        # Center camera on target
        self.offset.x = target.rect.centerx - self.display_surface.get_width() // 2
        self.offset.y = target.rect.centery - self.display_surface.get_height() // 2

        # Draw all sprites in layer order with camera offset
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
