import pygame
import json
import random
import os
from entities import Paddle, Ball, Brick, Particle, Modifier, load_image_or_fallback

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.load_configs()
        self.screen = pygame.display.set_mode((self.settings["window"]["width"], self.settings["window"]["height"]))
        pygame.display.set_caption("Arkanoid MLP Edition")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.player_name = ""
        self.active_effects = []
        self.current_music = ""
        self.bricks_destroyed = 0
        
        self.skip_rect = pygame.Rect(620, 15, 160, 40)
        
        self.load_assets()
        self.init_groups()
        self.set_state("MENU")

    def load_configs(self):
        with open("configs/settings.json", "r") as f:
            self.settings = json.load(f)
        with open("configs/levels.json", "r") as f:
            self.levels = json.load(f)
        try:
            with open("configs/highscores.json", "r") as f:
                self.highscores = json.load(f)
        except FileNotFoundError:
            self.highscores = []

    def get_bg_asset(self, filename):
        for ext in [".jpg", ".png", ".jpeg"]:
            full_path = f"assets/images/{filename}{ext}"
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert()
                return pygame.transform.scale(img, (800, 600))
        fallback = pygame.Surface((800, 600))
        fallback.fill(self.settings["colors"]["bg"])
        return fallback

    def load_assets(self):
        self.bg_image = self.get_bg_asset("background")
        self.menu_bg_image = self.get_bg_asset("menu_bg")
        try:
            self.snd_hit = pygame.mixer.Sound("assets/sounds/hit.wav")
            self.snd_explode = pygame.mixer.Sound("assets/sounds/explode.wav")
            self.snd_mod = pygame.mixer.Sound("assets/sounds/modifier.wav")
            self.snd_win = pygame.mixer.Sound("assets/sounds/win.wav")
        except Exception:
            self.snd_hit = None
            self.snd_explode = None
            self.snd_mod = None
            self.snd_win = None

    def play_sound(self, sound):
        if sound:
            sound.play()

    def play_music(self, track):
        if self.current_music == track:
            return
        self.current_music = track
        try:
            pygame.mixer.music.load(f"assets/music/{track}.mp3")
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def set_state(self, new_state):
        self.state = new_state
        if self.state in ["MENU", "HIGHSCORES", "HELP", "NEW_HIGHSCORE"]:
            self.play_music("menu")
        else:
            self.play_music("game")

    def init_groups(self):
        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.modifiers = pygame.sprite.Group()
        self.paddle = Paddle(400, 550, 150, 15, self.settings["colors"]["paddle"])
        self.ball = Ball(400, 500, 10, self.settings["colors"]["ball"])
        self.all_sprites.add(self.paddle, self.ball)

    def next_level(self):
        if self.current_level >= 10:
            self.check_highscore()
        else:
            self.current_level += 1
            self.load_level(self.current_level)

    def load_level(self, level_num):
        for b in list(self.bricks):
            b.kill()
        for m in list(self.modifiers):
            m.kill()
        for p in list(self.particles):
            p.kill()
        self.active_effects.clear()
        self.bricks_destroyed = 0
        self.ball.set_position(400, 500)
        self.ball.velocity = [self.ball.original_speed, -self.ball.original_speed]
        self.paddle.resize(1.0)
        level_data = self.levels.get(str(level_num))
        if not level_data:
            self.set_state("MENU")
            return
        cols = len(level_data[0])
        brick_width = self.settings["window"]["width"] // cols
        brick_height = 30
        for row_idx, row in enumerate(level_data):
            for col_idx, hp in enumerate(row):
                if hp > 0:
                    x_pos = col_idx * brick_width
                    y_pos = row_idx * brick_height + 120
                    brick = Brick(x_pos, y_pos, brick_width, brick_height, hp, self.settings["colors"])
                    self.bricks.add(brick)
                    self.all_sprites.add(brick)

    def spawn_particles(self, x, y):
        for _ in range(15):
            p = Particle(x, y, self.settings["colors"]["particle"])
            self.particles.add(p)
            self.all_sprites.add(p)

    def spawn_modifier(self, x, y):
        self.bricks_destroyed += 1
        if self.bricks_destroyed >= random.randint(4, 6):
            self.bricks_destroyed = 0
            mod_type = random.choice([1, 2, 3, 4, 5])
            mod = Modifier(x, y, mod_type, self.settings["colors"]["modifier"])
            self.modifiers.add(mod)
            self.all_sprites.add(mod)

    def apply_modifier(self, mod_type):
        if mod_type == 5:
            self.lives += 1
            return
        duration = 10000
        now = pygame.time.get_ticks()
        effect_data = {"type": mod_type, "end": now + duration, "total": duration}
        self.active_effects.append(effect_data)

    def update_effects(self):
        now = pygame.time.get_ticks()
        active_next_frame = []
        current_paddle_scale = 1.0
        current_ball_speed_mult = 1.0
        for effect in self.active_effects:
            if now < effect["end"]:
                active_next_frame.append(effect)
                m_type = effect["type"]
                if m_type == 1:
                    current_paddle_scale *= 1.5
                elif m_type == 2:
                    current_paddle_scale *= 0.7
                elif m_type == 3:
                    current_ball_speed_mult *= 1.5
                elif m_type == 4:
                    current_ball_speed_mult *= 0.7
        self.active_effects = active_next_frame
        self.paddle.resize(current_paddle_scale)
        self.ball.set_speed_multiplier(current_ball_speed_mult)

    def draw_ui(self):
        now = pygame.time.get_ticks()
        x_pos = 15
        y_pos = 15 
        for effect in self.active_effects:
            remaining = effect["end"] - now
            if remaining < 0:
                continue
            ratio = remaining / effect["total"]
            angle = ratio * 2 * 3.14159
            rect = pygame.Rect(x_pos, y_pos, 40, 40)
            pygame.draw.arc(self.screen, (0, 0, 0), rect, 0, angle, 4)
            m_type = effect["type"]
            names = {1: "grow", 2: "shrink", 3: "fast", 4: "slow"}
            name = names.get(m_type)
            img = load_image_or_fallback(f"assets/images/mod_{name}.png", (20, 20), (0, 255, 255))
            self.screen.blit(img, (x_pos + 10, y_pos + 10))
            x_pos += 50

    def handle_collisions(self):
        if self.ball.velocity[1] > 0:
            if self.ball.rect.colliderect(self.paddle.rect):
                self.ball.velocity[1] = -abs(self.ball.velocity[1])
                self.ball.rect.bottom = self.paddle.rect.top
                self.ball.y = float(self.ball.rect.centery)
                width_half = self.paddle.rect.width / 2
                offset = (self.ball.rect.centerx - self.paddle.rect.centerx) / width_half
                self.ball.velocity[0] = self.ball.original_speed * offset * 1.3
                self.play_sound(self.snd_hit)
        hit_bricks = pygame.sprite.spritecollide(self.ball, self.bricks, False)
        if hit_bricks:
            brick = sorted(hit_bricks, key=lambda b: pygame.Vector2(self.ball.rect.center).distance_to(b.rect.center))[0]
            dx = self.ball.rect.centerx - brick.rect.centerx
            dy = self.ball.rect.centery - brick.rect.centery
            if abs(dx / (brick.rect.width / 2)) > abs(dy / (brick.rect.height / 2)):
                self.ball.velocity[0] *= -1
            else:
                self.ball.velocity[1] *= -1
            self.ball.x = float(self.ball.rect.centerx)
            self.ball.y = float(self.ball.rect.centery)
            brick.hp -= 1
            if brick.hp <= 0:
                self.spawn_particles(brick.rect.centerx, brick.rect.centery)
                self.spawn_modifier(brick.rect.centerx, brick.rect.centery)
                brick.kill()
                self.score += 10
                self.play_sound(self.snd_explode)
                if len(self.bricks) == 0:
                    self.next_level()
            else:
                brick.update_image()
                self.play_sound(self.snd_hit)
        hit_mods = pygame.sprite.spritecollide(self.paddle, self.modifiers, True)
        for mod in hit_mods:
            self.apply_modifier(mod.mod_type)
            self.score += 5
            self.play_sound(self.snd_mod)

    def check_highscore(self):
        is_high = False
        if not self.highscores:
            is_high = True
        elif self.score > self.highscores[0].get("score", 0):
            is_high = True
        if is_high:
            self.set_state("NEW_HIGHSCORE")
            self.play_sound(self.snd_win)
            for _ in range(50):
                self.spawn_particles(random.randint(100, 700), random.randint(100, 400))
            self.player_name = ""
        else:
            self.set_state("MENU")

    def save_highscore(self):
        if self.player_name.strip() == "":
            self.player_name = "Player"
        new_entry = {"name": self.player_name, "score": self.score, "level": self.current_level}
        self.highscores.append(new_entry)
        self.highscores.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.highscores = self.highscores[:10]
        with open("configs/highscores.json", "w") as f:
            json.dump(self.highscores, f)
        self.set_state("MENU")

    def draw_text(self, text, x, y, font, color=(255, 255, 255), outline=False, outline_color=(0, 0, 0)):
        if outline:
            for dx, dy in [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]:
                surf_bg = font.render(text, True, outline_color)
                self.screen.blit(surf_bg, surf_bg.get_rect(center=(x + dx, y + dy)))
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=(x, y)))

    def run(self):
        running = True
        while running:
            if self.state in ["MENU", "HIGHSCORES", "HELP", "NEW_HIGHSCORE"]:
                self.screen.blit(self.menu_bg_image, (0, 0))
            else:
                self.screen.blit(self.bg_image, (0, 0))
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if self.state == "MENU":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.score = 0
                            self.lives = 3
                            self.current_level = 1
                            self.load_level(1)
                            self.set_state("PLAYING")
                        elif event.key == pygame.K_2:
                            self.set_state("HIGHSCORES")
                        elif event.key == pygame.K_3:
                            self.set_state("HELP")
                        elif event.key == pygame.K_4:
                            running = False
                elif self.state == "PLAYING":
                    if event.type == pygame.MOUSEBUTTONDOWN and self.skip_rect.collidepoint(event.pos):
                        self.next_level()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                        self.next_level()
                elif self.state in ["HIGHSCORES", "HELP"]:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.set_state("MENU")
                elif self.state == "NEW_HIGHSCORE":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.save_highscore()
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif len(self.player_name) < 10:
                            self.player_name += event.unicode

            pink = (255, 20, 147)
            white = (255, 255, 255)
            purple = (148, 0, 211)
            
            if self.state == "MENU":
                self.draw_text("ARKANOID", 400, 150, self.font_title, pink, True, white)
                self.draw_text("1. Начать игру", 400, 250, self.font_small, pink, True, white)
                self.draw_text("2. Таблица рекордов", 400, 300, self.font_small, pink, True, white)
                self.draw_text("3. Справка", 400, 350, self.font_small, pink, True, white)
                self.draw_text("4. Выход", 400, 400, self.font_small, pink, True, white)
            elif self.state == "HIGHSCORES":
                self.draw_text("РЕКОРДЫ", 400, 100, self.font_large, pink, True, white)
                for i, hs in enumerate(self.highscores):
                    self.draw_text(f"{hs['name']} | Счет: {hs['score']} | Ур: {hs['level']}", 400, 180 + i*40, self.font_small, pink, True, white)
                self.draw_text("Нажмите ESC для выхода", 400, 550, self.font_small, pink, True, white)
            elif self.state == "HELP":
                self.draw_text("ПРАВИЛА ИГРЫ", 400, 100, self.font_large, pink, True, white)
                rules = ["Отбивайте мяч платформой.", "Уничтожьте все блоки для победы.", "Стрелки для движения.", "Ловите бонусы.", "Кнопка 'N' — пропуск."]
                for i, r in enumerate(rules):
                    self.draw_text(r, 400, 200 + i*50, self.font_small, pink, True, white)
                self.draw_text("ESC для выхода", 400, 500, self.font_small, pink, True, white)
            elif self.state == "NEW_HIGHSCORE":
                if random.random() < 0.1:
                    self.spawn_particles(random.randint(100, 700), random.randint(100, 400))
                self.particles.update()
                self.draw_text("ВЫ ПОБИЛИ РЕКОРД!", 400, 100, self.font_title, purple, True, white)
                self.draw_text(f"Ваш результат: {self.score}", 400, 200, self.font_large, pink, True, white)
                self.draw_text("Введите имя:", 400, 300, self.font_small, purple, True, white)
                self.draw_text(self.player_name + "_", 400, 370, self.font_large, pink, True, white)
                self.draw_text("Нажмите ENTER для сохранения", 400, 500, self.font_small, purple, True, white)
                self.particles.draw(self.screen)
            elif self.state == "PLAYING":
                self.paddle.update(pygame.key.get_pressed(), self.settings["window"]["width"])
                self.ball.update(self.settings["window"]["width"])
                self.update_effects()
                self.particles.update()
                self.modifiers.update()
                if self.ball.rect.bottom >= self.settings["window"]["height"]:
                    self.lives -= 1
                    self.ball.set_position(400, 500)
                    self.ball.velocity = [self.ball.original_speed, -self.ball.original_speed]
                    if self.lives <= 0:
                        self.check_highscore()
                self.handle_collisions()
                self.all_sprites.draw(self.screen)
                self.draw_ui()
                self.draw_text(f"Счет: {self.score}   Жизни: {self.lives}   Ур: {self.current_level}", 400, 35, self.font_small, purple, True, white)
                pygame.draw.rect(self.screen, (221, 160, 221), self.skip_rect, border_radius=5)
                pygame.draw.rect(self.screen, purple, self.skip_rect, width=2, border_radius=5)
                self.draw_text("Пропуск (N)", self.skip_rect.centerx, self.skip_rect.centery, self.font_small, purple, True, white)
            pygame.display.flip()
            self.clock.tick(self.settings["window"]["fps"])
        pygame.quit()