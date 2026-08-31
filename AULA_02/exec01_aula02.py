"""
NOME: HENRIQUE RIBEIRO SIQUEIRA e BRUNO MENEZES GOMES
PROF.: FLAVIO SANTARELLI - DATA: 24/08/2026
CURSO: CIÊNCIA DA COMPUTAÇÃO - NOTURNO
"""
########### INTELLIGENT MOBILE ROBOTS - AC1-PT1 ##################


import pygame
import math
import numpy as np

# Constantes de Configuração
LARGURA_TELA = 800
ALTURA_TELA = 600
FPS = 60
COR_FUNDO = (30, 30, 30)
COR_ROBO = (0, 180, 255)
COR_DIRECAO = (255, 50, 50)
COR_TRAJETORIA = (100, 200, 100)

VELOCIDADE_RODA = 150.0  # pixels/s por roda

class DiffDriveRobot:
    def __init__(self, x, y, theta=0.0, wheelbase=30.0, radius=15.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

        self.L = float(wheelbase)
        self.radius = float(radius)

        self.v = 0.0
        self.omega = 0.0

        # Guarda as velocidades individuais das rodas para telemetria
        self.v_left = 0.0
        self.v_right = 0.0

        self.history = []

    def set_wheel_velocities(self, v_left, v_right):
        """Converte velocidade das rodas em velocidade linear e angular."""
        self.v_left = v_left
        self.v_right = v_right
        self.v = (v_right + v_left) / 2.0
        self.omega = (v_right - v_left) / self.L

    def set_direct_velocity(self, v, omega):
        """Comando direto de velocidade linear e angular (padrão cmd_vel)."""
        self.v = v
        self.omega = omega

    def update(self, dt):
        self.theta += self.omega * dt
        self.theta = (self.theta + math.pi) % (2 * math.pi) - math.pi

        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt

        if len(self.history) == 0 or np.hypot(self.x - self.history[-1][0], self.y - self.history[-1][1]) > 5:
            self.history.append((self.x, self.y))
            if len(self.history) > 500:
                self.history.pop(0)

    def draw(self, surface):
        if len(self.history) > 1:
            pygame.draw.lines(surface, COR_TRAJETORIA, False, self.history, 2)

        pos_int = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos_int, int(self.radius))

        linha_frente_x = self.x + (self.radius + 10) * math.cos(self.theta)
        linha_frente_y = self.y + (self.radius + 10) * math.sin(self.theta)
        pygame.draw.line(surface, COR_DIRECAO, pos_int, (int(linha_frente_x), int(linha_frente_y)), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Aula 01: Fundamentos de Robótica Móvel")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    robot = DiffDriveRobot(x=LARGURA_TELA // 2, y=ALTURA_TELA // 2, theta=0.0)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Leitura do teclado para controle independente de cada roda
        keys = pygame.key.get_pressed()
        v_esq = 0.0  # velocidade da roda esquerda (W/S)
        v_dir = 0.0  # velocidade da roda direita (I/K)

        if keys[pygame.K_w]:
            v_esq += VELOCIDADE_RODA
        if keys[pygame.K_s]:
            v_esq -= VELOCIDADE_RODA
        if keys[pygame.K_i]:
            v_dir += VELOCIDADE_RODA
        if keys[pygame.K_k]:
            v_dir -= VELOCIDADE_RODA

        # Aplica comando via cinemática das rodas
        robot.set_wheel_velocities(v_esq, v_dir)
        robot.update(dt)

        # Renderização
        screen.fill(COR_FUNDO)
        robot.draw(screen)

        # Painel de Telemetria
        info_txt = [
            f"Pose X: {robot.x:.1f} px | Y: {robot.y:.1f} px | Theta: {math.degrees(robot.theta):.1f} deg",
            f"Rodas: v_esq = {robot.v_left:.1f} px/s | v_dir = {robot.v_right:.1f} px/s",
            f"Resultante: v = {robot.v:.1f} px/s | omega = {robot.omega:.2f} rad/s",
            "Controles: W/S = roda esquerda | I/K = roda direita"
        ]
        for i, txt in enumerate(info_txt):
            rendered = font.render(txt, True, (220, 220, 220))
            screen.blit(rendered, (15, 15 + i * 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
