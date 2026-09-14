### Lab 1 - Validador de Pose em malha aberta (Cinematica Diferencial) ####


"""
Aplica uma sequencia temporizada de comandos (v, omega) a um robo
diferencial partindo da origem (0,0,0) e:
  1. Calcula a pose final TEORICA por integracao analitica exata
     (valida pois cada trecho tem v=0 OU omega=0).
  2. Simula o movimento no Pygame, integrando passo a passo (Euler)
     a cada frame, e imprime a pose final SIMULADA para comparacao.
"""

"""
NOME: HENRIQUE RIBEIRO SIQUEIRA e BRUNO MENEZES GOMES
PROF.: FLAVIO SANTARELLI - DATA: 14/09/2026
MATÉRIA: INTELLIGENT MOBILE ROBOTS - CURSO: CIÊNCIA DA COMPUTAÇÃO
PERÍODO: NOTURNO
"""

import pygame
import math
import sys

# ---------------------------------------------------------------------
# Parametros de simulacao
# ---------------------------------------------------------------------
FPS = 60
DT = 1.0 / FPS
SCALE = 80          # pixels por metro
WIDTH, HEIGHT = 900, 700
ORIGIN = (150, HEIGHT - 150)   # origem do mundo na tela (x cresce p/ direita, y p/ cima)
ROBOT_RADIUS = 0.15  # metros (raio do robo para desenho)

# ---------------------------------------------------------------------
# Sequencia de comandos: (v [m/s], omega [rad/s], duracao [s])
# ---------------------------------------------------------------------
SEGMENTS = [
    (0.5, 0.0, 4.0),            # Trecho 1: reta
    (0.0, math.pi / 4, 2.0),    # Trecho 2: giro no proprio eixo (0.7854 rad/s)
    (0.4, 0.0, 3.0),            # Trecho 3: reta na nova orientacao
]


def world_to_screen(x, y):
    sx = ORIGIN[0] + x * SCALE
    sy = ORIGIN[1] - y * SCALE
    return int(sx), int(sy)


def normalize_angle(theta):
    return math.atan2(math.sin(theta), math.cos(theta))


def compute_theoretical_pose(x0, y0, theta0, segments):
    """Integracao analitica exata para trechos com v=0 ou omega=0."""
    x, y, theta = x0, y0, theta0
    for v, omega, t in segments:
        if abs(omega) < 1e-9:
            # movimento retilineo: heading constante durante o trecho
            x += v * math.cos(theta) * t
            y += v * math.sin(theta) * t
        elif abs(v) < 1e-9:
            # rotacao pura no proprio eixo
            theta += omega * t
        else:
            # caso geral (arco), nao usado nesta pratica mas incluido por completude
            theta_new = theta + omega * t
            x += (v / omega) * (math.sin(theta_new) - math.sin(theta))
            y -= (v / omega) * (math.cos(theta_new) - math.cos(theta))
            theta = theta_new
    return x, y, normalize_angle(theta)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Lab 1 - Validador de Pose (Malha Aberta)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    # Pose teorica (calculada antes, de forma analitica)
    x_teo, y_teo, theta_teo = compute_theoretical_pose(0.0, 0.0, 0.0, SEGMENTS)

    # Pose simulada (sera integrada frame a frame, igual ao desenho)
    x, y, theta = 0.0, 0.0, 0.0
    trail = [world_to_screen(x, y)]

    seg_index = 0
    seg_elapsed = 0.0
    finished = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not finished:
            v, omega, duration = SEGMENTS[seg_index]
            step = min(DT, duration - seg_elapsed)
            if step > 0:
                x += v * math.cos(theta) * step
                y += v * math.sin(theta) * step
                theta += omega * step
                seg_elapsed += step
                trail.append(world_to_screen(x, y))

            if seg_elapsed >= duration - 1e-9:
                seg_index += 1
                seg_elapsed = 0.0
                if seg_index >= len(SEGMENTS):
                    finished = True
                    theta_norm = normalize_angle(theta)

                    print("=" * 62)
                    print("Pose final TEORICA:")
                    print(f"  x     = {x_teo:.4f} m")
                    print(f"  y     = {y_teo:.4f} m")
                    print(f"  theta = {theta_teo:.4f} rad ({math.degrees(theta_teo):.2f} graus)")
                    print("-" * 62)
                    print("Pose final SIMULADA:")
                    print(f"  x     = {x:.4f} m")
                    print(f"  y     = {y:.4f} m")
                    print(f"  theta = {theta_norm:.4f} rad ({math.degrees(theta_norm):.2f} graus)")
                    print("=" * 62)
                    print(
                        "Erro |teorico - simulado|: "
                        f"dx={abs(x_teo - x):.6f}  "
                        f"dy={abs(y_teo - y):.6f}  "
                        f"dtheta={abs(theta_teo - theta_norm):.6f} rad"
                    )

        # ---------------- desenho ----------------
        screen.fill((30, 30, 30))

        for gx in range(0, WIDTH, SCALE):
            pygame.draw.line(screen, (50, 50, 50), (gx, 0), (gx, HEIGHT))
        for gy in range(0, HEIGHT, SCALE):
            pygame.draw.line(screen, (50, 50, 50), (0, gy), (WIDTH, gy))

        ox, oy = ORIGIN
        pygame.draw.line(screen, (90, 90, 90), (0, oy), (WIDTH, oy), 2)
        pygame.draw.line(screen, (90, 90, 90), (ox, 0), (ox, HEIGHT), 2)

        if len(trail) > 1:
            pygame.draw.lines(screen, (0, 200, 255), False, trail, 2)

        rx, ry = world_to_screen(x, y)
        pygame.draw.circle(screen, (255, 200, 0), (rx, ry), int(ROBOT_RADIUS * SCALE))
        heading_len = ROBOT_RADIUS * SCALE * 1.8
        hx = rx + heading_len * math.cos(theta)
        hy = ry - heading_len * math.sin(theta)
        pygame.draw.line(screen, (255, 0, 0), (rx, ry), (hx, hy), 3)

        theta_disp = normalize_angle(theta)
        cur_seg = min(seg_index + 1, len(SEGMENTS))
        status = "[FINALIZADO]" if finished else f"t = {seg_elapsed:4.2f}s"
        lines = [
            f"x = {x:6.3f} m   y = {y:6.3f} m   theta = {math.degrees(theta_disp):6.2f} graus",
            f"Segmento {cur_seg}/{len(SEGMENTS)}   {status}",
        ]
        for i, line in enumerate(lines):
            surf = font.render(line, True, (255, 255, 255))
            screen.blit(surf, (10, 10 + i * 22))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()