"""
Lab 3 - Percepcao com 5 feixes + ruido gaussiano
NOME: BRUNO MENEZES GOMES / HENRIQUE RIBEIRO SIQUEIRA
PROF.: FLAVIO SANTARELLI - DATA: 31/08/26
CURSO: CIENCIA DA COMPUTACAO - NOTURNO
"""

import pygame
import math
import numpy as np

LARGURA, ALTURA = 900, 650
FPS = 60
COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_OBSTACULO = (180, 50, 50)
COR_RAIO_LIVRE = (0, 255, 100)
COR_RAIO_COLISAO = (255, 200, 0)

SENSOR_ANGLES = [math.radians(a) for a in (-60, -30, 0, 30, 60)]  # 5 feixes
SENSOR_RANGE = 200.0
RUIDO_MU, RUIDO_SIGMA = 0.0, 2.0
RAIO_CORPO = 16.0


class SensingRobot:
    def __init__(self, x, y, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        self.readings = [SENSOR_RANGE] * len(SENSOR_ANGLES)
        self.hit_points = [(0, 0)] * len(SENSOR_ANGLES)

    def _colide(self, nx, ny, obstacles):
        """True se corpo (circulo raio RAIO_CORPO) intersecta obstaculo/borda."""
        if nx - RAIO_CORPO <= 0 or nx + RAIO_CORPO >= LARGURA:
            return True
        if ny - RAIO_CORPO <= 0 or ny + RAIO_CORPO >= ALTURA:
            return True
        for obs in obstacles:
            # ponto mais proximo do retangulo ao centro do robo
            cx = max(obs.left, min(nx, obs.right))
            cy = max(obs.top, min(ny, obs.bottom))
            if (nx - cx) ** 2 + (ny - cy) ** 2 < RAIO_CORPO ** 2:
                return True
        return False

    def mover_para(self, alvo_x, alvo_y, ganho, obstacles):
        """Move suavemente rumo ao alvo com colisao (slide por eixo)."""
        dx = (alvo_x - self.x) * ganho
        dy = (alvo_y - self.y) * ganho
        # tenta X primeiro
        if not self._colide(self.x + dx, self.y, obstacles):
            self.x += dx
        # depois Y (permite slide ao longo de parede)
        if not self._colide(self.x, self.y + dy, obstacles):
            self.y += dy

    def cast_rays(self, obstacles):
        self.readings = []
        self.hit_points = []
        for beta in SENSOR_ANGLES:
            angle = self.theta + beta
            dist_real = SENSOR_RANGE
            hit_x = self.x + SENSOR_RANGE * math.cos(angle)
            hit_y = self.y + SENSOR_RANGE * math.sin(angle)
            for step in range(3, int(SENSOR_RANGE), 3):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    dist_real = float(step)
                    hit_x, hit_y = rx, ry
                    break
                colidiu = False
                for obs in obstacles:
                    if obs.collidepoint(rx, ry):
                        dist_real = float(step)
                        hit_x, hit_y = rx, ry
                        colidiu = True
                        break
                if colidiu:
                    break
            # ruido gaussiano por leitura (conforme docx)
            dist_ruido = dist_real + np.random.normal(RUIDO_MU, RUIDO_SIGMA)
            dist_ruido = max(0.0, min(SENSOR_RANGE, dist_ruido))
            self.readings.append(dist_ruido)
            self.hit_points.append((hit_x, hit_y))

    def draw(self, surface, font):
        for i, beta in enumerate(SENSOR_ANGLES):
            dist = self.readings[i]
            hit = self.hit_points[i]
            cor = COR_RAIO_COLISAO if dist < SENSOR_RANGE - 1 else COR_RAIO_LIVRE
            pygame.draw.line(surface, cor,
                             (int(self.x), int(self.y)),
                             (int(hit[0]), int(hit[1])), 2)
            pygame.draw.circle(surface, cor, (int(hit[0]), int(hit[1])), 4)
            # valor renderizado ao lado do raio
            tx = int(self.x + (dist * 0.6) * math.cos(self.theta + beta))
            ty = int(self.y + (dist * 0.6) * math.sin(self.theta + beta))
            label = font.render(f"{dist:5.1f}", True, (255, 255, 255))
            surface.blit(label, (tx + 4, ty - 8))

        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, int(RAIO_CORPO))
        fx = self.x + (RAIO_CORPO + 8) * math.cos(self.theta)
        fy = self.y + (RAIO_CORPO + 8) * math.sin(self.theta)
        pygame.draw.line(surface, (255, 50, 50), pos, (int(fx), int(fy)), 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 3 - 5 feixes + ruido gaussiano")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 12)

    robot = SensingRobot(200, 320, 0.0)
    obstacles = [
        pygame.Rect(400, 100, 90, 300),
        pygame.Rect(400, 450, 90, 150),
        pygame.Rect(650, 200, 180, 220),
    ]

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - robot.x, my - robot.y
        robot.theta = math.atan2(dy, dx)
        robot.mover_para(mx, my, 0.03, obstacles)

        robot.cast_rays(obstacles)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)
        robot.draw(screen, font)

        titulo = font.render(
            "5 sensores nos angulos -60/-30/0/+30/+60 graus | alcance 200 px | ruido N(0, 2.0)",
            True, (255, 215, 0))
        screen.blit(titulo, (15, 15))
        for i, dist in enumerate(robot.readings):
            ang_deg = math.degrees(SENSOR_ANGLES[i])
            txt = font.render(f"beta={ang_deg:+5.0f} deg  d = {dist:6.2f} px", True, (220, 220, 220))
            screen.blit(txt, (15, 40 + i * 18))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
