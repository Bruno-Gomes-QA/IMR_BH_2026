"""
Lab 1 - Validador de Pose em Malha Aberta (Cinematica Diferencial)
NOME: BRUNO MENEZES GOMES / HENRIQUE RIBEIRO SIQUEIRA
PROF.: FLAVIO SANTARELLI - DATA: 14/09/26
CURSO: CIENCIA DA COMPUTACAO - NOTURNO
"""

import math
import pygame

LARGURA, ALTURA = 900, 650
FPS = 60
SCALE = 150.0  # px por metro (so para desenho)
OFFSET_X, OFFSET_Y = 150, 400

COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_TRAJETO = (0, 255, 100)
COR_TEXTO = (220, 220, 220)

# Sequencia de comandos em malha aberta: (duracao_s, v_m_s, w_rad_s)
SEGMENTOS = [
    (4.0, 0.5, 0.0),
    (2.0, 0.0, math.pi / 4),
    (3.0, 0.4, 0.0),
]


def integrar_exato(x, y, theta, v, w, dt):
    """Integracao exata do modelo unicycle para v, w constantes em dt."""
    if abs(w) < 1e-9:
        x += v * dt * math.cos(theta)
        y += v * dt * math.sin(theta)
    else:
        novo_theta = theta + w * dt
        x += (v / w) * (math.sin(novo_theta) - math.sin(theta))
        y -= (v / w) * (math.cos(novo_theta) - math.cos(theta))
        theta = novo_theta
    return x, y, theta


def pose_teorica_final():
    x, y, theta = 0.0, 0.0, 0.0
    for t, v, w in SEGMENTOS:
        x, y, theta = integrar_exato(x, y, theta, v, w, t)
    return x, y, theta


def to_screen(x, y):
    return int(OFFSET_X + x * SCALE), int(OFFSET_Y - y * SCALE)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 1 - Validador de Pose em Malha Aberta")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    teorico = pose_teorica_final()

    x, y, theta = 0.0, 0.0, 0.0
    trajeto = [to_screen(x, y)]
    seg_idx = 0
    seg_tempo_restante = SEGMENTOS[0][0]
    simulacao_ativa = True
    simulado = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if simulacao_ativa:
            passo = min(dt, seg_tempo_restante)
            _, v, w = SEGMENTOS[seg_idx]
            x, y, theta = integrar_exato(x, y, theta, v, w, passo)
            trajeto.append(to_screen(x, y))
            seg_tempo_restante -= passo

            if seg_tempo_restante <= 1e-6:
                seg_idx += 1
                if seg_idx >= len(SEGMENTOS):
                    simulacao_ativa = False
                    simulado = (x, y, theta)
                    print("=== Pose final (graus para theta) ===")
                    print(f"Teorica : x={teorico[0]:.4f} m  y={teorico[1]:.4f} m  "
                          f"theta={math.degrees(teorico[2]):.2f} graus")
                    print(f"Simulada: x={simulado[0]:.4f} m  y={simulado[1]:.4f} m  "
                          f"theta={math.degrees(simulado[2]):.2f} graus")
                else:
                    seg_tempo_restante = SEGMENTOS[seg_idx][0]

        screen.fill(COR_FUNDO)
        if len(trajeto) > 1:
            pygame.draw.lines(screen, COR_TRAJETO, False, trajeto, 2)

        pos = to_screen(x, y)
        pygame.draw.circle(screen, COR_ROBO, pos, 12)
        fx = pos[0] + 22 * math.cos(theta)
        fy = pos[1] - 22 * math.sin(theta)
        pygame.draw.line(screen, (255, 50, 50), pos, (fx, fy), 3)

        linhas = [
            f"Pose atual: x={x:.2f}m y={y:.2f}m theta={math.degrees(theta):.1f} graus",
            f"Pose teorica final: x={teorico[0]:.2f}m y={teorico[1]:.2f}m "
            f"theta={math.degrees(teorico[2]):.1f} graus",
        ]
        if not simulacao_ativa:
            linhas.append("Simulacao concluida - ver terminal para comparacao completa.")
        for i, l in enumerate(linhas):
            screen.blit(font.render(l, True, COR_TEXTO), (20, 20 + i * 20))

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
