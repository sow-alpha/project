import pygame
import random

# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Base Game Entity class
class GameEntity(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=position)
        self.health = 200
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, amount=5):
        self.health -= amount
        if self.health <= 0:
            self.kill()

# Player class
class Player(GameEntity):
    def __init__(self, image_path, position):
        super().__init__(image_path, position)
        self.speed = 5

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def cast_spell(self):
        new_spell = Spell(self.rect.center, 'right')
        return new_spell

# Enemy class
class Enemy(GameEntity):
    def __init__(self, image_path, position):
        super().__init__(image_path, position)
        self.health = 300  # Enemies have 300 health, requiring three hits of 100 damage each to die
        self.shoot_interval = 3000  # milliseconds
        self.last_shot = pygame.time.get_ticks()


    def shoot(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_interval:
            self.last_shot = current_time
            direction = pygame.math.Vector2(player.rect.x - self.rect.x, player.rect.y - self.rect.y).normalize()
            new_bullet = Projectile(self.rect.center, direction)
            return new_bullet
        return None

# Health Bar class
class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health

    def draw(self, screen, health, position):
        bar_position = position
        bar_width = 100
        bar_height = 20
        fill = (health / self.max_health) * bar_width
        color = (255, 0, 0)  # Red
        if health > 70:
            color = (0, 255, 0)  # Green
        elif health > 40:
            color = (255, 255, 0)  # Yellow
        outline_rect = pygame.Rect(bar_position[0], bar_position[1], bar_width, bar_height)
        fill_rect = pygame.Rect(bar_position[0], bar_position[1], fill, bar_height)
        pygame.draw.rect(screen, color, fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)

# Spell class
class Spell(pygame.sprite.Sprite):
    def __init__(self, position, direction):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=position)
        self.speed = 10
        self.direction = direction

    def update(self):
        self.rect.x += self.speed if self.direction == 'right' else -self.speed

# Projectile class for enemies
class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, direction):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=position)
        self.speed = 7
        self.direction = direction

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mystic Quest Remastered')
clock = pygame.time.Clock()

# Background
background_image = pygame.image.load('assets/background_image.jpg').convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font for drawing text
font = pygame.font.SysFont(None, 36)

# Main menu function
def main_menu():
    menu_running = True
    title_font = pygame.font.SysFont(None, 48)
    while menu_running:
        screen.blit(background_image, (0, 0))
        title_text = title_font.render("Mystic Quest Remastered", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        start_text = font.render("Press SPACE to start", True, (255, 255, 255))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_game()

        pygame.display.flip()
        clock.tick(60)

# Main game function
def main_game():
    player = Player('assets/player_image.jpg', (50, SCREEN_HEIGHT // 2))
    player_health_bar = HealthBar(player.health)
    all_entities = pygame.sprite.Group()
    spells = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    all_entities.add(player)
    score = 0
    last_spawn_time = pygame.time.get_ticks()
    ENEMY_SPAWN_RATE = 5000  # Initial enemy spawn rate in milliseconds
    current_spawn_rate = ENEMY_SPAWN_RATE
    spawn_rate_decrease = 500  # How much to decrease spawn rate each increment of 10 points
    SHOOT_INTERVAL_DECREASE = 300  # Decrease shooting interval by 300ms each 10 points
    initial_shoot_interval = 3000  # Initial shooting interval in milliseconds
    last_score_checkpoint = 0  # Track the last score checkpoint

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time > current_spawn_rate:
            last_spawn_time = current_time
            y = random.randint(50, SCREEN_HEIGHT - 50)
            new_enemy_position = (SCREEN_WIDTH - 60, y)
            new_enemy = Enemy('assets/enemy_image.jpg', new_enemy_position)
            new_enemy.shoot_interval = max(1000, initial_shoot_interval - SHOOT_INTERVAL_DECREASE * (score // 10))
            enemies.add(new_enemy)
            all_entities.add(new_enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    new_spell = player.cast_spell()
                    if new_spell:  # Ensure the new spell is not None
                        spells.add(new_spell)
                        all_entities.add(new_spell)

        keys_pressed = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys_pressed[pygame.K_UP]:
            dy = -1
        if keys_pressed[pygame.K_DOWN]:
            dy = 1
        if keys_pressed[pygame.K_LEFT]:
            dx = -1
        if keys_pressed[pygame.K_RIGHT]:
            dx = 1
        player.move(dx, dy)

        for spell in spells:
            for enemy in enemies:
                if pygame.sprite.collide_mask(spell, enemy):
                    enemy.take_damage(100)
                    spell.kill()
                    score += 1
                    if score // 10 > last_score_checkpoint:
                        last_score_checkpoint = score // 10
                        current_spawn_rate = max(1000, current_spawn_rate - spawn_rate_decrease)
                        # Dynamically decrease the shooting interval for all enemies
                        for enemy in enemies:
                            enemy.shoot_interval = max(1000, initial_shoot_interval - SHOOT_INTERVAL_DECREASE * (score // 10))

        for bullet in enemy_bullets:
            if pygame.sprite.collide_mask(bullet, player):
                player.take_damage(10)
                bullet.kill()

        for enemy in enemies:
            bullet = enemy.shoot(player)
            if bullet:
                enemy_bullets.add(bullet)
                all_entities.add(bullet)

        screen.blit(background_image, (0, 0))
        all_entities.update()
        all_entities.draw(screen)
        player_health_bar.draw(screen, player.health, (10, 10))
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 40))

        if player.health <= 0:
            for _ in range(3):
                screen.fill((0, 0, 0))
                game_over_text = font.render("GAME OVER", True, (255, 0, 0))
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.delay(500)
                screen.blit(background_image, (0, 0))
                pygame.display.flip()
                pygame.time.delay(500)
            break

        pygame.display.flip()
        clock.tick(60)

    main_menu()



# Run the main menu initially
main_menu()

# Quit Pygame when the main menu loop exits
pygame.quit()
