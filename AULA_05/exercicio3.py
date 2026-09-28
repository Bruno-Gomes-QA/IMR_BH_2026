# Parâmetros do controlador
DIST_CRITICA = 0.4   # m  - abaixo disso, aciona o freio
V_NOMINAL    = 0.5   # m/s - velocidade de cruzeiro
OMEGA_GIRO   = 1.0   # rad/s - velocidade de giro sobre o eixo
K_OMEGA      = 1.0   # ganho proporcional (rad/s por metro de diferença)
OMEGA_MAX    = 1.0   # rad/s - saturação da velocidade angular


def controle_reativo(distancias):
    """
    distancias = {'frente': float, 'esquerda': float, 'direita': float}
    Retorna (v, omega): v em m/s, omega em rad/s (positivo = anti-horário/esquerda).
    """
    frente   = distancias['frente']
    esquerda = distancias['esquerda']
    direita  = distancias['direita']

    # 1) Trava de segurança: obstáculo à frente
    if frente < DIST_CRITICA:
        v = 0.0
        # Gira para o lado mais livre (esquerda = +omega, direita = -omega)
        omega = OMEGA_GIRO if esquerda >= direita else -OMEGA_GIRO
        return v, omega

    # 2) Frente livre: avança e ajusta omega pela diferença lateral
    v = V_NOMINAL
    omega = K_OMEGA * (esquerda - direita)   # mais espaço à esquerda -> vira à esquerda
    omega = max(-OMEGA_MAX, min(OMEGA_MAX, omega))  # saturação

    return v, omega

print(controle_reativo({'frente': 0.3, 'esquerda': 1.2, 'direita': 0.5}))  # (0.0, 1.0)   freia, gira p/ esquerda
print(controle_reativo({'frente': 0.3, 'esquerda': 0.4, 'direita': 2.0}))  # (0.0, -1.0)  freia, gira p/ direita
print(controle_reativo({'frente': 2.0, 'esquerda': 1.0, 'direita': 0.6}))  # (0.5, 0.4)   avança, corrige p/ esquerda
print(controle_reativo({'frente': 2.0, 'esquerda': 1.0, 'direita': 1.0}))  # (0.5, 0.0)   avança reto
