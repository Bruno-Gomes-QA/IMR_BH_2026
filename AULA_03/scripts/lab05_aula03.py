"""
Lab 5 - Go-to-goal + desvio reativo
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
COR_ALVO = (255, 220, 0)

SENSOR_ANGLES = [math.radians(a) for a in (-60, -30, 0, 30, 60)]
SENSOR_RANGE = 200.0

KP_V = 1.5
KP_OMEGA = 4.0
V_MAX = 120.0
OMEGA_MAX = 3.0
DIST_TOLERANCIA = 15.0    # docx: parar a menos de 15 px
D_SEG = 60.0              # docx: qualquer sensor < 60 -> desvio
K_ATR = 1.0               # peso do vetor atrativo
K_REP = 2.5               # peso do vetor repulsivo (por sensor ativo)
V_MIN_DESVIO = 25.0       # piso de velocidade linear no modo desvio (evita travar)


def normalizar_angulo(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class DiffDriveRobot:
    def __init__(self, x, y, theta=0.0, wheelbase=30.0, radius=15.0):
        self.x = float(x); self.y = float(y); self.theta = float(theta)
        self.L = float(wheelbase); self.radius = float(radius)
        self.v = 0.0; self.omega = 0.0
        self.history = []
        self.readings = [SENSOR_RANGE] * len(SENSOR_ANGLES)
        self.hit_points = [(0, 0)] * len(SENSOR_ANGLES)

    def set_direct_velocity(self, v, omega):
        self.v = v; self.omega = omega

    def cast_rays(self, obstacles):
        self.readings = []; self.hit_points = []
        for beta in SENSOR_ANGLES:
            angle = self.theta + beta
            dist_real = SENSOR_RANGE
            hit_x = self.x + SENSOR_RANGE * math.cos(angle)
            hit_y = self.y + SENSOR_RANGE * math.sin(angle)
            for step in range(3, int(SENSOR_RANGE), 3):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    dist_real = float(step); hit_x, hit_y = rx, ry; break
                colidiu = False
                for obs in obstacles:
                    if obs.collidepoint(rx, ry):
                        dist_real = float(step); hit_x, hit_y = rx, ry
                        colidiu = True; break
                if colidiu: break
            self.readings.append(dist_real)
            self.hit_points.append((hit_x, hit_y))

    def update(self, dt):
        self.theta = normalizar_angulo(self.theta + self.omega * dt)
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        if not self.history or np.hypot(self.x - self.history[-1][0], self.y - self.history[-1][1]) > 4:
            self.history.append((self.x, self.y))
            if len(self.history) > 800: self.history.pop(0)

    def draw(self, surface):
        if len(self.history) > 1:
            pygame.draw.lines(surface, COR_TRAJETORIA, False, self.history, 2)
        for i, beta in enumerate(SENSOR_ANGLES):
            d = self.readings[i]; hit = self.hit_points[i]
            cor = COR_RAIO_COLISAO if d < SENSOR_RANGE - 1 else COR_RAIO_LIVRE
            pygame.draw.line(surface, cor,
                             (int(self.x), int(self.y)),
                             (int(hit[0]), int(hit[1])), 1)
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, int(self.radius))
        fx = self.x + (self.radius + 10) * math.cos(self.theta)
        fy = self.y + (self.radius + 10) * math.sin(self.theta)
        pygame.draw.line(surface, (255, 50, 50), pos, (int(fx), int(fy)), 3)


def controlar(robot, alvo):
    """
    Campo potencial vetorial:
      F_atr = unit(alvo - pose) * K_ATR
      F_rep = soma_i [ -unit(raio_i) * peso_i * K_REP ]   com peso_i = (D_SEG - d_i)/D_SEG
      theta_desejado = atan2(F_atr + F_rep)
      omega = KP_OMEGA * erro_theta
      v     = KP_V * dist * cos(erro_theta)  (atracao)
              max(V_MIN_DESVIO, V_MAX * 0.5 * cos(erro_theta))  (desvio)

    Vantagem sobre soma escalar: sensor central (beta=0) contribui como vetor
    apontando para tras, sem viezes arbitrarios de sinal. Piso V_MIN_DESVIO
    impede que o robo congele girando em zero enquanto contorna obstaculo.
    """
    dx = alvo[0] - robot.x
    dy = alvo[1] - robot.y
    dist = math.hypot(dx, dy)

    # Componente atrativa (vetor unitario * peso)
    if dist > 1e-6:
        F_atr_x = (dx / dist) * K_ATR
        F_atr_y = (dy / dist) * K_ATR
    else:
        F_atr_x = F_atr_y = 0.0

    # Componente repulsiva por sensor ativo
    F_rep_x = 0.0
    F_rep_y = 0.0
    modo = "ATRACAO"
    for beta, d in zip(SENSOR_ANGLES, robot.readings):
        if d < D_SEG:
            modo = "DESVIO"
            peso = (D_SEG - d) / D_SEG   # 1 quando encosta, 0 na fronteira
            ang_global = robot.theta + beta
            # vetor repulsivo: sentido contrario ao raio do sensor
            F_rep_x -= math.cos(ang_global) * peso * K_REP
            F_rep_y -= math.sin(ang_global) * peso * K_REP

    # Comando resultante
    Fx = F_atr_x + F_rep_x
    Fy = F_atr_y + F_rep_y
    theta_desejado = math.atan2(Fy, Fx)
    erro_theta = normalizar_angulo(theta_desejado - robot.theta)

    omega_cmd = KP_OMEGA * erro_theta

    if modo == "DESVIO":
        # velocidade proporcional a cos(erro), mas com piso pra nao travar
        v_cmd = V_MAX * 0.5 * max(0.0, math.cos(erro_theta))
        v_cmd = max(V_MIN_DESVIO, v_cmd)
    else:
        v_cmd = KP_V * dist * max(0.0, math.cos(erro_theta))

    v_cmd = max(-V_MAX, min(V_MAX, v_cmd))
    omega_cmd = max(-OMEGA_MAX, min(OMEGA_MAX, omega_cmd))
    robot.set_direct_velocity(v_cmd, omega_cmd)
    return dist, modo


def desenhar_alvo(surface, alvo):
    if alvo is None: return
    x, y = alvo; t = 8
    pygame.draw.line(surface, COR_ALVO, (x - t, y - t), (x + t, y + t), 3)
    pygame.draw.line(surface, COR_ALVO, (x - t, y + t), (x + t, y - t), 3)
    pygame.draw.circle(surface, COR_ALVO, (x, y), t + 4, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 5 - Go-to-goal + desvio reativo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13)

    robot = DiffDriveRobot(120, 120, theta=0.0)
    obstacles = [
        pygame.Rect(350, 200, 90, 250),
        pygame.Rect(550, 100, 50, 200),
        pygame.Rect(600, 400, 200, 40),
        pygame.Rect(250, 500, 200, 40),
    ]
    alvo = None
    dist_atual = 0.0
    modo = "-"

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                alvo = event.pos

        robot.cast_rays(obstacles)

        if alvo is not None:
            dist_atual, modo = controlar(robot, alvo)
            if dist_atual < DIST_TOLERANCIA:
                robot.set_direct_velocity(0.0, 0.0)
                alvo = None
                modo = "CHEGOU"
        else:
            robot.set_direct_velocity(0.0, 0.0)

        robot.update(dt)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)
        desenhar_alvo(screen, alvo)
        robot.draw(screen)

        info = [
            f"Modo: {modo}   D_SEG = {D_SEG:.0f}   tol_alvo = {DIST_TOLERANCIA:.0f}",
            f"Alvo: {alvo}   dist = {dist_atual:6.1f} px",
            f"leituras: " + " ".join(f"{d:5.1f}" for d in robot.readings),
            "Clique esquerdo define alvo",
        ]
        for i, t in enumerate(info):
            screen.blit(font.render(t, True, (230, 230, 230)), (15, 15 + i * 18))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
