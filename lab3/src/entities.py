import pygame
import random
import math
import os

def load_image_or_fallback(path, size, fallback_color, is_circle=False, is_modifier=False):
    if os.path.exists(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            scaled_image = pygame.transform.scale(image, size)
            return scaled_image
        except pygame.error:
            pass

    surface = pygame.Surface(size, pygame.SRCALPHA)
    if is_circle:
        radius = size[0] // 2
        pygame.draw.circle(surface, fallback_color, (radius, radius), radius)
    else:
        pygame.draw.rect(surface, fallback_color, (0, 0, size[0], size[1]))
        if is_modifier:
            pygame.draw.rect(surface, (255, 255, 255), (0, 0, size[0], size[1]), 2)
    return surface

class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.original_width = width
        self.height = height
        self.speed = 15
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.update_image(width)

    def update_image(self, width):
        self.image = pygame.Surface((width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 105, 180), (0, 0, width, self.height), border_radius=7)
        pygame.draw.rect(self.image, (139, 0, 139), (0, 0, width, self.height), 2, border_radius=7)

    def update(self, keys, screen_width):
        if keys[pygame.K_LEFT]:
            if self.rect.left > 0:
                self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            if self.rect.right < screen_width:
                self.rect.x += self.speed

    def resize(self, scale):
        new_width = int(self.original_width * scale)
        if new_width == self.rect.width:
            return
        center = self.rect.center
        self.update_image(new_width)
        self.rect = self.image.get_rect(center=center)

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color):
        super().__init__()
        self.radius = radius
        self.original_speed = 7.0
        self.velocity = [self.original_speed, -self.original_speed]
        
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 182, 193), (radius, radius), radius)
        pygame.draw.circle(self.image, (199, 21, 133), (radius, radius), radius, 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect.center = (x, y)

    def update(self, screen_width):
        if abs(self.velocity[0]) < 2.0:
            if self.velocity[0] >= 0:
                self.velocity[0] = 2.0
            else:
                self.velocity[0] = -2.0

        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        if self.rect.left <= 0:
            self.velocity[0] = abs(self.velocity[0])
            self.rect.left = 0
            self.x = float(self.rect.centerx)
        elif self.rect.right >= screen_width:
            self.velocity[0] = -abs(self.velocity[0])
            self.rect.right = screen_width
            self.x = float(self.rect.centerx)

        if self.rect.top <= 0:
            self.velocity[1] = abs(self.velocity[1])
            self.rect.top = 0
            self.y = float(self.rect.centery)

    def set_speed_multiplier(self, multiplier):
        if self.velocity[0] > 0:
            sign_x = 1
        else:
            sign_x = -1
            
        if self.velocity[1] > 0:
            sign_y = 1
        else:
            sign_y = -1
            
        self.velocity[0] = self.original_speed * multiplier * sign_x
        self.velocity[1] = self.original_speed * multiplier * sign_y

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, hp, colors_dict):
        super().__init__()
        self.hp = hp
        self.width = width
        self.height = height
        self.update_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_image(self):
        mlp_colors = {
            1: (255, 228, 225), 
            2: (221, 160, 221), 
            3: (135, 206, 250)
        }
        fill_color = mlp_colors.get(self.hp, (255, 192, 203))
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, fill_color, (0, 0, self.width, self.height))
        pygame.draw.rect(self.image, (148, 0, 211), (0, 0, self.width, self.height), 2)

class Modifier(pygame.sprite.Sprite):
    def __init__(self, x, y, mod_type, color):
        super().__init__()
        self.mod_type = mod_type
        self.vy = 3.5
        self.y = float(y)
        size = (30, 30)
        names = {1: "grow", 2: "shrink", 3: "fast", 4: "slow", 5: "life"}
        name = names.get(mod_type)
        path = f"assets/images/mod_{name}.png"
        self.image = load_image_or_fallback(path, size, (255, 105, 180), False, True)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.y += self.vy
        self.rect.centery = int(self.y)
        if self.rect.top > 800:
            self.kill()

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        # Случайный выбор между розовым и фиолетовым
        p_color = random.choice([(255, 105, 180), (148, 0, 211)])
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, p_color, (3, 3), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 20

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()