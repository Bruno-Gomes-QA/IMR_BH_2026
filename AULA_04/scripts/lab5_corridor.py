"""
Exercicio 5 - Centralizacao Autonoma em Corredor (Controle Proporcional)
NOME: BRUNO MENEZES GOMES / HENRIQUE RIBEIRO SIQUEIRA
PROF.: FLAVIO SANTARELLI - DATA: 14/09/26
CURSO: CIENCIA DA COMPUTACAO - NOTURNO
"""

import math
import pygame

LARGURA, ALTURA = 900, 650
FPS = 60

V = 40.0        # velocidade linear constante (px/s)
KP = 0.01       # ganho proporcional
ALCANCE_MAX = 300.0

PAREDE_TOPO = pygame.Rect(0, 150, LARGURA, 20)
PAREDE_BASE = pygame.Rect(0, 480, LARGURA, 20)

COR_FUNDO = (20, 24, 30)
COR_PAREDE = (120, 120, 130)
COR_ROBO = (0, 200, 255)
COR_RAIO = (0, 255, 100)
COR_TRAJETO = (255, 200, 0)
COR_TEXTO = (220, 220, 220)


def raycast(x, y, angle, paredes):
    for step in range(1, int(ALCANCE_MAX), 2):
        rx = x + step * math.cos(angle)
        ry = y + step * math.sin(angle)
        if ry <= 0 or ry >= ALTURA or rx <= 0 or rx >= LARGURA:
            return float(step), (rx, ry)
        for parede in paredes:
            if parede.collidepoint(rx, ry):
                return float(step), (rx, ry)
    return ALCANCE_MAX, (x + ALCANCE_MAX * math.cos(angle), y + ALCANCE_MAX * math.sin(angle))


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("EX5 - Centralizacao em Corredor")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    paredes = [PAREDE_TOPO, PAREDE_BASE]

    # Robo inicia desalinhado (mais perto da parede de cima) para provar a correcao
    x, y, theta = 50.0, 230.0, 0.0
    trajeto = [(int(x), int(y))]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ang_esq = theta - math.pi / 2
        ang_dir = theta + math.pi / 2
        d_esq, ponto_esq = raycast(x, y, ang_esq, paredes)
        d_dir, ponto_dir = raycast(x, y, ang_dir, paredes)

        # No Pygame o y cresce para baixo (theta positivo gira o robo para o
        # lado "direito"/baixo). Por isso o erro usado no controle e
        # d_dir - d_esq: se a parede esquerda esta perto (d_esq pequeno) o
        # robo precisa de w positivo para se afastar dela.
        erro = d_dir - d_esq
        w = max(-1.5, min(1.5, KP * erro))  # clamp evita giro violento perto da parede

        theta += w * dt
        x += V * math.cos(theta) * dt
        y += V * math.sin(theta) * dt

        if x > LARGURA - 40:
            x = 40.0  # relanca no inicio do corredor para demo continua

        trajeto.append((int(x), int(y)))
        if len(trajeto) > 2000:
            trajeto.pop(0)

        screen.fill(COR_FUNDO)
        for parede in paredes:
            pygame.draw.rect(screen, COR_PAREDE, parede)

        if len(trajeto) > 1:
            pygame.draw.lines(screen, COR_TRAJETO, False, trajeto, 2)

        pygame.draw.line(screen, COR_RAIO, (int(x), int(y)), (int(ponto_esq[0]), int(ponto_esq[1])), 1)
        pygame.draw.line(screen, COR_RAIO, (int(x), int(y)), (int(ponto_dir[0]), int(ponto_dir[1])), 1)
        pygame.draw.circle(screen, COR_ROBO, (int(x), int(y)), 10)
        fx = x + 20 * math.cos(theta)
        fy = y + 20 * math.sin(theta)
        pygame.draw.line(screen, (255, 50, 50), (int(x), int(y)), (int(fx), int(fy)), 3)

        linhas = [
            f"d_esq={d_esq:6.1f} px   d_dir={d_dir:6.1f} px   erro={erro:7.2f}",
            f"w={w:.4f} rad/s   theta={math.degrees(theta):5.1f} graus",
        ]
        for i, l in enumerate(linhas):
            screen.blit(font.render(l, True, COR_TEXTO), (20, 20 + i * 20))

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
