"""
Lab 2 - Calculadora de Giro Ackermann vs. Diferencial
NOME: BRUNO MENEZES GOMES / HENRIQUE RIBEIRO SIQUEIRA
PROF.: FLAVIO SANTARELLI - DATA: 14/09/26
CURSO: CIENCIA DA COMPUTACAO - NOTURNO
"""

import math
import pygame

LARGURA, ALTURA = 900, 650
FPS = 60
SCALE = 40.0  # px por metro

L = 2.0  # entre-eixos (m) - veiculo Ackermann
PHI_MAX = math.radians(30)
V_STEP = 0.3
PHI_STEP = math.radians(2)

COR_FUNDO = (20, 24, 30)
COR_ACKERMANN = (0, 200, 255)
COR_DIFERENCIAL = (255, 150, 0)
COR_TRAJETO_A = (0, 255, 100)
COR_TRAJETO_D = (255, 200, 0)
COR_TEXTO = (220, 220, 220)


class VeiculoAckermann:
    def __init__(self, x, y, theta):
        self.x, self.y, self.theta = x, y, theta
        self.v = 0.0
        self.phi = 0.0

    def w(self):
        return (self.v / L) * math.tan(self.phi)

    def raio(self):
        if abs(self.phi) < 1e-6:
            return float("inf")
        return L / math.tan(self.phi)

    def step(self, dt):
        w = self.w()
        self.theta += w * dt
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt


class VeiculoDiferencial:
    """Usado apenas como referencia visual: consegue w != 0 com v = 0 (raio zero)."""
    def __init__(self, x, y, theta):
        self.x, self.y, self.theta = x, y, theta
        self.v = 0.0
        self.w = 0.0

    def step(self, dt):
        self.theta += self.w * dt
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt


def to_screen(x, y, ox, oy):
    return int(ox + x * SCALE), int(oy - y * SCALE)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 2 - Ackermann vs Diferencial")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    ack = VeiculoAckermann(0.0, 0.0, 0.0)
    dif = VeiculoDiferencial(0.0, 0.0, 0.0)
    origem_ack = (250, 200)
    origem_dif = (250, 480)
    trajeto_a = []
    trajeto_d = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        # Controle do veiculo Ackermann (setas)
        if keys[pygame.K_UP]:
            ack.v += V_STEP * dt * 10
        if keys[pygame.K_DOWN]:
            ack.v -= V_STEP * dt * 10
        if keys[pygame.K_LEFT]:
            ack.phi = max(-PHI_MAX, ack.phi - PHI_STEP)
        if keys[pygame.K_RIGHT]:
            ack.phi = min(PHI_MAX, ack.phi + PHI_STEP)
        if keys[pygame.K_SPACE]:
            ack.phi = 0.0

        # Controle do veiculo diferencial (W/S para v, A/D para w) - so para comparacao
        if keys[pygame.K_w]:
            dif.v += V_STEP * dt * 10
        if keys[pygame.K_s]:
            dif.v -= V_STEP * dt * 10
        if keys[pygame.K_a]:
            dif.w -= PHI_STEP * dt * 30
        if keys[pygame.K_d]:
            dif.w += PHI_STEP * dt * 30

        ack.step(dt)
        dif.step(dt)

        trajeto_a.append(to_screen(ack.x, ack.y, *origem_ack))
        trajeto_d.append(to_screen(dif.x, dif.y, *origem_dif))

        screen.fill(COR_FUNDO)
        pygame.draw.line(screen, (80, 80, 90), (0, 340), (LARGURA, 340), 1)

        if len(trajeto_a) > 1:
            pygame.draw.lines(screen, COR_TRAJETO_A, False, trajeto_a, 2)
        if len(trajeto_d) > 1:
            pygame.draw.lines(screen, COR_TRAJETO_D, False, trajeto_d, 2)

        pos_a = to_screen(ack.x, ack.y, *origem_ack)
        pygame.draw.circle(screen, COR_ACKERMANN, pos_a, 10)
        pygame.draw.line(screen, (255, 50, 50), pos_a,
                          (pos_a[0] + 20 * math.cos(ack.theta), pos_a[1] - 20 * math.sin(ack.theta)), 3)

        pos_d = to_screen(dif.x, dif.y, *origem_dif)
        pygame.draw.circle(screen, COR_DIFERENCIAL, pos_d, 10)
        pygame.draw.line(screen, (255, 50, 50), pos_d,
                          (pos_d[0] + 20 * math.cos(dif.theta), pos_d[1] - 20 * math.sin(dif.theta)), 3)

        raio_txt = "inf" if math.isinf(ack.raio()) else f"{ack.raio():.2f} m"
        linhas = [
            "ACKERMANN (setas: cima/baixo=v, esq/dir=phi, espaco=zera phi)",
            f"  v={ack.v:5.2f} m/s  phi={math.degrees(ack.phi):5.1f} graus  "
            f"w={ack.w():.3f} rad/s  R={raio_txt}",
            "DIFERENCIAL (W/S=v, A/D=w) - referencia: consegue R=0 com v=0",
            f"  v={dif.v:5.2f} m/s  w={dif.w:.3f} rad/s",
        ]
        for i, l in enumerate(linhas):
            screen.blit(font.render(l, True, COR_TEXTO), (20, 20 + i * 20))

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
