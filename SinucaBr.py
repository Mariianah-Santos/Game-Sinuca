import pygame
import pymunk
import pymunk.pygame_util
import math
from sys import exit 
from pygame.locals import *
import os

pygame.init()

lar= 1200
alt = 678
painel = 50




tela = pygame.display.set_mode((lar, alt + painel)) #estabelecendo o tamanho da janela do jogo
pygame.display.set_caption("Game SinucaBr")
draw_options = pymunk.pygame_util.DrawOptions(tela) #estabelecendo a bola na janela

space = pymunk.Space() #criando o espaço
static_body = space.static_body
clock = pygame.time.Clock()
FPS = 120
BG = (50, 50, 50) #cor cinza para o fundo
RED = (255, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont('Latos', 30)
large_font = pygame.font.SysFont('Latos', 60)

lives = 3 #vidas
dia = 36 #jogo e variaveis
buracos = 66
força = 0 #força do bastão na bola
max_forca = 10000
forca_direc = 1
GAMEOVER = True
bastao_morto = False
taking_shot = True
ligado = False
potted_balls = []

dic_pri = os.path.dirname(__file__)
dic_imagem = os.path.join(dic_pri, 'Imagens')
bastao_imagem = pygame.image.load(os.path.join(dic_imagem, 'cue.png')).convert_alpha()
mesa_imagem = pygame.image.load(os.path.join(dic_imagem, 'table.png')).convert_alpha()
bolas_imagens = []
for i in range(1, 17):
    b_ima = pygame.image.load(os.path.join(dic_imagem, f'ball_{i}.png')).convert_alpha()
    bolas_imagens.append(b_ima)

def draw_txt(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    tela.blit(img, (x, y))
    

def criando_bola(radius, pos): #criando bola
  body = pymunk.Body()
  body.position = pos
  shape = pymunk.Circle(body, radius)
  shape.mass = 5
  shape.elasticity = 0.8
  pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0)) #criar atrito
  pivot.max_bias = 0 #desabilitar correção articular
  pivot.max_force = 1000 #emular a força do atrito ( colisão)

  space.add(body, shape, pivot)
  return shape

balls = [] #criando 2d de todas as bolas
rows = 5 #linhas do jogo (bolas)

for posi_ball in range(5): #posições das bolas
    for row in range(rows):
        pos = (250 + (posi_ball * (dia+ 1)), 267 + (row * (dia + 1)) + (posi_ball * dia / 2))#posições das bolas
        new_ball = criando_bola(dia / 2, pos) #estabeleceer a bola na janela
        balls.append(new_ball)
    rows -= 1

pos = (888, alt / 2)
bola_branca = criando_bola(dia / 2, pos) #criado a bola branca do jogo
balls.append(bola_branca)

pockets = [
    (55, 63),
    (592, 48),
    (1134, 64),
    (55, 616),
    (592, 629),
    (1134, 616)
]

paredes = [
    [(88, 56), (109, 77), (555, 77), (564, 56)], #criando paredes ao lado das bordas (buracos) para as bolas não passarem
    [(621, 56), (630, 77), (1081, 77), (1102, 56)],
  [(89, 621), (110, 600),(556, 600), (564, 621)],
  [(622, 621), (630, 600), (1081, 600), (1102, 621)],
  [(56, 96), (77, 117), (77, 560), (56, 581)],
  [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]

def criar_paredes(poly_dms):
    body = pymunk.Body(body_type = pymunk.Body.STATIC)
    body.position = ((0, 0))
    shape = pymunk.Poly(body, poly_dms)
    shape.elasticity = 0.8

    space.add(body, shape)
for c in paredes:
    criar_paredes(c)

class Bastao():
    def __init__(self, pos):
        self.original_image = bastao_imagem
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def upadete(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image,
        (self.rect.centerx - self.image.get_width() / 2,
        self.rect.centery - self.image.get_height() / 2)
        )

bastao = Bastao(balls[-1].body.position)

barra_energia = pygame.Surface((10, 20))
barra_energia.fill(RED)



while True: #criando a saida do jogo
    clock.tick(FPS)
    space.step(1 / FPS)
    

    tela.fill(BG) #cor de fundo

    tela.blit(mesa_imagem, (0, 0))

    for i, ball in enumerate(balls): #crindo os 6 buracos da mesa 
        for pocket in pockets:
            ball_x_dist = abs(ball.body.position[0] - pocket[0])
            ball_y_dist = abs(ball.body.position[1] - pocket[1])
            ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
            if ball_dist <= buracos / 2:
                if i == len(balls) - 1:
                    lives -= 1
                    bastao_morto = True
                    ball.body.position = (-100, -100)
                    ball.body.velocity = (0.0, 0.0)
                else:
                    space.remove(ball.body)
                    balls.remove(ball)
                    potted_balls.append(bolas_imagens[i])
                    bolas_imagens.pop(i)



    
    for i, ball in enumerate(balls):#inserindo as imagens no jogo
        tela.blit(bolas_imagens[i], (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))

    taking_shot = True #chekando se a bola branca estiver movimento o bastao some
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False

    if taking_shot == True and GAMEOVER == True:
        if bastao_morto == True:#reposicionando a bol branca caso ela cai no buraco
            balls[-1].body.position = (888, alt / 2)
            bastao_morto = False
        mouse_pos = pygame.mouse.get_pos() #calculando o anglo do bastao
        bastao.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = (balls[-1].body.position[1] - mouse_pos[1])
        bastao_angle = math.degrees(math.atan2(y_dist, x_dist))
        bastao.upadete(bastao_angle)
        bastao.draw(tela)

    if ligado == True and GAMEOVER == True:
        força += 100 * forca_direc
        if força >= max_forca or força <= 0:
            forca_direc *= -1
        for b in range(math.ceil(força / 2000)): #criando a barra de energia
            tela.blit(barra_energia, 
            (balls[-1].body.position[0] - 30 + (b * 15),
             balls[-1].body.position[1] + 30))

    elif ligado == False and taking_shot == True: #aumentando a força da variavel   
        x_impulse = math.cos(math.radians(bastao_angle))
        y_impulse = math.sin(math.radians(bastao_angle))
        balls[-1].body.apply_impulse_at_local_point((força * -x_impulse, força * y_impulse), (0, 0))
        força = 0
        forca_direc = 1

    pygame.draw.rect(tela, BG, (0, alt, lar, painel))#criando fundo dao paunel
    draw_txt('VIDAS: ' + str(lives), font, WHITE, lar -200, alt + 10)

    if lives <= 0: #perdeu pq todas as bolas brancas foram para o buraco
        draw_txt('GAME OVER', large_font, WHITE, lar / 2 - 160, alt / 2 - 100)
        GAMEOVER = False

    if len(balls) == 1: #por falta de mais buracos
        draw_txt('YOU WIN', large_font, WHITE, lar / 2 - 160, alt / 2 - 100)
        GAMEOVER = False

    for i, ball in enumerate(potted_balls):
        tela.blit(ball, (10 + (i * 50), alt + 10))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot == True:
            ligado = True
        if event.type == pygame.MOUSEBUTTONUP and taking_shot == True:
            ligado = False
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    #space.debug_draw(draw_options)
    pygame.display.update()
