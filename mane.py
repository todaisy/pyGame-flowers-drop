import pygame
import pygame_menu
import sqlite3
import re
from flower import Flower
from random import randint

pygame.init()
pygame.time.set_timer(pygame.USEREVENT, 2000)
pygame.display.set_caption('flowers drop pygame', 'img/people2.png')
f = pygame.font.SysFont('arial', 30)
W, H = 900, 600
sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
FPS = 40
game_score = 0
speed = 10
data = []
running = True
game_play = False
menu = None
player_name = 'Player1'


# база данных
db = sqlite3.connect('players_name.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS players_name ( name text, score integer)')
db.commit()


# все спрайты
people = pygame.image.load('img/people2.png')
people = pygame.transform.scale(people, (people.get_width()//5, people.get_height()//5)).convert_alpha()
people_rect = people.get_rect(centerx=W//2, bottom=H-5)
# people_right = people_rect
# people_left = pygame.transform.flip(people, 1, 0)
trig = pygame.image.load('img/trigger.png')
trig_rect = trig.get_rect(centerx=W//2, y=590)

flowers_data = ({'path': 'flower1.png', 'score': 10},
                {'path': 'flower2.png', 'score': 15},
                {'path': 'flower3.png', 'score': 20})

flowers_surf = [pygame.image.load('img/'+data['path']).convert_alpha() for data in flowers_data]
flowers = pygame.sprite.Group()


def create_flower(group):
    indx = randint(0, len(flowers_surf) - 1)
    x = randint(20, W - 20)
    speed = randint(1, 4)

    return Flower(x, speed, flowers_surf[indx], flowers_data[indx]['score'], group)


def collide_flower():
    global game_score
    for flower1 in flowers:
        if people_rect.colliderect(flower1.rect):
            game_score += flower1.score
            flower1.kill()


def start_the_game():
    global game_play
    game_play = True
    menu.disable()


def my_name(name):
    global player_name
    print('Player name is', name)
    player_name = name


def show_menu1():
    global menu
    global data
    data = []
    menu = pygame_menu.Menu('flowers fall', 900, 600, theme=pygame_menu.themes.THEME_SOLARIZED)
    frame = menu.add.frame_h(500, 300, background_color=(238, 231, 213), padding=0)
    frame_left = menu.add.frame_v(250, 300, background_color=(238, 231, 213), padding=0)
    frame_right = menu.add.frame_v(250, 300, background_color=(238, 231, 213), padding=0)
    frame.pack(frame_left)
    frame.pack(frame_right)
    frame_left.pack(menu.add.text_input('Name: ', default=player_name, onchange=my_name))
    frame_left.pack(menu.add.button('Play', start_the_game))
    frame_left.pack(menu.add.button('Quit', pygame_menu.events.EXIT))

    cursor.execute('SELECT * FROM players_name ORDER BY score DESC LIMIT 5')
    for i in cursor.fetchall():
        x = re.findall("\w+", str(i))
        str_ns = ''
        for s in x:
            str_ns += s + ' '
        frame_right.pack(menu.add.label(str_ns))

    menu.mainloop(sc)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
            people_rect.x -= speed
            if people_rect.x < 0:
                people_rect.x = 0
        elif keys[pygame.K_RIGHT]:
            people_rect.x += speed
            if people_rect.x > W-people_rect.width:
                people_rect.x = W-people_rect.width

    else:
        show_menu1()

    for flower in flowers:
        if trig_rect.colliderect(flower):
            game_play = False
            print(player_name)
            data.append((player_name, game_score))
            cursor.executemany('INSERT INTO players_name VALUES (?, ?)', data)
            db.commit()
            cursor.execute('SELECT * FROM players_name')
            print(cursor.fetchall())
            game_score = 0
            flowers.empty()

    pygame.display.update()
    flowers.update(H)
    collide_flower()
    clock.tick(FPS)

db.close()
