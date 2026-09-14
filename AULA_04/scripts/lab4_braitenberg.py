"""
Lab 4 - Braitenberg com Conexoes Diretas (Comportamento de Agressao/Atracao)
NOME: BRUNO MENEZES GOMES / HENRIQUE RIBEIRO SIQUEIRA
PROF.: FLAVIO SANTARELLI - DATA: 14/09/26
CURSO: CIENCIA DA COMPUTACAO - NOTURNO
"""

import math
import pygame

LARGURA, ALTURA = 900, 650
FPS = 60

V0 = 40.0       # velocidade base das rodas (px/s)
ALPHA = 120.0   # ganho de excitacao
D_MAX = 220.0   # alcance do sensor (px)
WHEEL_BASE = 30.0

SENSOR_ANGULOS = [-math.pi / 6, math.pi / 6]  # esquerdo, direito

COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_OBSTACULO = (180, 50, 50)
COR_RAIO = (255, 200, 0)
COR_TEXTO = (220, 220, 220)


class RoboBraitenberg:
    def __init__(self, x, y, theta):
        self.x, self.y, self.theta = x, y, theta
        self.d_esq = D_MAX
        self.d_dir = D_MAX
        self.vL = V0
        self.vR = V0

    def sensear(self, obstacles):
        distancias = []
        for beta in SENSOR_ANGULOS:
            angle = self.theta + beta
            d = D_MAX
            for step in range(2, int(D_MAX), 2):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    d = float(step)
                    break
                if any(obs.collidepoint(rx, ry) for obs in obstacles):
                    d = float(step)
                    break
            distancias.append(d)
        self.d_esq, self.d_dir = distancias

    def controlar(self):
        # Conexoes diretas (nao-cruzadas): sensor esq -> roda esq, sensor dir -> roda dir
        self.vL = V0 + ALPHA * (1.0 - self.d_esq / D_MAX)
        self.vR = V0 + ALPHA * (1.0 - self.d_dir / D_MAX)

    def mover(self, dt):
        v = (self.vL + self.vR) / 2.0
        w = (self.vR - self.vL) / WHEEL_BASE
        self.theta += w * dt
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt

    def draw(self, surface):
        for beta, d, ativo in ((SENSOR_ANGULOS[0], self.d_esq, self.d_esq < D_MAX),
                                (SENSOR_ANGULOS[1], self.d_dir, self.d_dir < D_MAX)):
            angle = self.theta + beta
            fx = self.x + d * math.cos(angle)
            fy = self.y + d * math.sin(angle)
            cor = COR_RAIO if ativo else (0, 255, 100)
            pygame.draw.line(surface, cor, (int(self.x), int(self.y)), (int(fx), int(fy)), 2)
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, 14)
        fx = self.x + 24 * math.cos(self.theta)
        fy = self.y + 24 * math.sin(self.theta)
        pygame.draw.line(surface, (255, 50, 50), pos, (int(fx), int(fy)), 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 4 - Braitenberg Conexoes Diretas (Agressao)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    robo = RoboBraitenberg(150, 480, -math.pi / 8)
    obstacles = [pygame.Rect(650, 200, 100, 100)]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        robo.sensear(obstacles)
        robo.controlar()
        robo.mover(dt)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)

        robo.draw(screen)

        linhas = [
            f"d_esq={robo.d_esq:6.1f} px   d_dir={robo.d_dir:6.1f} px",
            f"vL={robo.vL:6.1f}   vR={robo.vR:6.1f}",
            "Conexao direta (esq->esq, dir->dir): roda do lado que ve o obstaculo acelera -> ROBO VIRA PARA O OBSTACULO.",
        ]
        for i, l in enumerate(linhas):
            screen.blit(font.render(l, True, COR_TEXTO), (20, 20 + i * 20))

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
