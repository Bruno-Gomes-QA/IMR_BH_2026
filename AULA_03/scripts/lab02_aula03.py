"""
Lab 2 - Rotacao In-Place 90 graus
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
COR_DIRECAO = (255, 50, 50)
COR_TRAJETORIA = (100, 200, 100)
COR_ESTADO = (255, 220, 100)

# Especificacao do docx AULA_03 - Lab 2
ANGULO_ALVO = math.pi / 2   # 90 graus
OMEGA_CMD   = 0.5           # rad/s (anti-horario)
TEMPO_TEORICO = ANGULO_ALVO / OMEGA_CMD   # ~ pi segundos


class DiffDriveRobot:
    def __init__(self, x, y, theta=0.0, wheelbase=30.0, radius=15.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        self.L = float(wheelbase)
        self.radius = float(radius)
        self.v = 0.0
        self.omega = 0.0

    def set_direct_velocity(self, v, omega):
        """Emula publicacao no topico /cmd_vel."""
        self.v = v
        self.omega = omega

    def update(self, dt):
        self.theta += self.omega * dt
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, int(self.radius))
        fx = self.x + (self.radius + 10) * math.cos(self.theta)
        fy = self.y + (self.radius + 10) * math.sin(self.theta)
        pygame.draw.line(surface, COR_DIRECAO, pos, (int(fx), int(fy)), 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 2 - Rotacao In-Place 90 graus")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    robot = DiffDriveRobot(LARGURA // 2, ALTURA // 2, theta=0.0)
    theta_inicial = robot.theta
    tempo_acumulado = 0.0
    concluido = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Controle open-loop: publica omega no /cmd_vel ate atingir alvo
        if not concluido:
            delta = robot.theta - theta_inicial
            if delta < ANGULO_ALVO:
                robot.set_direct_velocity(0.0, OMEGA_CMD)
                tempo_acumulado += dt
            else:
                robot.set_direct_velocity(0.0, 0.0)   # zera cmd_vel ao concluir
                concluido = True
        else:
            robot.set_direct_velocity(0.0, 0.0)

        robot.update(dt)

        screen.fill(COR_FUNDO)
        # marca eixo fixo (pose x,y deve nao mudar)
        pygame.draw.circle(screen, (60, 60, 60),
                           (LARGURA // 2, ALTURA // 2), 4, 1)
        robot.draw(screen)

        delta_deg = math.degrees(robot.theta - theta_inicial)
        info = [
            f"omega_cmd = {OMEGA_CMD:.2f} rad/s | alvo = 90 deg (pi/2 rad)",
            f"Tempo teorico = pi/omega = {TEMPO_TEORICO:.3f} s",
            f"Tempo real acumulado = {tempo_acumulado:.3f} s",
            f"delta_theta atual = {delta_deg:6.2f} deg",
            f"pose: x={robot.x:.1f} y={robot.y:.1f} (deve ficar fixa)",
            "Estado: CONCLUIDO" if concluido else "Estado: GIRANDO",
        ]
        for i, txt in enumerate(info):
            cor = COR_ESTADO if txt.startswith("Estado") else (220, 220, 220)
            screen.blit(font.render(txt, True, cor), (15, 15 + i * 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
