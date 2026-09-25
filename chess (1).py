import pygame
import random
import math
import os
import sys

# ============================================================
# ADVANCED AIRPLANE SHOOTING GAME
# ============================================================
# Controls:
#   Arrow Keys = Move
#   SPACE      = Shoot
#   P          = Pause
#   R          = Restart
#   ESC        = Quit
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
except pygame.error:
    pass

# ============================================================
# SCREEN
# ============================================================

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SARACHYAN - Advanced Airplane Shooting Game")

clock = pygame.time.Clock()
FPS = 60

# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
GREEN = (70, 255, 100)
BLUE = (70, 170, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 240, 50)
ORANGE = (255, 150, 30)
PURPLE = (190, 80, 255)
PINK = (255, 80, 180)
DARK_BLUE = (5, 10, 35)
LIGHT_BLUE = (30, 80, 160)
GRAY = (100, 110, 130)

# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.SysFont("Arial", 18)
FONT_MEDIUM = pygame.font.SysFont("Arial", 26, bold=True)
FONT_LARGE = pygame.font.SysFont("Arial", 48, bold=True)
FONT_HUGE = pygame.font.SysFont("Arial", 75, bold=True)

# ============================================================
# GAME STATES
# ============================================================

MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
VICTORY = 4

game_state = MENU

# ============================================================
# HIGH SCORE
# ============================================================

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as file:
                return int(file.read())
    except:
        pass

    return 0


def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(value))
    except:
        pass


high_score = load_high_score()

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def draw_text(text, font, color, x, y, center=True):
    surface = font.render(text, True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


def draw_health_bar(x, y, width, height, current, maximum):
    pygame.draw.rect(
        screen,
        (50, 50, 60),
        (x, y, width, height),
        border_radius=5
    )

    percentage = max(0, current / maximum)

    bar_width = int(width * percentage)

    if percentage > 0.6:
        color = GREEN
    elif percentage > 0.3:
        color = YELLOW
    else:
        color = RED

    pygame.draw.rect(
        screen,
        color,
        (x, y, bar_width, height),
        border_radius=5
    )


# ============================================================
# STAR BACKGROUND
# ============================================================

stars = []


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1, 5)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)

    def update(self):
        self.y += self.speed

        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        color = (
            self.brightness,
            self.brightness,
            self.brightness
        )

        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            self.size
        )


for _ in range(120):
    stars.append(Star())


def update_background():
    screen.fill(DARK_BLUE)

    for star in stars:
        star.update()
        star.draw()


# ============================================================
# PARTICLE SYSTEM
# ============================================================

particles = []


class Particle:
    def __init__(
        self,
        x,
        y,
        color,
        speed=None,
        lifetime=None,
        size=None
    ):
        self.x = x
        self.y = y
        self.color = color

        angle = random.uniform(0, math.pi * 2)

        if speed is None:
            speed = random.uniform(1, 7)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = lifetime or random.randint(20, 50)
        self.max_life = self.life

        self.size = size or random.randint(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.98
        self.vy *= 0.98

        self.life -= 1

    def draw(self):
        if self.life <= 0:
            return

        ratio = self.life / self.max_life
        size = max(1, int(self.size * ratio))

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            size
        )


def create_explosion(x, y, color=ORANGE, amount=30):
    for _ in range(amount):
        particles.append(
            Particle(
                x,
                y,
                color,
                speed=random.uniform(2, 9),
                lifetime=random.randint(20, 60),
                size=random.randint(2, 7)
            )
        )


def update_particles():
    for particle in particles[:]:
        particle.update()

        if particle.life <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        particle.draw()


# ============================================================
# BULLET CLASS
# ============================================================

bullets = []


class Bullet:
    def __init__(self, x, y, dx=0, dy=-12, damage=1):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.width = 5
        self.height = 18
        self.active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

        if (
            self.y < -30
            or self.y > HEIGHT + 30
            or self.x < -30
            or self.x > WIDTH + 30
        ):
            self.active = False

    def draw(self):
        pygame.draw.rect(
            screen,
            CYAN,
            (
                int(self.x - self.width / 2),
                int(self.y),
                self.width,
                self.height
            ),
            border_radius=3
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x), int(self.y)),
            3
        )

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width / 2,
            self.y,
            self.width,
            self.height
        )


# ============================================================
# ENEMY BULLET
# ============================================================

enemy_bullets = []


class EnemyBullet:
    def __init__(self, x, y, dx=0, dy=6, damage=1):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.radius = 6
        self.active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

        if (
            self.y > HEIGHT + 30
            or self.y < -30
            or self.x < -30
            or self.x > WIDTH + 30
        ):
            self.active = False

    def draw(self):
        pygame.draw.circle(
            screen,
            RED,
            (int(self.x), int(self.y)),
            self.radius
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (int(self.x), int(self.y)),
            3
        )

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


# ============================================================
# PLAYER
# ============================================================


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100

        self.width = 55
        self.height = 70

        self.speed = 7

        self.max_health = 100
        self.health = self.max_health

        self.lives = 3

        self.shoot_cooldown = 0
        self.shoot_delay = 12

        self.rapid_fire = 0
        self.shield = 0

        self.invincible = 0

        self.blink_timer = 0

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100

        self.health = self.max_health
        self.lives = 3

        self.rapid_fire = 0
        self.shield = 0

        self.invincible = 120

    def update(self):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx -= self.speed

        if keys[pygame.K_RIGHT]:
            dx += self.speed

        if keys[pygame.K_UP]:
            dy -= self.speed

        if keys[pygame.K_DOWN]:
            dy += self.speed

        # Diagonal movement normalization
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.x += dx
        self.y += dy

        self.x = clamp(
            self.x,
            self.width / 2,
            WIDTH - self.width / 2
        )

        self.y = clamp(
            self.y,
            100,
            HEIGHT - self.height / 2
        )

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.rapid_fire > 0:
            self.rapid_fire -= 1

        if self.shield > 0:
            self.shield -= 1

        if self.invincible > 0:
            self.invincible -= 1

        if self.blink_timer > 0:
            self.blink_timer -= 1

    def shoot(self):
        if self.shoot_cooldown > 0:
            return

        if self.rapid_fire > 0:
            self.shoot_cooldown = 5

            bullets.append(
                Bullet(
                    self.x - 18,
                    self.y - 25,
                    damage=2
                )
            )

            bullets.append(
                Bullet(
                    self.x + 18,
                    self.y - 25,
                    damage=2
                )
            )

        else:
            self.shoot_cooldown = self.shoot_delay

            bullets.append(
                Bullet(
                    self.x,
                    self.y - 30,
                    damage=1
                )
            )

    def take_damage(self, amount):
        if self.invincible > 0:
            return

        if self.shield > 0:
            create_explosion(
                self.x,
                self.y,
                CYAN,
                15
            )
            self.shield -= 20
            return

        self.health -= amount
        self.invincible = 60

        create_explosion(
            self.x,
            self.y,
            RED,
            15
        )

        if self.health <= 0:
            self.lives -= 1

            if self.lives > 0:
                self.health = self.max_health
                self.x = WIDTH // 2
                self.y = HEIGHT - 100
                self.invincible = 180
            else:
                end_game()

    def draw(self):
        # Blink while invincible
        if self.invincible > 0:
            if (self.invincible // 5) % 2 == 0:
                return

        x = int(self.x)
        y = int(self.y)

        # Shield
        if self.shield > 0:
            pygame.draw.circle(
                screen,
                CYAN,
                (x, y),
                48,
                3
            )

        # Main body
        pygame.draw.polygon(
            screen,
            BLUE,
            [
                (x, y - 35),
                (x - 25, y + 30),
                (x, y + 20),
                (x + 25, y + 30)
            ]
        )

        # Wings
        pygame.draw.polygon(
            screen,
            CYAN,
            [
                (x - 10, y),
                (x - 50, y + 25),
                (x - 20, y + 30),
                (x, y + 15)
            ]
        )

        pygame.draw.polygon(
            screen,
            CYAN,
            [
                (x + 10, y),
                (x + 50, y + 25),
                (x + 20, y + 30),
                (x, y + 15)
            ]
        )

        # Cockpit
        pygame.draw.ellipse(
            screen,
            WHITE,
            (x - 8, y - 20, 16, 22)
        )

        pygame.draw.ellipse(
            screen,
            LIGHT_BLUE,
            (x - 5, y - 17, 10, 15)
        )

        # Engine
        pygame.draw.polygon(
            screen,
            ORANGE,
            [
                (x - 8, y + 28),
                (x, y + 48 + random.randint(0, 8)),
                (x + 8, y + 28)
            ]
        )

    def get_rect(self):
        return pygame.Rect(
            self.x - 25,
            self.y - 30,
            50,
            60
        )


player = Player()


# ============================================================
# ENEMY CLASS
# ============================================================

enemies = []


class Enemy:
    def __init__(self, enemy_type=0):
        self.enemy_type = enemy_type

        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-200, -50)

        if enemy_type == 0:
            # Basic enemy
            self.width = 45
            self.height = 45
            self.speed = random.uniform(2, 3.5)
            self.health = 3
            self.max_health = 3
            self.color = RED
            self.score = 20
            self.shoot_timer = random.randint(80, 180)

        elif enemy_type == 1:
            # Fast enemy
            self.width = 35
            self.height = 35
            self.speed = random.uniform(4, 6)
            self.health = 2
            self.max_health = 2
            self.color = PINK
            self.score = 35
            self.shoot_timer = random.randint(120, 220)

        elif enemy_type == 2:
            # Heavy enemy
            self.width = 65
            self.height = 65
            self.speed = random.uniform(1, 2)
            self.health = 10
            self.max_health = 10
            self.color = PURPLE
            self.score = 80
            self.shoot_timer = random.randint(70, 150)

        else:
            # Zigzag enemy
            self.width = 50
            self.height = 50
            self.speed = random.uniform(2, 3)
            self.health = 5
            self.max_health = 5
            self.color = ORANGE
            self.score = 60
            self.shoot_timer = random.randint(90, 160)

        self.wave_offset = random.uniform(0, math.pi * 2)
        self.time = 0

    def update(self):
        self.time += 0.05

        self.y += self.speed

        if self.enemy_type == 3:
            self.x += math.sin(
                self.time * 3 + self.wave_offset
            ) * 3

        self.x = clamp(
            self.x,
            self.width / 2,
            WIDTH - self.width / 2
        )

        self.shoot_timer -= 1

        if self.shoot_timer <= 0:

            if self.enemy_type == 1:
                # Fast enemy shoots a little less
                self.shoot_timer = random.randint(140, 230)

            else:
                self.shoot_timer = random.randint(80, 180)

            self.shoot()

    def shoot(self):
        if self.enemy_type == 2:
            # Heavy enemy fires 3 bullets
            enemy_bullets.append(
                EnemyBullet(
                    self.x,
                    self.y + 25,
                    -1.5,
                    5
                )
            )

            enemy_bullets.append(
                EnemyBullet(
                    self.x,
                    self.y + 25,
                    0,
                    6
                )
            )

            enemy_bullets.append(
                EnemyBullet(
                    self.x,
                    self.y + 25,
                    1.5,
                    5
                )
            )

        else:
            dx = player.x - self.x
            dy = player.y - self.y

            length = math.sqrt(dx * dx + dy * dy)

            if length != 0:
                dx = dx / length * 4
                dy = dy / length * 4
            else:
                dx = 0
                dy = 4

            enemy_bullets.append(
                EnemyBullet(
                    self.x,
                    self.y + self.height / 2,
                    dx,
                    dy
                )
            )

    def take_damage(self, damage):
        self.health -= damage

        create_explosion(
            self.x,
            self.y,
            YELLOW,
            5
        )

        if self.health <= 0:
            destroy_enemy(self)

    def draw(self):
        x = int(self.x)
        y = int(self.y)

        # Main body
        pygame.draw.polygon(
            screen,
            self.color,
            [
                (x, y + self.height / 2),
                (x - self.width / 2, y - self.height / 2),
                (x, y - self.height / 4),
                (x + self.width / 2, y - self.height / 2)
            ]
        )

        # Wings
        pygame.draw.polygon(
            screen,
            self.color,
            [
                (x, y),
                (x - self.width / 2 - 15, y + 15),
                (x - self.width / 3, y + 25),
                (x, y + 10)
            ]
        )

        pygame.draw.polygon(
            screen,
            self.color,
            [
                (x, y),
                (x + self.width / 2 + 15, y + 15),
                (x + self.width / 3, y + 25),
                (x, y + 10)
            ]
        )

        # Cockpit
        pygame.draw.circle(
            screen,
            BLACK,
            (x, y - 10),
            7
        )

        # Health bar
        if self.health < self.max_health:

            draw_health_bar(
                x - self.width / 2,
                y - self.height / 2 - 10,
                self.width,
                5,
                self.health,
                self.max_health
            )

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )


# ============================================================
# BOSS
# ============================================================

boss = None


class Boss:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = -150

        self.width = 180
        self.height = 130

        self.max_health = 500
        self.health = self.max_health

        self.speed = 3

        self.direction = 1

        self.shoot_timer = 80

        self.active = True

        self.phase = 1

    def update(self):
        if self.y < 130:
            self.y += 1.5
            return

        self.x += self.speed * self.direction

        if self.x < 120:
            self.direction = 1

        if self.x > WIDTH - 120:
            self.direction = -1

        self.shoot_timer -= 1

        if self.shoot_timer <= 0:
            self.shoot_timer = 50

            self.shoot()

        # Boss phases
        health_ratio = self.health / self.max_health

        if health_ratio < 0.5:
            self.phase = 2
            self.speed = 4

        if health_ratio < 0.25:
            self.phase = 3
            self.speed = 5

    def shoot(self):
        # Center bullet
        enemy_bullets.append(
            EnemyBullet(
                self.x,
                self.y + 50,
                0,
                6,
                2
            )
        )

        # Side bullets
        enemy_bullets.append(
            EnemyBullet(
                self.x - 60,
                self.y + 40,
                -2,
                5,
                2
            )
        )

        enemy_bullets.append(
            EnemyBullet(
                self.x + 60,
                self.y + 40,
                2,
                5,
                2
            )
        )

        if self.phase >= 2:
            for angle in [-0.8, -0.4, 0.4, 0.8]:

                enemy_bullets.append(
                    EnemyBullet(
                        self.x,
                        self.y + 40,
                        math.sin(angle) * 5,
                        math.cos(angle) * 5,
                        2
                    )
                )

    def take_damage(self, damage):
        self.health -= damage

        create_explosion(
            self.x + random.randint(-60, 60),
            self.y + random.randint(-30, 30),
            ORANGE,
            4
        )

        if self.health <= 0:
            self.active = False

            create_explosion(
                self.x,
                self.y,
                RED,
                100
            )

            create_explosion(
                self.x,
                self.y,
                YELLOW,
                70
            )

            victory()

    def draw(self):
        x = int(self.x)
        y = int(self.y)

        # Wings
        pygame.draw.polygon(
            screen,
            RED,
            [
                (x, y - 50),
                (x - 100, y + 45),
                (x - 50, y + 55),
                (x, y + 25),
                (x + 50, y + 55),
                (x + 100, y + 45)
            ]
        )

        # Main body
        pygame.draw.polygon(
            screen,
            PURPLE,
            [
                (x, y - 65),
                (x - 45, y + 50),
                (x, y + 35),
                (x + 45, y + 50)
            ]
        )

        # Cockpit
        pygame.draw.ellipse(
            screen,
            CYAN,
            (
                x - 22,
                y - 40,
                44,
                50
            )
        )

        # Boss lights
        pygame.draw.circle(
            screen,
            YELLOW,
            (x - 70, y + 20),
            8
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (x + 70, y + 20),
            8
        )

        # Health bar
        draw_health_bar(
            WIDTH // 2 - 300,
            80,
            600,
            20,
            self.health,
            self.max_health
        )

        draw_text(
            "BOSS",
            FONT_MEDIUM,
            RED,
            WIDTH // 2,
            60
        )

    def get_rect(self):
        return pygame.Rect(
            self.x - 90,
            self.y - 60,
            180,
            120
        )


# ============================================================
# POWER UPS
# ============================================================

powerups = []


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y

        self.power_type = power_type

        self.speed = 2

        self.radius = 18

        self.angle = 0

    def update(self):
        self.y += self.speed
        self.angle += 0.08

    def draw(self):
        colors = {
            "health": GREEN,
            "shield": CYAN,
            "rapid": YELLOW,
            "life": PINK
        }

        color = colors.get(
            self.power_type,
            WHITE
        )

        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            self.radius
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x), int(self.y)),
            self.radius,
            2
        )

        symbols = {
            "health": "+",
            "shield": "S",
            "rapid": "R",
            "life": "♥"
        }

        draw_text(
            symbols[self.power_type],
            FONT_MEDIUM,
            BLACK,
            self.x,
            self.y
        )

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


# ============================================================
# GAME VARIABLES
# ============================================================

score = 0
level = 1

enemies_destroyed = 0

combo = 0
combo_timer = 0

enemy_spawn_timer = 0

boss_level = 5


# ============================================================
# RESET GAME
# ============================================================


def reset_game():
    global score
    global level
    global enemies_destroyed
    global combo
    global combo_timer
    global enemy_spawn_timer
    global boss

    score = 0
    level = 1

    enemies_destroyed = 0

    combo = 0
    combo_timer = 0

    enemy_spawn_timer = 0

    bullets.clear()
    enemy_bullets.clear()
    enemies.clear()
    powerups.clear()
    particles.clear()

    boss = None

    player.reset()


# ============================================================
# DESTROY ENEMY
# ============================================================


def destroy_enemy(enemy):
    global score
    global enemies_destroyed
    global combo
    global combo_timer
    global level

    if enemy not in enemies:
        return

    enemies.remove(enemy)

    enemies_destroyed += 1

    combo += 1
    combo_timer = 180

    multiplier = min(5, 1 + combo // 5)

    score += enemy.score * multiplier

    create_explosion(
        enemy.x,
        enemy.y,
        enemy.color,
        35
    )

    # Chance of power-up
    if random.random() < 0.15:

        power_type = random.choice(
            [
                "health",
                "shield",
                "rapid",
                "life"
            ]
        )

        powerups.append(
            PowerUp(
                enemy.x,
                enemy.y,
                power_type
            )
        )

    # Level up
    new_level = 1 + enemies_destroyed // 10

    if new_level > level:
        level = new_level

        create_explosion(
            WIDTH // 2,
            HEIGHT // 2,
            CYAN,
            50
        )


# ============================================================
# APPLY POWER UP
# ============================================================


def collect_powerup(powerup):
    global score

    if powerup.power_type == "health":

        player.health = min(
            player.max_health,
            player.health + 40
        )

    elif powerup.power_type == "shield":

        player.shield = 600

    elif powerup.power_type == "rapid":

        player.rapid_fire = 600

    elif powerup.power_type == "life":

        player.lives = min(
            5,
            player.lives + 1
        )

    score += 50

    create_explosion(
        powerup.x,
        powerup.y,
        GREEN,
        20
    )


# ============================================================
# SPAWN ENEMIES
# ============================================================


def spawn_enemy():
    global enemy_spawn_timer

    enemy_spawn_timer -= 1

    if enemy_spawn_timer > 0:
        return

    # More enemies at higher levels
    enemy_spawn_timer = max(
        15,
        60 - level * 4
    )

    chance = random.random()

    if level < 3:

        enemy_type = 0

    elif level < 5:

        if chance < 0.6:
            enemy_type = 0
        else:
            enemy_type = 1

    else:

        if chance < 0.45:
            enemy_type = 0

        elif chance < 0.7:
            enemy_type = 1

        elif chance < 0.9:
            enemy_type = 3

        else:
            enemy_type = 2

    enemies.append(
        Enemy(enemy_type)
    )


# ============================================================
# BOSS SPAWN
# ============================================================


def spawn_boss():
    global boss

    if boss is None:

        boss = Boss()

        enemies.clear()

        enemy_bullets.clear()

        create_explosion(
            WIDTH // 2,
            100,
            PURPLE,
            60
        )


# ============================================================
# COLLISION CHECKING
# ============================================================


def check_collisions():

    # Player bullets vs enemies
    for bullet in bullets[:]:

        if not bullet.active:
            continue

        bullet_rect = bullet.get_rect()

        for enemy in enemies[:]:

            if bullet_rect.colliderect(
                enemy.get_rect()
            ):

                enemy.take_damage(
                    bullet.damage
                )

                bullet.active = False
                break

        # Bullet vs boss
        if (
            boss is not None
            and boss.active
            and bullet.active
        ):

            if bullet_rect.colliderect(
                boss.get_rect()
            ):

                boss.take_damage(
                    bullet.damage
                )

                bullet.active = False

    # Enemy bullets vs player
    player_rect = player.get_rect()

    for bullet in enemy_bullets:

        if bullet.active:

            if player_rect.colliderect(
                bullet.get_rect()
            ):

                bullet.active = False

                player.take_damage(
                    bullet.damage * 10
                )

    # Enemies vs player
    for enemy in enemies[:]:

        if player_rect.colliderect(
            enemy.get_rect()
        ):

            player.take_damage(30)

            if enemy in enemies:
                enemies.remove(enemy)

            create_explosion(
                enemy.x,
                enemy.y,
                RED,
                30
            )

    # Boss vs player
    if boss is not None and boss.active:

        if player_rect.colliderect(
            boss.get_rect()
        ):

            player.take_damage(50)

    # Powerups vs player
    for powerup in powerups[:]:

        if player_rect.colliderect(
            powerup.get_rect()
        ):

            collect_powerup(powerup)

            powerups.remove(powerup)


# ============================================================
# CLEAN OBJECTS
# ============================================================


def clean_objects():

    for bullet in bullets[:]:

        if not bullet.active:
            bullets.remove(bullet)

    for bullet in enemy_bullets[:]:

        if not bullet.active:
            enemy_bullets.remove(bullet)

    for enemy in enemies[:]:

        if enemy.y > HEIGHT + 100:

            enemies.remove(enemy)

    for powerup in powerups[:]:

        if powerup.y > HEIGHT + 50:

            powerups.remove(powerup)


# ============================================================
# GAME OVER
# ============================================================


def end_game():
    global game_state
    global high_score

    game_state = GAME_OVER

    if score > high_score:

        high_score = score

        save_high_score(
            high_score
        )


# ============================================================
# VICTORY
# ============================================================


def victory():
    global game_state
    global high_score

    game_state = VICTORY

    if score > high_score:

        high_score = score

        save_high_score(
            high_score
        )


# ============================================================
# HUD
# ============================================================


def draw_hud():

    # Top panel
    pygame.draw.rect(
        screen,
        (10, 15, 45),
        (0, 0, WIDTH, 100)
    )

    pygame.draw.line(
        screen,
        CYAN,
        (0, 99),
        (WIDTH, 99),
        2
    )

    draw_text(
        "SARACHYAN",
        FONT_MEDIUM,
        CYAN,
        20,
        18,
        center=False
    )

    draw_text(
        f"SCORE: {score}",
        FONT_MEDIUM,
        WHITE,
        20,
        55,
        center=False
    )

    draw_text(
        f"LEVEL: {level}",
        FONT_MEDIUM,
        YELLOW,
        280,
        55,
        center=False
    )

    draw_text(
        f"HIGH: {high_score}",
        FONT_MEDIUM,
        ORANGE,
        450,
        55,
        center=False
    )

    draw_text(
        f"LIVES: {player.lives}",
        FONT_MEDIUM,
        RED,
        750,
        55,
        center=False
    )

    # Health
    draw_health_bar(
        750,
        20,
        220,
        18,
        player.health,
        player.max_health
    )

    # Combo
    if combo > 1 and combo_timer > 0:

        multiplier = min(
            5,
            1 + combo // 5
        )

        draw_text(
            f"COMBO x{multiplier}",
            FONT_MEDIUM,
            ORANGE,
            WIDTH // 2,
            125
        )

    # Powerup indicators
    y = HEIGHT - 35

    if player.rapid_fire > 0:

        draw_text(
            f"RAPID FIRE {player.rapid_fire // 60 + 1}s",
            FONT_SMALL,
            YELLOW,
            20,
            y,
            center=False
        )

    if player.shield > 0:

        draw_text(
            f"SHIELD {player.shield // 60 + 1}s",
            FONT_SMALL,
            CYAN,
            250,
            y,
            center=False
        )


# ============================================================
# UPDATE GAME
# ============================================================


def update_game():

    global combo_timer

    player.update()

    # Shoot continuously when holding SPACE
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        player.shoot()

    # Update bullets
    for bullet in bullets:
        bullet.update()

    # Update enemy bullets
    for bullet in enemy_bullets:
        bullet.update()

    # Boss
    if boss is not None and boss.active:

        boss.update()

    else:

        # Boss every 5 levels
        if level >= boss_level:

            spawn_boss()

        else:

            spawn_enemy()

            for enemy in enemies:
                enemy.update()

    # Update powerups
    for powerup in powerups:
        powerup.update()

    # Collision
    check_collisions()

    # Clean
    clean_objects()

    # Particles
    update_particles()

    # Combo timer
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo = 0


# ============================================================
# DRAW GAME
# ============================================================


def draw_game():

    update_background()

    # Objects
    for powerup in powerups:
        powerup.draw()

    for bullet in bullets:
        bullet.draw()

    for bullet in enemy_bullets:
        bullet.draw()

    for enemy in enemies:
        enemy.draw()

    if boss is not None and boss.active:
        boss.draw()

    player.draw()

    draw_particles()

    draw_hud()


# ============================================================
# MENU SCREEN
# ============================================================


def draw_menu():

    update_background()

    # Decorative explosions
    pygame.draw.circle(
        screen,
        (20, 40, 100),
        (WIDTH // 2, 320),
        200
    )

    draw_text(
        "SARACHYAN",
        FONT_HUGE,
        CYAN,
        WIDTH // 2,
        170
    )

    draw_text(
        "ADVANCED AIRPLANE SHOOTING",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        245
    )

    pygame.draw.rect(
        screen,
        (20, 40, 90),
        (
            WIDTH // 2 - 170,
            300,
            340,
            70
        ),
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            WIDTH // 2 - 170,
            300,
            340,
            70
        ),
        3,
        border_radius=15
    )

    draw_text(
        "PRESS ENTER TO START",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        335
    )

    draw_text(
        "ARROW KEYS = MOVE",
        FONT_SMALL,
        WHITE,
        WIDTH // 2,
        430
    )

    draw_text(
        "SPACE = SHOOT",
        FONT_SMALL,
        WHITE,
        WIDTH // 2,
        460
    )

    draw_text(
        "P = PAUSE",
        FONT_SMALL,
        WHITE,
        WIDTH // 2,
        490
    )

    draw_text(
        f"HIGH SCORE: {high_score}",
        FONT_MEDIUM,
        YELLOW,
        WIDTH // 2,
        560
    )

    draw_text(
        "Good luck, pilot!",
        FONT_SMALL,
        CYAN,
        WIDTH // 2,
        620
    )


# ============================================================
# PAUSE SCREEN
# ============================================================


def draw_pause():

    draw_game()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 170)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "PAUSED",
        FONT_HUGE,
        CYAN,
        WIDTH // 2,
        280
    )

    draw_text(
        "Press P to continue",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        370
    )

    draw_text(
        "Press ESC to quit",
        FONT_SMALL,
        GRAY,
        WIDTH // 2,
        420
    )


# ============================================================
# GAME OVER SCREEN
# ============================================================


def draw_game_over():

    update_background()

    draw_text(
        "GAME OVER",
        FONT_HUGE,
        RED,
        WIDTH // 2,
        200
    )

    draw_text(
        "SARACHYAN",
        FONT_LARGE,
        CYAN,
        WIDTH // 2,
        280
    )

    draw_text(
        f"FINAL SCORE: {score}",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        350
    )

    draw_text(
        f"HIGH SCORE: {high_score}",
        FONT_MEDIUM,
        YELLOW,
        WIDTH // 2,
        395
    )

    draw_text(
        "Press R to restart",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        480
    )

    draw_text(
        "Press ESC to quit",
        FONT_SMALL,
        GRAY,
        WIDTH // 2,
        530
    )


# ============================================================
# VICTORY SCREEN
# ============================================================


def draw_victory():

    update_background()

    # Celebration particles
    for _ in range(2):
        particles.append(
            Particle(
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.choice(
                    [
                        CYAN,
                        YELLOW,
                        PINK,
                        GREEN,
                        PURPLE
                    ]
                ),
                speed=random.uniform(1, 4),
                lifetime=50,
                size=random.randint(2, 6)
            )
        )

    update_particles()
    draw_particles()

    draw_text(
        "VICTORY!",
        FONT_HUGE,
        YELLOW,
        WIDTH // 2,
        180
    )

    draw_text(
        "SARACHYAN",
        FONT_LARGE,
        CYAN,
        WIDTH // 2,
        270
    )

    draw_text(
        "BOSS DEFEATED!",
        FONT_MEDIUM,
        GREEN,
        WIDTH // 2,
        330
    )

    draw_text(
        f"SCORE: {score}",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        390
    )

    draw_text(
        f"HIGH SCORE: {high_score}",
        FONT_MEDIUM,
        YELLOW,
        WIDTH // 2,
        430
    )

    draw_text(
        "Press R to play again",
        FONT_MEDIUM,
        WHITE,
        WIDTH // 2,
        510
    )

    draw_text(
        "Press ESC to quit",
        FONT_SMALL,
        GRAY,
        WIDTH // 2,
        555
    )


# ============================================================
# EVENT HANDLING
# ============================================================


def handle_events():

    global game_state

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # Quit
            if event.key == pygame.K_ESCAPE:

                pygame.quit()
                sys.exit()

            # MENU
            if game_state == MENU:

                if event.key == pygame.K_RETURN:

                    reset_game()
                    game_state = PLAYING

            # PLAYING
            elif game_state == PLAYING:

                if event.key == pygame.K_p:

                    game_state = PAUSED

            # PAUSED
            elif game_state == PAUSED:

                if event.key == pygame.K_p:

                    game_state = PLAYING

            # GAME OVER
            elif game_state == GAME_OVER:

                if event.key == pygame.K_r:

                    reset_game()
                    game_state = PLAYING

            # VICTORY
            elif game_state == VICTORY:

                if event.key == pygame.K_r:

                    reset_game()
                    game_state = PLAYING


# ============================================================
# MAIN GAME LOOP
# ============================================================


running = True

while running:

    clock.tick(FPS)

    handle_events()

    # ========================================================
    # MENU
    # ========================================================

    if game_state == MENU:

        draw_menu()

    # ========================================================
    # PLAYING
    # ========================================================

    elif game_state == PLAYING:

        update_game()

        draw_game()

    # ========================================================
    # PAUSED
    # ========================================================

    elif game_state == PAUSED:

        draw_pause()

    # ========================================================
    # GAME OVER
    # ========================================================

    elif game_state == GAME_OVER:

        draw_game_over()

    # ========================================================
    # VICTORY
    # ========================================================

    elif game_state == VICTORY:

        draw_victory()

    pygame.display.flip()


# ============================================================
# END
# ============================================================

pygame.quit()
sys.exit()