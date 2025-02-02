import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventure Game")

clock = pygame.time.Clock()

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, health, color):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = health

    def move(self, dx, dy):
        if dx != 0:
            self.rect.x += dx
        if dy != 0:
            self.rect.y += dy

    def draw_health_bar(self, screen):
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, 40, 5))
        if self.health > 0:
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, 40 * (self.health / 100), 5))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, health=100, color=BLUE)
        self.speed = 5
        self.inventory = {
            "weapons": [],
            "food": [],
            "potions": []
        }
        self.active_weapon = None

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed
        self.move(dx, dy)

    def use_potion(self):
        if self.inventory["potions"]:
            potion = self.inventory["potions"].pop(0)
            if potion.effect_type == "health":
                self.health = min(100, self.health + 30)
            elif potion.effect_type == "speed":
                self.speed += 2
            elif potion.effect_type == "damage":
                if self.active_weapon:
                    self.active_weapon.damage += 5

    def change_weapon(self):
        if self.inventory["weapons"]:
            self.active_weapon = self.inventory["weapons"].pop(0)
            self.inventory["weapons"].append(self.active_weapon)

class Enemy(Entity):
    def __init__(self, x, y, health, enemy_type):
        super().__init__(x, y, health, color=RED)
        self.enemy_type = enemy_type
        self.speed = random.randint(1, 3)

    def follow_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed

        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed

class Weapon:
    def __init__(self, name, damage, range):
        self.name = name
        self.damage = damage
        self.range = range

class Food:
    def __init__(self, name, health_restore, is_magic=False):
        self.name = name
        self.health_restore = health_restore
        self.is_magic = is_magic

class Potion:
    def __init__(self, name, effect_duration, effect_type):
        self.name = name
        self.effect_duration = effect_duration
        self.effect_type = effect_type

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = 7
        self.damage = damage

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

class Game:
    def __init__(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.food_items = pygame.sprite.Group()
        self.potions = pygame.sprite.Group()
        self.running = True
        self.spawn_enemies(5)
        self.spawn_food(3)
        self.spawn_potions(2)

    def spawn_enemies(self, count):
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH - 40)
            y = random.randint(0, SCREEN_HEIGHT - 40)
            enemy_type = random.choice(["demon", "giant", "snake"])
            health = 50 if enemy_type == "demon" else 100 if enemy_type == "giant" else 75
            enemy = Enemy(x, y, health, enemy_type)
            self.enemies.add(enemy)

    def spawn_food(self, count):
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH - 40)
            y = random.randint(0, SCREEN_HEIGHT - 40)
            health_restore = random.randint(10, 30)
            food = Food("Food", health_restore)
            food_sprite = pygame.sprite.Sprite()
            food_sprite.image = pygame.Surface((20, 20))
            food_sprite.image.fill(GREEN)
            food_sprite.rect = food_sprite.image.get_rect()
            food_sprite.rect.topleft = (x, y)
            food_sprite.food = food
            self.food_items.add(food_sprite)

    def spawn_potions(self, count):
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH - 40)
            y = random.randint(0, SCREEN_HEIGHT - 40)
            effect_type = random.choice(["speed", "health", "damage"])
            potion = Potion("Potion", effect_duration=10, effect_type=effect_type)
            potion_sprite = pygame.sprite.Sprite()
            potion_sprite.image = pygame.Surface((20, 20))
            potion_sprite.image.fill(PURPLE)
            potion_sprite.rect = potion_sprite.image.get_rect()
            potion_sprite.rect.topleft = (x, y)
            potion_sprite.potion = potion
            self.potions.add(potion_sprite)

    def run(self):
        while self.running:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        direction = (0, -1)
                        projectile = Projectile(self.player.rect.centerx, self.player.rect.top, direction, damage=10)
                        self.projectiles.add(projectile)
                    if event.key == pygame.K_c:  
                        self.player.change_weapon()
                    if event.key == pygame.K_p:  
                        self.player.use_potion()

            keys = pygame.key.get_pressed()
            self.player.update(keys)

            for enemy in self.enemies:
                enemy.follow_player(self.player)

            self.projectiles.update()

            screen.blit(self.player.image, self.player.rect)
            self.player.draw_health_bar(screen)

            for enemy in self.enemies:
                screen.blit(enemy.image, enemy.rect)
                enemy.draw_health_bar(screen)

            self.projectiles.draw(screen)
            self.food_items.draw(screen)
            self.potions.draw(screen)

            for projectile in self.projectiles:
                hit = pygame.sprite.spritecollideany(projectile, self.enemies)
                if hit:
                    hit.health -= projectile.damage
                    self.projectiles.remove(projectile)
                    if hit.health <= 0:
                        self.enemies.remove(hit)

            pygame.display.flip()
            clock.tick(60)


game = Game()
game.run()
pygame.quit()