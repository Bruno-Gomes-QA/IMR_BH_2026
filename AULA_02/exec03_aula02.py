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
COR_ALVO = (255, 220, 0)

# Parâmetros do controlador proporcional
KP_OMEGA = 4.0        # Ganho proporcional angular
KP_V = 1.5            # Ganho proporcional linear
V_MAX = 120.0          # Velocidade linear máxima (px/s)
OMEGA_MAX = 3.0        # Velocidade angular máxima (rad/s)
DIST_TOLERANCIA = 8.0  # Distância mínima para considerar o alvo alcançado (px)


def normalizar_angulo(angulo):
    """Normaliza um ângulo para o intervalo [-pi, pi]."""
    return (angulo + math.pi) % (2 * math.pi) - math.pi


class DiffDriveRobot:
    def __init__(self, x, y, theta=0.0, wheelbase=30.0, radius=15.0):
        # Estado do robô: [x, y, theta]
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)  # em radianos

        # Parâmetros físicos (em pixels)
        self.L = float(wheelbase)  # Distância entre rodas
        self.radius = float(radius)

        # Entradas de controle
        self.v = 0.0      # Velocidade linear (pixels/s)
        self.omega = 0.0  # Velocidade angular (rad/s)

        # Histórico de posições para plotar rastro
        self.history = []

    def set_wheel_velocities(self, v_left, v_right):
        """Converte velocidade das rodas em velocidade linear e angular."""
        self.v = (v_right + v_left) / 2.0
        self.omega = (v_right - v_left) / self.L

    def set_direct_velocity(self, v, omega):
        """Comando direto de velocidade linear e angular (padrão cmd_vel)."""
        self.v = v
        self.omega = omega

    def controlar_para_alvo(self, alvo_x, alvo_y):
        """
        Controlador proporcional simples que gera (v, omega) para levar
        o robô até o ponto (alvo_x, alvo_y).

        Retorna a distância atual até o alvo, para que o chamador possa
        decidir quando parar.
        """
        dx = alvo_x - self.x
        dy = alvo_y - self.y
        distancia = math.hypot(dx, dy)

        # Ângulo desejado (em direção ao alvo) e erro angular
        theta_desejado = math.atan2(dy, dx)
        erro_theta = normalizar_angulo(theta_desejado - self.theta)

        # Lei de controle proporcional
        omega_cmd = KP_OMEGA * erro_theta
        v_cmd = KP_V * distancia

        # Reduz a velocidade linear quando o erro angular é grande,
        # para o robô girar no lugar antes de avançar
        fator_alinhamento = max(0.0, math.cos(erro_theta))
        v_cmd *= fator_alinhamento

        # Satura os comandos nos limites físicos
        v_cmd = max(-V_MAX, min(V_MAX, v_cmd))
        omega_cmd = max(-OMEGA_MAX, min(OMEGA_MAX, omega_cmd))

        self.set_direct_velocity(v_cmd, omega_cmd)
        return distancia

    def update(self, dt):
        """Integração numérica da cinemática diferencial."""
        # Atualização angular
        self.theta += self.omega * dt
        # Normaliza o ângulo entre [-pi, pi]
        self.theta = normalizar_angulo(self.theta)

        # Atualização de posição cartesiana
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt

        # Guarda histórico para desenhar o rastro
        if len(self.history) == 0 or np.hypot(self.x - self.history[-1][0], self.y - self.history[-1][1]) > 5:
            self.history.append((self.x, self.y))
            if len(self.history) > 500:
                self.history.pop(0)

    def draw(self, surface):
        # 1. Desenha o rastro
        if len(self.history) > 1:
            pygame.draw.lines(surface, COR_TRAJETORIA, False, self.history, 2)

        # 2. Desenha o corpo do robô
        pos_int = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos_int, int(self.radius))

        # 3. Desenha a linha indicadora da direção (orientação theta)
        linha_frente_x = self.x + (self.radius + 10) * math.cos(self.theta)
        linha_frente_y = self.y + (self.radius + 10) * math.sin(self.theta)
        pygame.draw.line(surface, COR_DIRECAO, pos_int, (int(linha_frente_x), int(linha_frente_y)), 3)


def desenhar_alvo(surface, alvo):
    """Desenha um marcador em forma de X na posição do alvo."""
    if alvo is None:
        return
    x, y = alvo
    tam = 8
    pygame.draw.line(surface, COR_ALVO, (x - tam, y - tam), (x + tam, y + tam), 3)
    pygame.draw.line(surface, COR_ALVO, (x - tam, y + tam), (x + tam, y - tam), 3)
    pygame.draw.circle(surface, COR_ALVO, (x, y), tam + 4, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Aula 01: Fundamentos de Robótica Móvel")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    robot = DiffDriveRobot(x=LARGURA_TELA // 2, y=ALTURA_TELA // 2, theta=0.0)

    # Alvo clicado pelo usuário (None enquanto não houver alvo ativo)
    alvo = None
    distancia_atual = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time em segundos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clique com o botão esquerdo define um novo alvo
                alvo = event.pos

        if alvo is not None:
            # Modo autônomo: controlador proporcional guia o robô até o alvo
            distancia_atual = robot.controlar_para_alvo(alvo[0], alvo[1])

            if distancia_atual < DIST_TOLERANCIA:
                # Chegou perto o suficiente: para o robô e limpa o alvo
                robot.set_direct_velocity(0.0, 0.0)
                alvo = None
        else:
            # Modo manual: leitura do teclado para controle direto
            keys = pygame.key.get_pressed()
            v_cmd = 0.0
            omega_cmd = 0.0

            if keys[pygame.K_UP]:
                v_cmd += 120.0     # 120 pixels/s para frente
            if keys[pygame.K_DOWN]:
                v_cmd -= 80.0      # 80 pixels/s para trás
            if keys[pygame.K_LEFT]:
                omega_cmd -= 2.5   # 2.5 rad/s anti-horário
            if keys[pygame.K_RIGHT]:
                omega_cmd += 2.5   # 2.5 rad/s horário

            robot.set_direct_velocity(v_cmd, omega_cmd)

        # Atualiza física do robô
        robot.update(dt)

        # Renderização
        screen.fill(COR_FUNDO)
        desenhar_alvo(screen, alvo)
        robot.draw(screen)

        # Painel de Telemetria
        info_txt = [
            f"Pose X: {robot.x:.1f} px | Y: {robot.y:.1f} px | Theta: {math.degrees(robot.theta):.1f} deg",
            f"Comandos: v = {robot.v:.1f} px/s | omega = {robot.omega:.2f} rad/s",
            f"Alvo: {'Ativo, dist=' + format(distancia_atual, '.1f') + ' px' if alvo else 'Nenhum (clique para definir)'}",
            "Controles: Clique esquerdo define alvo | Setas: controle manual (sem alvo ativo)",
        ]
        for i, txt in enumerate(info_txt):
            rendered = font.render(txt, True, (220, 220, 220))
            screen.blit(rendered, (15, 15 + i * 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
