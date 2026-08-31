"""
Lab 4 - Braitenberg (medo puro)
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
COR_TRAJETORIA = (100, 200, 100)

SENSOR_ANGLES = [math.radians(a) for a in (-60, -30, 0, 30, 60)]
SENSOR_RANGE = 200.0

V_BASE = 100.0           # velocidade base de cruzeiro (docx)
KS = 1.5                 # ganho Braitenberg
THRESHOLD_CENTRAL = 40.0 # docx: sensor central < 40 -> giro imediato


class DiffDriveRobot:
    def __init__(self, x, y, theta=0.0, wheelbase=30.0, radius=15.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        self.L = float(wheelbase)
        self.radius = float(radius)
        self.v = 0.0
        self.omega = 0.0
        self.v_left = 0.0
        self.v_right = 0.0
        self.history = []
        self.readings = [SENSOR_RANGE] * len(SENSOR_ANGLES)
        self.hit_points = [(0, 0)] * len(SENSOR_ANGLES)

    def set_wheel_velocities(self, v_left, v_right):
        self.v_left = v_left
        self.v_right = v_right
        self.v = (v_right + v_left) / 2.0
        self.omega = (v_right - v_left) / self.L

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
                    dist_real = float(step); hit_x, hit_y = rx, ry
                    break
                colidiu = False
                for obs in obstacles:
                    if obs.collidepoint(rx, ry):
                        dist_real = float(step); hit_x, hit_y = rx, ry
                        colidiu = True
                        break
                if colidiu: break
            self.readings.append(dist_real)
            self.hit_points.append((hit_x, hit_y))

    def update(self, dt):
        self.theta += self.omega * dt
        self.theta = (self.theta + math.pi) % (2 * math.pi) - math.pi
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        if not self.history or np.hypot(self.x - self.history[-1][0], self.y - self.history[-1][1]) > 4:
            self.history.append((self.x, self.y))
            if len(self.history) > 800:
                self.history.pop(0)

    def draw(self, surface):
        if len(self.history) > 1:
            pygame.draw.lines(surface, COR_TRAJETORIA, False, self.history, 2)
        for i, beta in enumerate(SENSOR_ANGLES):
            d = self.readings[i]
            hit = self.hit_points[i]
            cor = COR_RAIO_COLISAO if d < SENSOR_RANGE - 1 else COR_RAIO_LIVRE
            pygame.draw.line(surface, cor,
                             (int(self.x), int(self.y)),
                             (int(hit[0]), int(hit[1])), 1)
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, int(self.radius))
        fx = self.x + (self.radius + 10) * math.cos(self.theta)
        fy = self.y + (self.radius + 10) * math.sin(self.theta)
        pygame.draw.line(surface, (255, 50, 50), pos, (int(fx), int(fy)), 3)


def braitenberg_control(robot):
    """
    Lei de medo puro (Braitenberg vehicle 3a):
      - sensores da direita  -> aceleram roda esquerda  (vira para longe da direita)
      - sensores da esquerda -> aceleram roda direita   (vira para longe da esquerda)
    Excitacao = (S_max - d)/S_max em [0..1].
    Se sensor central < THRESHOLD_CENTRAL -> giro no proprio eixo.
    """
    d_left1, d_left2, d_center, d_right2, d_right1 = robot.readings
    # excitacoes (perto = 1, longe = 0)
    e_L = ((SENSOR_RANGE - d_left1) + (SENSOR_RANGE - d_left2)) / (2 * SENSOR_RANGE)
    e_R = ((SENSOR_RANGE - d_right1) + (SENSOR_RANGE - d_right2)) / (2 * SENSOR_RANGE)

    # obstaculo perto na esquerda -> acelera roda direita; e vice-versa
    v_left  = V_BASE + KS * V_BASE * e_R
    v_right = V_BASE + KS * V_BASE * e_L

    if d_center < THRESHOLD_CENTRAL:
        # giro emergencial: inverte uma das rodas
        if e_L >= e_R:
            v_left, v_right = V_BASE, -V_BASE
        else:
            v_left, v_right = -V_BASE, V_BASE

    robot.set_wheel_velocities(v_left, v_right)


def sala_fechada():
    """Sala com paredes externas (bordas da tela) + 5 obstaculos internos."""
    return [
        pygame.Rect(200, 100, 120, 40),
        pygame.Rect(500, 220, 40, 260),
        pygame.Rect(700, 100, 40, 200),
        pygame.Rect(200, 450, 260, 40),
        pygame.Rect(650, 480, 200, 40),
    ]


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 4 - Braitenberg 'medo puro'")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13)

    robot = DiffDriveRobot(120, 120, theta=0.3)
    obstacles = sala_fechada()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                robot = DiffDriveRobot(120, 120, theta=0.3)

        robot.cast_rays(obstacles)
        braitenberg_control(robot)
        robot.update(dt)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)
        robot.draw(screen)

        info = [
            f"v_base = {V_BASE:.0f}  Ks = {KS:.2f}  central_thr = {THRESHOLD_CENTRAL:.0f} px",
            f"leituras: " + " ".join(f"{d:5.1f}" for d in robot.readings),
            f"rodas: vL = {robot.v_left:6.1f}  vR = {robot.v_right:6.1f}",
            "R = reinicia posicao inicial",
        ]
        for i, t in enumerate(info):
            screen.blit(font.render(t, True, (230, 230, 230)), (15, 15 + i * 18))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
