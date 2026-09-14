"""
Lab 3 - Varredura Sensorial com Filtro de Alcance e Desvio de Ruido
NOME: BRUNO MENEZES GOMES / HENRIQUE RIBEIRO SIQUEIRA
PROF.: FLAVIO SANTARELLI - DATA: 14/09/26
CURSO: CIENCIA DA COMPUTACAO - NOTURNO
"""

import math
import numpy as np
import pygame

LARGURA, ALTURA = 900, 650
FPS = 60

N_FEIXES = 7
FOV = math.pi  # 180 graus, de -pi/2 a +pi/2
ALCANCE_MAX = 200.0
LIMIAR_MIN = 10.0
RUIDO_STD = 5.0

COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_OBSTACULO = (180, 50, 50)
COR_RAIO_BRUTO = (120, 120, 130)
COR_RAIO_OK = (0, 255, 100)
COR_RAIO_ERRO = (255, 60, 60)
COR_TEXTO = (220, 220, 220)


class SensorArray:
    def __init__(self, x, y, theta):
        self.x, self.y, self.theta = x, y, theta
        self.angulos = [
            -FOV / 2 + i * (FOV / (N_FEIXES - 1)) for i in range(N_FEIXES)
        ]
        self.brutas = [ALCANCE_MAX] * N_FEIXES
        self.filtradas = [ALCANCE_MAX] * N_FEIXES
        self.validas = [True] * N_FEIXES

    def varrer(self, obstacles):
        self.brutas, self.filtradas, self.validas = [], [], []
        for beta in self.angulos:
            angle = self.theta + beta
            d_real = ALCANCE_MAX
            for step in range(2, int(ALCANCE_MAX), 2):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    d_real = float(step)
                    break
                if any(obs.collidepoint(rx, ry) for obs in obstacles):
                    d_real = float(step)
                    break

            d_ruido = d_real + np.random.normal(0, RUIDO_STD)

            if d_ruido < LIMIAR_MIN:
                valido = False
                d_filtrada = self.filtradas[-1] if self.filtradas else ALCANCE_MAX
            elif d_ruido > ALCANCE_MAX:
                valido = True
                d_filtrada = ALCANCE_MAX
            else:
                valido = True
                d_filtrada = d_ruido

            self.brutas.append(d_ruido)
            self.filtradas.append(d_filtrada)
            self.validas.append(valido)

    def draw(self, surface):
        for i, beta in enumerate(self.angulos):
            angle = self.theta + beta
            dist_f = self.filtradas[i]
            cor = COR_RAIO_OK if self.validas[i] else COR_RAIO_ERRO
            fx = self.x + dist_f * math.cos(angle)
            fy = self.y + dist_f * math.sin(angle)
            pygame.draw.line(surface, cor, (int(self.x), int(self.y)), (int(fx), int(fy)), 2)
            pygame.draw.circle(surface, cor, (int(fx), int(fy)), 4)
        pygame.draw.circle(surface, COR_ROBO, (int(self.x), int(self.y)), 14)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 3 - Filtro de Alcance e Ruido")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13)

    sensores = SensorArray(200, 325, 0.0)
    obstacles = [
        pygame.Rect(500, 150, 120, 100),
        pygame.Rect(550, 400, 150, 150),
        pygame.Rect(750, 250, 80, 200),
    ]

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - sensores.x, my - sensores.y
        sensores.theta = math.atan2(dy, dx)

        sensores.varrer(obstacles)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)

        sensores.draw(screen)

        for i in range(N_FEIXES):
            status = "OK " if sensores.validas[i] else "ERR"
            texto = (f"Feixe {i} ({math.degrees(sensores.angulos[i]):5.1f} graus)  "
                     f"bruto={sensores.brutas[i]:6.1f}  filtrado={sensores.filtradas[i]:6.1f}  [{status}]")
            screen.blit(font.render(texto, True, COR_TEXTO), (20, 20 + i * 18))

        screen.blit(font.render("Mova o mouse para reapontar os feixes (posicao do robo fixa).",
                                 True, (255, 215, 0)), (20, 20 + N_FEIXES * 18 + 10))

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
