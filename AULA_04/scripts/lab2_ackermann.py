"""
NOME: HENRIQUE RIBEIRO SIQUEIRA e BRUNO MENEZES GOMES
PROF.: FLAVIO SANTARELLI - DATA: 14/09/2026
MATÉRIA: INTELLIGENT MOBILE ROBOTS - CURSO: CIÊNCIA DA COMPUTAÇÃO
PERÍODO: NOTURNO


------------------
Laboratório 2 - Calculadora de giro Ackermann vs. Diferencial

Objetivo:
    Comparar visualmente e matematicamente o raio de curvatura de uma
    tração Ackermann em relação ao modelo Diferencial.

Controles:
    Setas CIMA / BAIXO  -> aumenta / diminui a velocidade linear v
    Setas ESQUERDA/DIREITA:
        - Modo ACKERMANN: aumenta / diminui o ângulo de esterço φ (graus)
        - Modo DIFERENCIAL: aumenta / diminui a velocidade angular ω direto
    TAB                 -> alterna entre modo ACKERMANN e DIFERENCIAL
    R                   -> reinicia posição, trajetória e velocidades
    ESC / fechar janela -> sai

Modelo Ackermann:
    ω = (v / L) * tan(φ)        com φ limitado a ±φ_max = ±30°
    R = L / tan(φ)              (R -> ∞ quando φ -> 0; nunca R = 0)

Modelo Diferencial:
    ω é definido diretamente pelo usuário, independente de v.
    Logo é possível ter v = 0 e ω ≠ 0  =>  R = v/ω = 0 (giro sobre o
    próprio eixo), algo que o Ackermann nunca consegue realizar.


"""

import math
import sys
import pygame

# --------------------------------------------------------------------------- #
# Parâmetros gerais
# --------------------------------------------------------------------------- #
LARGURA, ALTURA = 1000, 700
FPS = 60

L = 2.0                     # entre-eixos (m) do veículo Ackermann
PHI_MAX_DEG = 30.0           # ângulo máximo de esterço (graus)
PHI_MAX = math.radians(PHI_MAX_DEG)

PIXELS_POR_METRO = 40        # escala de desenho
DT = 1 / FPS                 # passo de integração (s)

V_STEP = 0.3                 # incremento de velocidade linear (m/s) por tecla
V_MAX = 4.0
PHI_STEP = math.radians(1.5) # incremento de ângulo de esterço por tecla
OMEGA_STEP = 0.3              # incremento de ω no modo diferencial (rad/s)
OMEGA_MAX = 3.0

TRAIL_MAX_PONTOS = 4000

BRANCO = (245, 245, 245)
PRETO = (20, 20, 20)
CINZA = (120, 120, 120)
AZUL = (50, 120, 230)
VERMELHO = (220, 60, 60)
VERDE = (40, 170, 90)
AMARELO = (230, 180, 40)


class Robo:
    """Representa o estado cinemático do robô (pose + trajetória)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0        # orientação (rad)
        self.v = 0.0             # velocidade linear (m/s)
        self.phi = 0.0            # ângulo de esterço - modo Ackermann (rad)
        self.omega_manual = 0.0    # ω direto - modo Diferencial (rad/s)
        self.trail = []

    def omega_atual(self, modo):
        """Retorna ω conforme o modo ativo."""
        if modo == "ackermann":
            return (self.v / L) * math.tan(self.phi)
        else:  # diferencial
            return self.omega_manual

    def raio_atual(self, modo):
        """Retorna o raio de curvatura R (None representa R infinito)."""
        omega = self.omega_atual(modo)
        if modo == "ackermann":
            if abs(math.tan(self.phi)) < 1e-6:
                return None  # reta, R -> infinito
            return L / math.tan(self.phi)
        else:
            if abs(omega) < 1e-6:
                return None
            return self.v / omega

    def atualizar(self, modo, dt):
        omega = self.omega_atual(modo)
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        self.theta += omega * dt

        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_MAX_PONTOS:
            self.trail.pop(0)


def mundo_para_tela(x, y):
    """Converte coordenadas do mundo (metros) para pixels na tela,
    com origem no centro da janela e eixo y invertido."""
    cx, cy = LARGURA // 2, ALTURA // 2
    px = cx + x * PIXELS_POR_METRO
    py = cy - y * PIXELS_POR_METRO
    return int(px), int(py)


def desenhar_robo(tela, robo):
    px, py = mundo_para_tela(robo.x, robo.y)
    tamanho = 14
    # triângulo apontando na direção theta
    ponta = (px + tamanho * math.cos(robo.theta),
             py - tamanho * math.sin(robo.theta))
    esquerda = (px + tamanho * 0.6 * math.cos(robo.theta + 2.5),
                py - tamanho * 0.6 * math.sin(robo.theta + 2.5))
    direita = (px + tamanho * 0.6 * math.cos(robo.theta - 2.5),
               py - tamanho * 0.6 * math.sin(robo.theta - 2.5))
    pygame.draw.polygon(tela, AZUL, [ponta, esquerda, direita])


def desenhar_trilha(tela, robo):
    if len(robo.trail) < 2:
        return
    pontos = [mundo_para_tela(x, y) for x, y in robo.trail]
    pygame.draw.lines(tela, VERDE, False, pontos, 2)


def desenhar_raio(tela, robo, modo):
    """Desenha o círculo de curvatura instantâneo (quando existir)."""
    R = robo.raio_atual(modo)
    if R is None:
        return
    # centro do círculo de curvatura fica perpendicular à direção do robô
    cx = robo.x - R * math.sin(robo.theta)
    cy = robo.y + R * math.cos(robo.theta)
    centro_px = mundo_para_tela(cx, cy)
    raio_px = int(abs(R) * PIXELS_POR_METRO)
    if 0 < raio_px < 5000:
        pygame.draw.circle(tela, CINZA, centro_px, raio_px, 1)
        pygame.draw.circle(tela, AMARELO, centro_px, 3)


def formatar_raio(R):
    if R is None:
        return "∞ (reta)"
    return f"{R:.2f} m"


def desenhar_hud(tela, fonte, fonte_titulo, robo, modo):
    omega = robo.omega_atual(modo)
    R = robo.raio_atual(modo)

    linhas = []
    titulo = "MODO: ACKERMANN (tração dianteira com esterço)" if modo == "ackermann" \
        else "MODO: DIFERENCIAL (duas rodas, velocidades independentes)"
    cor_titulo = AZUL if modo == "ackermann" else VERMELHO

    linhas.append(f"v (velocidade linear)      = {robo.v:5.2f} m/s")
    if modo == "ackermann":
        linhas.append(f"φ (ângulo de esterço)      = {math.degrees(robo.phi):6.2f}°  "
                       f"(limite ±{PHI_MAX_DEG:.0f}°)")
        linhas.append(f"ω = (v/L)·tan(φ)          = {omega:6.3f} rad/s")
        linhas.append(f"R = L/tan(φ)               = {formatar_raio(R)}")
        linhas.append("")
        linhas.append("Observação: mesmo com φ = φ_max, R nunca chega a 0.")
        linhas.append(f"R mínimo teórico (φ=30°)   = {L/math.tan(PHI_MAX):.2f} m")
    else:
        linhas.append(f"ω (definido pelo usuário)  = {robo.omega_manual:6.3f} rad/s")
        linhas.append(f"R = v/ω                    = {formatar_raio(R)}")
        linhas.append("")
        linhas.append("Observação: com v = 0 e ω ≠ 0, R = 0 (giro no próprio eixo).")

    tela.blit(fonte_titulo.render(titulo, True, cor_titulo), (20, 15))

    y = 55
    for linha in linhas:
        tela.blit(fonte.render(linha, True, PRETO), (20, y))
        y += 24

    comandos = [
        "↑/↓: velocidade v   ←/→: φ ou ω   TAB: alterna modo   R: reinicia   ESC: sair"
    ]
    for linha in comandos:
        tela.blit(fonte.render(linha, True, CINZA), (20, ALTURA - 30))


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 2 - Ackermann vs Diferencial")
    relogio = pygame.time.Clock()

    fonte = pygame.font.SysFont("consolas", 18)
    fonte_titulo = pygame.font.SysFont("consolas", 20, bold=True)

    robo = Robo()
    modo = "ackermann"  # ou "diferencial"

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_TAB:
                    modo = "diferencial" if modo == "ackermann" else "ackermann"
                elif evento.key == pygame.K_r:
                    robo.reset()

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_UP]:
            robo.v = min(V_MAX, robo.v + V_STEP * DT * 10)
        if teclas[pygame.K_DOWN]:
            robo.v = max(-V_MAX, robo.v - V_STEP * DT * 10)

        if modo == "ackermann":
            if teclas[pygame.K_LEFT]:
                robo.phi = min(PHI_MAX, robo.phi + PHI_STEP)
            if teclas[pygame.K_RIGHT]:
                robo.phi = max(-PHI_MAX, robo.phi - PHI_STEP)
        else:
            if teclas[pygame.K_LEFT]:
                robo.omega_manual = min(OMEGA_MAX, robo.omega_manual + OMEGA_STEP * DT * 10)
            if teclas[pygame.K_RIGHT]:
                robo.omega_manual = max(-OMEGA_MAX, robo.omega_manual - OMEGA_STEP * DT * 10)

        robo.atualizar(modo, DT)

        tela.fill(BRANCO)
        desenhar_raio(tela, robo, modo)
        desenhar_trilha(tela, robo)
        desenhar_robo(tela, robo)
        desenhar_hud(tela, fonte, fonte_titulo, robo, modo)

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()