import pygame
import sys
import random
import time
from backend import SpaceInvadersBackend

pygame.init()

# ----------------------------
# BASIC GAME SETUP
# ----------------------------
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
FPS = 60
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

backend = SpaceInvadersBackend()
current_user = None

# ----------------------------
# LOAD IMAGES
# ----------------------------
BACKGROUND = pygame.image.load("ships/background.png")
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

PLAYER_IMG = pygame.image.load("ships/mainShip.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (150, 90))

BULLET_IMG = pygame.image.load("ships/bullet.png")
BULLET_IMG = pygame.transform.scale(BULLET_IMG, (10, 20))

HEART_IMG = pygame.image.load("ships/heart.png")
HEART_IMG = pygame.transform.scale(HEART_IMG, (30, 30))

ENEMY_IMAGES = []
for i in range(1, 13):
    img = pygame.image.load(f"ships/level{i}.png")
    img = pygame.transform.scale(img, (160, 120))
    ENEMY_IMAGES.append(img)

BOSS_IMG = pygame.image.load("ships/boss.png")
BOSS_IMG = pygame.transform.scale(BOSS_IMG, (400, 200))

LASER_IMG = pygame.image.load("ships/laser.png")
LASER_IMG = pygame.transform.scale(LASER_IMG, (40, HEIGHT))

SECRET_IMG = pygame.image.load("ships/levelSecret.png")
SECRET_IMG = pygame.transform.scale(SECRET_IMG, (160, 120))


# ----------------------------
# DRAW TEXT FUNCTION
# ----------------------------
def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size)
    label = font.render(text, True, color)
    WIN.blit(label, (x - label.get_width() // 2, y))


# ----------------------------
# INPUT BOX CLASS
# ----------------------------
class InputBox:
    def __init__(self, x, y, w, h, placeholder=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ''
        self.placeholder = placeholder
        self.active = False
        self.is_password = 'password' in placeholder.lower()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN and len(self.text) < 20:
                self.text += event.unicode

    def draw(self, win):
        color = WHITE if self.active else GRAY
        pygame.draw.rect(win, color, self.rect, 2)
        font = pygame.font.SysFont("Arial", 24)

        if self.text:
            display_text = '*' * len(self.text) if self.is_password else self.text
            txt_surface = font.render(display_text, True, WHITE)
        else:
            txt_surface = font.render(self.placeholder, True, GRAY)

        win.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))


# ----------------------------
# BUTTON CLASS
# ----------------------------
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hovered = False

    def draw(self, win):
        color = WHITE if self.hovered else GRAY
        pygame.draw.rect(win, color, self.rect, 2)
        draw_text(self.text, 28, self.rect.centerx, self.rect.centery, WHITE)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)


# ----------------------------
# LOGIN/SIGNUP SCREEN
# ----------------------------
def auth_screen():
    global current_user

    username_box = InputBox(WIDTH // 2 - 150, HEIGHT // 2 - 80, 300, 40, 'Username')
    password_box = InputBox(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40, 'Password')

    login_btn = Button(WIDTH // 2 - 160, HEIGHT // 2 + 50, 140, 50, 'Login')
    signup_btn = Button(WIDTH // 2 + 20, HEIGHT // 2 + 50, 140, 50, 'Sign Up')

    message = ''
    message_color = WHITE

    running = True
    while running:
        WIN.blit(BACKGROUND, (0, 0))
        draw_text("SPACE INVADERS", 60, WIDTH // 2, HEIGHT // 2 - 180)

        mouse_pos = pygame.mouse.get_pos()
        login_btn.update_hover(mouse_pos)
        signup_btn.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            username_box.handle_event(event)
            password_box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_btn.is_clicked(event.pos):
                    result = backend.login(username_box.text, password_box.text)
                    if result['success']:
                        current_user = username_box.text
                        return
                    else:
                        message = result['message']
                        message_color = RED

                elif signup_btn.is_clicked(event.pos):
                    result = backend.sign_up(username_box.text, password_box.text)
                    message = result['message']
                    message_color = GREEN if result['success'] else RED

        username_box.draw(WIN)
        password_box.draw(WIN)
        login_btn.draw(WIN)
        signup_btn.draw(WIN)

        if message:
            draw_text(message, 20, WIDTH // 2, HEIGHT // 2 + 130, message_color)

        pygame.display.update()
        clock.tick(FPS)


# ----------------------------
# PLAYER CLASS
# ----------------------------
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 6
        self.width = 150
        self.height = 90
        self.lives = 12

    def draw(self, win):
        win.blit(PLAYER_IMG, (self.x, self.y))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed


# ----------------------------
# BULLET CLASS
# ----------------------------
class Bullet:
    def __init__(self, x, y, speed, is_enemy=False, size=20):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.is_enemy = is_enemy
        self.img = pygame.transform.scale(BULLET_IMG, (10 if not is_enemy else 18, size))

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self):
        self.y += self.speed


# ----------------------------
# ENEMY CLASS (regular enemies no boss bar)
# ----------------------------
class Enemy:
    def __init__(self, x, y, img, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.img = img
        self.width = img.get_width()
        self.height = img.get_height()

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self):
        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.speed *= -1
            self.y += 20


# ----------------------------
# BOSS CLASS
# ----------------------------
class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - 200
        self.y = 50
        self.width = 400
        self.height = 200
        self.health = 15
        self.speed = 6
        self.laser_active = False
        self.laser_warning = False
        self.laser_x = self.x + self.width // 2 - 20
        self.laser_cooldown = 200
        self.laser_timer = 0

    def draw(self, win):
        win.blit(BOSS_IMG, (self.x, self.y))
        if self.laser_active:
            win.blit(LASER_IMG, (self.laser_x, 0))
        pygame.draw.rect(win, RED, (self.x, self.y - 10, self.width, 10))
        pygame.draw.rect(win, GREEN, (self.x, self.y - 10, int(self.width * self.health / 15), 10))

    def move(self):
        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.speed *= -1
        self.laser_x = self.x + self.width // 2 - 20


# ----------------------------
# SECRET SHIP CLASS
# ----------------------------
class SecretShip:
    def __init__(self):
        self.x = WIDTH // 2 - 80
        self.y = 100
        self.width = 160
        self.height = 120
        self.img = SECRET_IMG
        self.health = int(15 * 3 / 4)
        self.speed = 7
        self.transparent = False
        self.timer = 0
        self.shoot_timer = 0

    def draw(self, win):
        if not self.transparent:
            win.blit(self.img, (self.x, self.y))
            pygame.draw.rect(win, RED, (self.x, self.y - 10, self.width, 10))
            pygame.draw.rect(win, GREEN, (self.x, self.y - 10, int(self.width * self.health / (15 * 3 / 4)), 10))

    def move(self):
        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.speed *= -1
        self.timer += 1
        if self.timer >= 300:
            self.transparent = not self.transparent
            self.timer = 0


# ----------------------------
# MENU & SCREENS
# ----------------------------
def menu_screen():
    running = True
    while running:
        WIN.blit(BACKGROUND, (0, 0))
        draw_text("SPACE INVADERS", 60, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text("Press ENTER to Play", 32, WIDTH // 2, HEIGHT // 2 + 20)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False


def leaderboard_screen():
    result = backend.get_leaderboard()
    leaderboard = result.get('leaderboard', [])

    running = True
    while running:
        WIN.blit(BACKGROUND, (0, 0))
        draw_text("LEADERBOARD", 60, WIDTH // 2, 80)

        y_pos = 160
        for i, entry in enumerate(leaderboard):
            draw_text(f"{i + 1}. {entry['username']}: {entry['score']}", 32, WIDTH // 2, y_pos)
            y_pos += 50

        draw_text("Press R to Restart or Q to Quit", 24, WIDTH // 2, HEIGHT - 60)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False


def lose_screen(score):
    global current_user

    backend.register_score(current_user, score)

    while True:
        WIN.blit(BACKGROUND, (0, 0))
        draw_text("YOU LOST!", 60, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Score: {score}", 40, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text("Press L to view Leaderboard", 30, WIDTH // 2, HEIGHT // 2 + 70)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                should_restart = leaderboard_screen()
                if should_restart:
                    return
                else:
                    pygame.quit()
                    sys.exit()


def win_screen(score):
    global current_user

    backend.register_score(current_user, score)

    while True:
        WIN.blit(BACKGROUND, (0, 0))
        draw_text("YOU WIN!", 60, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Score: {score}", 40, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text("Press L to view Leaderboard", 30, WIDTH // 2, HEIGHT // 2 + 70)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                should_restart = leaderboard_screen()
                if should_restart:
                    return
                else:
                    pygame.quit()
                    sys.exit()


# ----------------------------
# LEVEL CREATION
# ----------------------------
def create_level(level_index):
    enemies = []
    img = ENEMY_IMAGES[level_index]
    margin = 10
    cols = max(1, WIDTH // (img.get_width() + margin))
    rows = max(1, (HEIGHT // 2) // (img.get_height() + margin))
    for row in range(rows):
        for col in range(cols):
            x = col * (img.get_width() + margin) + margin
            y = row * (img.get_height() + margin) + 50
            enemies.append(Enemy(x, y, img))
    return enemies


# ----------------------------
# MAIN GAME LOOP
# ----------------------------
def main():
    player = Player()
    bullets = []
    enemy_bullets = []

    score = 0
    level_index = 0
    enemies = create_level(level_index)
    level_start_time = time.time()

    boss_fight = False
    secret_level_active = False
    secret_ship = None
    secret_done = False
    boss = Boss()

    running = True
    paused = False

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.x + player.width // 2 - 5, player.y, -7))

        if paused:
            draw_text("PAUSED", 60, WIDTH // 2, HEIGHT // 2)
            pygame.display.update()
            continue

        player.move(keys)

        for bullet in bullets[:]:
            bullet.move()
            if bullet.y < 0:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.move()
            if enemy.y + 30 >= player.y:
                lose_screen(score)
                return main()

            for bullet in bullets[:]:
                if enemy.x < bullet.x < enemy.x + enemy.width and enemy.y < bullet.y < enemy.y + enemy.height:
                    # Remove bullet safely
                    try:
                        bullets.remove(bullet)
                    except ValueError:
                        pass

                    # Remove enemy safely
                    try:
                        enemies.remove(enemy)
                    except ValueError:
                        pass

                    score += 100
                    break  # prevent double-removal attempts

        if enemies and random.randint(1, 40) == 1:
            shooter = random.choice(enemies)
            enemy_bullets.append(Bullet(shooter.x + shooter.width // 2, shooter.y + shooter.height, 7, True, 26))

        for b in enemy_bullets[:]:
            b.move()
            if b.y > HEIGHT:
                enemy_bullets.remove(b)
            elif player.x < b.x < player.x + player.width and player.y < b.y < player.y + player.height:
                enemy_bullets.remove(b)
                player.lives -= 1
                if player.lives <= 0:
                    lose_screen(score)
                    return main()

        if not enemies and not boss_fight and not secret_level_active:
            level_end_time = time.time()
            time_taken = int(level_end_time - level_start_time)
            bonus = max(0, 1000 - 125 * time_taken)
            score += bonus

            level_index += 1
            if level_index < len(ENEMY_IMAGES):
                enemies = create_level(level_index)
                level_start_time = time.time()
            else:
                if player.lives >= 6 and not secret_done:
                    secret_ship = SecretShip()
                    secret_level_active = True
                    secret_done = True
                    enemies = []
                    boss_fight = False
                    level_start_time = time.time()
                else:
                    boss_fight = True
                    level_start_time = time.time()

        if secret_level_active and secret_ship is not None:
            secret_ship.move()
            secret_ship.shoot_timer += 1
            if secret_ship.shoot_timer >= 30:
                enemy_bullets.append(
                    Bullet(secret_ship.x + secret_ship.width // 2, secret_ship.y + secret_ship.height, 10, True, 28))
                secret_ship.shoot_timer = 0
            for bullet in bullets[:]:
                if secret_ship is not None and not secret_ship.transparent and secret_ship.x < bullet.x < secret_ship.x + secret_ship.width and secret_ship.y < bullet.y < secret_ship.y + secret_ship.height:
                    bullets.remove(bullet)
                    secret_ship.health -= 1
                    if secret_ship.health <= 0:
                        secret_level_active = False
                        boss_fight = True
                        secret_ship = None
                        level_start_time = time.time()

        if boss_fight:
            boss.move()
            if random.randint(1, 55) == 1:
                enemy_bullets.append(Bullet(boss.x + boss.width // 2, boss.y + boss.height, 10, True, 28))
            boss.laser_timer += 1
            if not boss.laser_warning and boss.laser_timer >= boss.laser_cooldown:
                boss.laser_warning = True
                boss.laser_timer = 0
            elif boss.laser_warning and boss.laser_timer >= 60:
                boss.laser_warning = False
                boss.laser_active = True
                boss.laser_timer = 0
            elif boss.laser_active:
                if boss.laser_x < player.x + player.width and boss.laser_x + 40 > player.x:
                    player.lives -= 1
                    if player.lives <= 0:
                        lose_screen(score)
                        return main()
                if boss.x <= 0 or boss.x >= WIDTH - boss.width:
                    boss.laser_active = False
                    boss.laser_timer = 0
                    boss.laser_cooldown = max(60, boss.laser_cooldown - 10)

            for bullet in bullets[:]:
                if boss.x < bullet.x < boss.x + boss.width and boss.y < bullet.y < boss.y + boss.height:
                    bullets.remove(bullet)
                    boss.health -= 1
                    if boss.health <= 0:
                        bonus = max(0, 1000 - 125 * int(time.time() - level_start_time))
                        score += 5000 + bonus
                        win_screen(score)
                        return main()

        WIN.blit(BACKGROUND, (0, 0))
        player.draw(WIN)

        for i in range(player.lives):
            WIN.blit(HEART_IMG, (WIDTH - 40 * (i + 1), 20))

        for enemy in enemies:
            enemy.draw(WIN)

        for bullet in bullets:
            bullet.draw(WIN)

        for b in enemy_bullets:
            b.draw(WIN)

        if secret_level_active and secret_ship is not None:
            secret_ship.draw(WIN)

        if boss_fight:
            boss.draw(WIN)

        draw_text(f"Score: {score}", 30, 70, 20)

        pygame.display.update()


auth_screen()
menu_screen()
main()