import random
import sys
import numpy
import pygame
from pygame.locals import *

SW = 600
SH = 600

BASEY = SH * 0.8
BASEX = 0
IMAGES = {}
pygame.font.init()
WINDOW = pygame.display.set_mode((SW, SH))
Font = pygame.font.SysFont("comicsans", 30)
with open('data.txt', "r") as f:
    a = [str(i) for i in f.read().split()]
Q = numpy.zeros((600, 1200, 2), dtype=float)
p = 0
for i in range(600):    # doc du lieu tu file data.txt
    for j in range(1200):
        for k in range(2):
            Q[i][j][k] = float(a[p])
            p += 1
FPS = 60

def game_start(generation, max_score):
    score = 0                  #luu diem
    birdxpos = int(SW / 5)     #toa do x cua chim = 1/5 chieu ngang man hinh
    birdypos = int(SH / 2)      #toa do y cua chim = 1/2 chieu ngang man hinh
    basex1 = 0                  #vi tri anh base 1
    basex2 = SW                 # vi tri anh base 2 thay the cho anh 1 khi anh 1 chay het man hinh

    bgx1 = 0                                    #anh background 1
    bgx2 = IMAGES['background'].get_width()     #anh background 2 thay the cho anh background 1 khi anh 1 chay het man hinh

    newPipe1 = get_new_pipe()                   #tao ong moi
    newPipe2 = get_new_pipe()

    up_pipes = [
        {'x': SW + 0, 'y': newPipe1[0]['y']},        #gan vi tri cho ong tren (co 2 ong tren)
        {'x': SW + 400, 'y': newPipe2[0]['y']}
    ]

    bttm_pipes = [
        {'x': SW + 0, 'y': newPipe1[1]['y']},       #gan vi tri cho ong duoi (co 2 ong duoi)
        {'x': SW + 400, 'y': newPipe2[1]['y']}
    ]

    pipeVelx = -4

    flyVel = -10      #toc do bay len
    fallMaxVel = 10    #toc do toi da khi roi cua chim
    originVel = -10      #toc do bay len
    flapped = False     #trang thai bay

    while True:

        x_prev, y_prev = calculate(birdxpos, birdypos, bttm_pipes)    #toa do cu cua chim
        jump = ai_play(x_prev, y_prev)                              #tim hanh dong tiep theo

        for event in pygame.event.get():     #kiem tra su kien thoat game
            if event.type == QUIT:
                with open('data.txt', "w") as f:  # ghi file
                    for i in range(600):
                        for j in range(1200):
                            for k in range(2):
                                f.write(str(Q[i][j][k]) + " ")
                pygame.quit()
                sys.exit()


        if jump:
            if birdypos > 0:      #khi chim chua tram bien tren
                flyVel = originVel      #gan cho chim van toc bay len
                flapped = True          # set trang thai bay bang true


        playerMidPos = birdxpos + IMAGES['bird'].get_width() / 2
        for pipe in up_pipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        if flyVel < fallMaxVel and not flapped:      #giam van toc bay len
            flyVel += 1

        if flapped:
            flapped = False     # set la trang thai bay bang false

        playerHeight = IMAGES['bird'].get_height()

        birdypos = birdypos + min(flyVel, BASEY - birdypos - playerHeight)

        for upperPipe, lowerPipe in zip(up_pipes, bttm_pipes):
            upperPipe['x'] += pipeVelx
            lowerPipe['x'] += pipeVelx

        if 0 < up_pipes[0]['x'] < 5:
            newPipe = get_new_pipe()
            up_pipes.append(newPipe[0])
            bttm_pipes.append(newPipe[1])

        if up_pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            up_pipes.pop(0)
            bttm_pipes.pop(0)
        basex1 -= 4
        basex2 -= 4
        if basex1 <= -IMAGES['base'].get_width():
            basex1 = basex2
            basex2 = basex1 + IMAGES['base'].get_width()

        bgx1 -= 4
        bgx2 -= 4
        if bgx1 <= -IMAGES['background'].get_width():
            bgx1 = bgx2
            bgx2 = bgx1 + IMAGES['background'].get_width()
        crashTest = Collision(birdxpos, birdypos, up_pipes, bttm_pipes)
        x_new, y_new = calculate(birdxpos, birdypos, bttm_pipes)
        if crashTest:
            reward = -1
            Q_update(x_prev, y_prev, jump, reward, x_new, y_new)

            return score

        reward = 1
        Q_update(x_prev, y_prev, jump, reward, x_new, y_new)

        WINDOW.blit(IMAGES['background'], (bgx1, 0))
        WINDOW.blit(IMAGES['background'], (bgx2, 0))
        for upperPipe, lowerPipe in zip(up_pipes, bttm_pipes):
            WINDOW.blit(IMAGES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            WINDOW.blit(IMAGES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        WINDOW.blit(IMAGES['base'], (basex1, BASEY))
        WINDOW.blit(IMAGES['base'], (basex2, BASEY))
        text1 = Font.render("Score: " + str(score), True, (255, 255, 255))
        text3 = Font.render("Max: " + str(max_score), True, (255, 255, 255))
        text2 = Font.render("Episode: " + str(episode), True, (255, 255, 255))
        WINDOW.blit(text1, (SW - 10 - text1.get_width(), 10))
        WINDOW.blit(text3, (SW - 10 - text3.get_width(), 50))
        WINDOW.blit(text2, (0, 0))
        WINDOW.blit(IMAGES['bird'], (birdxpos, birdypos))
        pygame.display.update()
        FPSCLOCK.tick(FPS*1000)


def Collision(birdxpos, birdypos, up_pipes, bttm_pipes):
    if birdypos >= BASEY - IMAGES['bird'].get_height() or birdypos < 0:
        return True
    for pipe in up_pipes:
        pipeHeight = IMAGES['pipe'][0].get_height()
        if birdypos < pipeHeight + pipe['y'] and \
                abs(birdxpos - pipe['x']) < IMAGES['pipe'][0].get_width():
            return True

    for pipe in bttm_pipes:
        if birdypos + IMAGES['bird'].get_height() > pipe['y'] and \
                abs(birdxpos - pipe['x']) < IMAGES['pipe'][
            0].get_width():
            return True
    return False


def get_new_pipe():    #sinh ong moi
    pipeHeight = IMAGES['pipe'][1].get_height()             #lay chieu cao cua ong
    gap = int(SH / 3)                                       #lo hong giua ong tren vao ong duoi
    # y2 = int(gap + random.randrange(0, int(SH - IMAGES['base'].get_height() - gap)))
    y2 = int(gap + random.randrange(100, 105))
    pipex = int(SW + 400)
    y1 = int(pipeHeight - y2 + gap)
    pipe = [
        {'x': pipex, 'y': -y1},
        {'x': pipex, 'y': y2}
    ]
    return pipe


def ai_play(x, y):
    jump = False
    if Q[x][y][1] > Q[x][y][0]:
        jump = True
    return jump


def calculate(birdxpos, birdypos, bttm_pipes):
    x = min(SW, bttm_pipes[0]['x']-birdxpos)
    y = (bttm_pipes[0]['y'] + birdypos)/2
    return int(x)-1, int(y)


def Q_update(x_prev, y_prev, jump, reward, x_new, y_new):      # cap nhat ma tran Q
    if jump:
        Q[x_prev][y_prev][1] = Q[x_prev][y_prev][1] + \
        0.5 * (reward + max(Q[x_new][y_new][0], Q[x_new][y_new][1])-Q[x_prev][y_prev][1])
    else:
        Q[x_prev][y_prev][0] = Q[x_prev][y_prev][0] + \
        0.5 * (reward + max(Q[x_new][y_new][0], Q[x_new][y_new][1])-Q[x_prev][y_prev][0])


if __name__ == "__main__":
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird with Q-learning")

    IMAGES['base'] = pygame.image.load('imgs/base.png').convert_alpha()
    IMAGES['pipe'] = (
        pygame.transform.rotate(pygame.image.load('imgs/pipe.png').convert_alpha(), 180), pygame.image.load('imgs/pipe.png').convert_alpha())
    IMAGES['background'] = pygame.image.load('imgs/bg.png').convert()
    IMAGES['bird'] = pygame.image.load('imgs/bird.png').convert_alpha()
    episode = 1
    max_score = 0
    while True:
        score = game_start(episode, max_score)
        if score == -1:
            break
        episode += 1
        if score>max_score:
            max_score=score

