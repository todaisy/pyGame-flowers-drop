import pygame
import pygame_menu
import sqlite3
from flower import Flower
from random import randint

# Constants
W, H = 900, 600
FPS = 40
FLOWER_DROP_INTERVAL = 2000  # ms
SPEED = 10
FLOWERS_DATA = [{'path': 'flower1.png', 'score': 10},
                {'path': 'flower2.png', 'score': 15},
                {'path': 'flower3.png', 'score': 20}]
PLAYER_NAME_DB = 'players_name.db'
PLAYER_NAME_TABLE = 'players_name'

# Initialize Pygame
pygame.init()
pygame.time.set_timer(pygame.USEREVENT, FLOWER_DROP_INTERVAL)
pygame.display.set_caption('Flowers Drop Pygame')

# Create the screen
sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
f = pygame.font.SysFont('arial', 30)
game_score = 0
game_play = False
player_name = 'Player1'

# Database
with sqlite3.connect(PLAYER_NAME_DB) as db:
    cursor = db.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {PLAYER_NAME_TABLE} (name text, score integer)')
    db.commit()

# Load images
people = pygame.image.load('img/people2.png')
people = pygame.transform.scale(people, (people.get_width() // 5, people.get_height() // 5)).convert_alpha()
people_rect = people.get_rect(centerx=W // 2, bottom=H - 5)

trig = pygame.image.load('img/trigger.png')
trig_rect = trig.get_rect(centerx=W // 2, y=590)

flowers_surf = [pygame.image.load('img/' + data['path']).convert_alpha() for data in FLOWERS_DATA]
flowers = pygame.sprite.Group()

# Load music
pygame.mixer_music.load('msc/c152-hold-up.mp3')
pygame.mixer_music.set_volume(0.3)
bubble = pygame.mixer.Sound('msc/bub.mp3')
fail = pygame.mixer.Sound('msc/fail-wha-wha-version.mp3')


# Function to create a flower
def create_flower(group):
    indx = randint(0, len(flowers_surf) - 1)
    x = randint(20, W - 20)
    speed = randint(1, 4)
    return Flower(x, speed, flowers_surf[indx], FLOWERS_DATA[indx]['score'], group)


# Function to handle collisions with flowers
def collide_flower():
    global game_score
    for flower in flowers:
        if people_rect.colliderect(flower.rect):
            game_score += flower.score
            pygame.mixer.Sound.play(bubble)
            flower.kill()


# Function to start the game
def start_the_game():
    global game_play
    game_play = True
    pygame.mixer_music.play(-1)
    menu.disable()


# Function to update the player name
def my_name(name):
    global player_name
    player_name = name


# Function to display the main menu
def show_menu():
    global menu
    menu = pygame_menu.Menu('Flowers Fall', W, H, theme=pygame_menu.themes.THEME_SOLARIZED)
    frame = menu.add.frame_h(500, 300, background_color=(238, 231, 213), padding=0)
    frame_left = menu.add.frame_v(250, 300, background_color=(238, 231, 213), padding=0)
    frame_right = menu.add.frame_v(250, 300, background_color=(238, 231, 213), padding=0)
    frame_text = menu.add.frame_h(520, 60, background_color=(238, 231, 213), padding=0)
    frame.pack(frame_left)
    frame.pack(frame_right)
    frame_text.pack(menu.add.label(f'Catch falling flowers and get points!'))
    frame_left.pack(menu.add.text_input('Name: ', default=player_name, onchange=my_name))
    frame_left.pack(menu.add.button('Play', start_the_game))
    frame_left.pack(menu.add.button('Quit', pygame_menu.events.EXIT))

    cursor.execute(f'SELECT * FROM {PLAYER_NAME_TABLE} ORDER BY score DESC LIMIT 5')
    for row in cursor.fetchall():
        name, score = row
        frame_right.pack(menu.add.label(f'{name} {score}'))

    menu.mainloop(sc)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.USEREVENT:
            create_flower(flowers)

    if game_play:
        sc.fill((255, 255, 255))
        flowers.draw(sc)
        sc_text = f.render(str(game_score), True, (191, 73, 130))
        sc.blit(sc_text, (20, 10))
        sc.blit(people, people_rect)
        sc.blit(trig, trig_rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            people_rect.x -= SPEED
            if people_rect.x < 0:
                people_rect.x = 0
        elif keys[pygame.K_RIGHT]:
            people_rect.x += SPEED
            if people_rect.x > W - people_rect.width:
                people_rect.x = W - people_rect.width

    else:
        show_menu()

    for flower in flowers:
        if trig_rect.colliderect(flower):
            game_play = False
            cursor.executemany(f'INSERT INTO {PLAYER_NAME_TABLE} VALUES (?, ?)', [(player_name, game_score)])
            db.commit()
            pygame.mixer_music.stop()
            pygame.mixer.Sound.play(fail)
            game_score = 0
            flowers.empty()

    pygame.display.update()
    flowers.update(H)
    collide_flower()
    clock.tick(FPS)
