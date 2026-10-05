import random
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
DARK = (30, 35, 42)
GOLD = (214, 175, 54)
RED = (220, 70, 70)
GREEN = (90, 210, 120)
BLUE = (70, 120, 240)
GRAY = (150, 150, 160)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luxury Drive")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24)
font_big = pygame.font.SysFont("arial", 42, bold=True)

class PlayerCar:
    def __init__(self):
        self.w = 58
        self.h = 96
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - self.h - 30
        self.speed = 6
        self.color = (230, 195, 72)
        self.health = 3

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.x = max(30, min(WIDTH - self.w - 30, self.x))
        self.y = max(60, min(HEIGHT - self.h - 10, self.y))

    def draw(self):
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(screen, self.color, rect, border_radius=14)
        pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 18, self.w - 16, self.h - 28), border_radius=10)
        pygame.draw.rect(screen, GOLD, (self.x + 12, self.y + 8, self.w - 24, 16), border_radius=8)
        pygame.draw.rect(screen, GOLD, (self.x + 13, self.y + self.h - 22, self.w - 26, 12), border_radius=6)

class TrafficCar:
    def __init__(self, x, y):
        self.w = 56
        self.h = 96
        self.x = x
        self.y = y
        self.speed = random.randint(4, 11)
        self.color = random.choice([
            (255, 99, 71), (100, 149, 237), (75, 180, 160),
            (216, 75, 130), (170, 110, 255), (255, 182, 74)
        ])

    def update(self):
        self.y += self.speed

    def draw(self):
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(screen, self.color, rect, border_radius=14)
        pygame.draw.rect(screen, BLACK, (self.x + 7, self.y + 16, self.w - 14, self.h - 28), border_radius=10)
        pygame.draw.rect(screen, WHITE, (self.x + 12, self.y + 8, self.w - 24, 18), border_radius=6)

class Gem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 18
        self.speed = random.randint(3, 7)
        self.color = random.choice([GOLD, GREEN, BLUE, (255, 153, 255)])

    def update(self):
        self.y += self.speed

    def draw(self):
        points = [
            (self.x, self.y - self.size),
            (self.x + self.size, self.y),
            (self.x, self.y + self.size),
            (self.x - self.size, self.y),
        ]
        pygame.draw.polygon(screen, self.color, points)

class Game:
    def __init__(self):
        self.running = True
        self.game_over = False
        self.player = PlayerCar()
        self.traffic = []
        self.gems = []
        self.score = 0
        self.spawn_timer = 0
        self.gem_timer = 0
        self.distance = 0
        self.flash_timer = 0

    def spawn_traffic(self):
        lane_width = 120
        lanes = [70, 70 + lane_width, 70 + lane_width * 2, 70 + lane_width * 3]
        lane = random.choice(lanes)
        self.traffic.append(TrafficCar(lane, -120))

    def spawn_gem(self):
        lane = random.randint(60, WIDTH - 90)
        self.gems.append(Gem(lane, -30))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        self.player.move(dx, dy)

    def update(self):
        if self.game_over:
            return

        self.distance += 1
        self.spawn_timer += 1
        self.gem_timer += 1

        if self.spawn_timer > max(22, 60 - self.score // 80):
            self.spawn_traffic()
            self.spawn_timer = 0

        if self.gem_timer > 80:
            self.spawn_gem()
            self.gem_timer = 0

        for car in self.traffic:
            car.update()
            if car.y > HEIGHT + 120:
                self.traffic.remove(car)
                self.score += 10

            if self.player.x < car.x + car.w and self.player.x + self.player.w > car.x and self.player.y < car.y + car.h and self.player.y + self.player.h > car.y:
                self.player.health -= 1
                self.flash_timer = 20
                self.traffic.remove(car)
                if self.player.health <= 0:
                    self.game_over = True

        for gem in self.gems:
            gem.update()
            if gem.y > HEIGHT + 40:
                self.gems.remove(gem)

            if self.player.x < gem.x + gem.size and self.player.x + self.player.w > gem.x - gem.size and self.player.y < gem.y + gem.size and self.player.y + self.player.h > gem.y - gem.size:
                self.score += 25
                self.gems.remove(gem)

    def draw_background(self):
        screen.fill(BLACK)
        for i in range(0, HEIGHT, 40):
            pygame.draw.rect(screen, DARK, (0, i, WIDTH, 20))

        for lane in [120, 270, 420, 570]:
            pygame.draw.rect(screen, WHITE, (lane, 0, 4, HEIGHT), width=2)

        pygame.draw.rect(screen, (42, 48, 55), (45, 0, WIDTH - 90, HEIGHT))

    def draw_hud(self):
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        health_text = font.render(f"Health: {self.player.health}", True, RED)
        speed_text = font.render(f"Luxury Meter: {min(100, self.score // 5)}%", True, GOLD)

        screen.blit(score_text, (20, 20))
        screen.blit(health_text, (20, 52))
        screen.blit(speed_text, (20, 84))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            game_over_text = font_big.render("GAME OVER", True, RED)
            score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            prompt_text = font.render("Press ESC to quit", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - 130, HEIGHT // 2 - 50))
            screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
            screen.blit(prompt_text, (WIDTH // 2 - 90, HEIGHT // 2 + 50))

    def draw(self):
        self.draw_background()
        self.player.draw()
        for car in self.traffic:
            car.draw()
        for gem in self.gems:
            gem.draw()
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
