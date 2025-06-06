# Simulador simples de órbita elíptica usando gravitação de Newton
# Autor: ChatGPT + Vinicio Almeida
# Requisitos: numpy, matplotlib

import numpy as np
import matplotlib.pyplot as plt

# Constantes físicas
G = 6.67430e-11  # Constante gravitacional, m^3 kg^-1 s^-2
M = 5.972e24     # Massa da Terra, kg

# Condições iniciais
r0 = np.array([7.0e6, 0.0])      # posição inicial (m)
v0 = np.array([0.0, 7500.0])     # velocidade inicial (m/s)

# Parâmetros de tempo
dt = 10.0         # intervalo de tempo (s)
t_max = 10000.0   # tempo total (s)

# Inicializações
r = r0.copy()
v = v0.copy()
positions = [r.copy()]

# Loop de simulação
t = 0.0
while t < t_max:
    r_norm = np.linalg.norm(r)
    a = -G * M * r / r_norm**3
    v += a * dt
    r += v * dt
    positions.append(r.copy())
    t += dt

# Conversão para array
positions = np.array(positions)

# Plot da órbita
plt.figure(figsize=(6,6))
plt.plot(positions[:,0], positions[:,1], label='Órbita')
plt.plot(0, 0, 'yo', label='Terra')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.legend()
plt.axis('equal')
plt.title('Simulação de Órbita Elíptica')
plt.grid(True)
plt.show()
