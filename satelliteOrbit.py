import numpy as np
import matplotlib.pyplot as plt

# Constantes físicas
G = 6.67430e-11  # m³/kg/s²
M_earth = 5.972e24  # kg
R_earth = 6.371e6  # m

def simulate_orbit(vy0, t_max=6000, dt=1):
    x, y = [R_earth + 300e3], [0]
    vx, vy = [0], [vy0]

    for _ in range(int(t_max / dt)):
        r = np.sqrt(x[-1]**2 + y[-1]**2)
        if r < R_earth:
            break  # colisão com a Terra
        ax = -G * M_earth * x[-1] / r**3
        ay = -G * M_earth * y[-1] / r**3

        vx_new = vx[-1] + ax * dt
        vy_new = vy[-1] + ay * dt

        x_new = x[-1] + vx_new * dt
        y_new = y[-1] + vy_new * dt

        x.append(x_new)
        y.append(y_new)
        vx.append(vx_new)
        vy.append(vy_new)

    return x, y

# Lista de velocidades iniciais para comparar
velocities = [7500, 7700, 7900, 8200, 11000]  # m/s
colors = ['blue', 'green', 'orange', 'purple', 'red']

plt.figure(figsize=(8, 8))
for v, c in zip(velocities, colors):
    x, y = simulate_orbit(vy0=v)
    plt.plot(x, y, label=f'{v} m/s', color=c)

# Terra no centro
circle = plt.Circle((0, 0), R_earth, color='gray', alpha=0.5, label='Terra')
plt.gca().add_artist(circle)

plt.axis('equal')
plt.title('Órbitas com diferentes velocidades iniciais')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
