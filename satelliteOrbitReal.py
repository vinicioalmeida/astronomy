from skyfield.api import load, EarthSatellite
import matplotlib.pyplot as plt

# Baixamos os dados TLE do NORAD (exemplo: ISS)
lines = [
    "ISS (ZARYA)",
    "1 25544U 98067A   24154.57013889  .00014466  00000+0  26242-3 0  9996",
    "2 25544  51.6393 174.5467 0004444 104.4969  49.9257 15.50630521449855"
]

# Criamos o objeto satélite e carregamos efemérides
satellite = EarthSatellite(lines[1], lines[2], lines[0])
ts = load.timescale()

# Simulamos posições ao longo de uma órbita (~90 minutos)
times = ts.utc(2024, 6, 3, range(0, 91))  # uma posição por minuto
geocentric = satellite.at(times)

# Extraímos coordenadas cartesianas (x, y, z) em km
positions = geocentric.position.km
x, y, z = positions

# Plotagem 2D (x vs y) da órbita projetada no plano equatorial
plt.figure(figsize=(8, 8))
plt.plot(x, y, label='ISS')
plt.scatter([0], [0], color='blue', s=100, label='Terra')
plt.title('Órbita da ISS baseada em dados reais (TLE)')
plt.xlabel('x (km)')
plt.ylabel('y (km)')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.tight_layout()
plt.show()



from skyfield.api import load, EarthSatellite
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Importa suporte 3D do matplotlib

# Dados TLE reais do NOAA 19 (retirados do Celestrak)
lines = [
    "NOAA 19",
    "1 33591U 09005A   24155.01902778  .00000098  00000+0  92610-4 0  9997",
    "2 33591  99.1899  38.9610 0014732 313.1985  46.7824 14.12535453796876"
]

# Criando o objeto satélite
satellite = EarthSatellite(lines[1], lines[2], lines[0])
ts = load.timescale()

# Criando um intervalo de tempo (100 minutos, 1 ponto por minuto)
times = ts.utc(2024, 6, 3, range(101))
geocentric = satellite.at(times)

# Posição no espaço (em km)
x, y, z = geocentric.position.km

# Plotagem 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Trajetória do satélite
ax.plot(x, y, z, label='NOAA 19', color='green')

# Centro da Terra
ax.scatter(0, 0, 0, color='blue', s=100, label='Terra')

# Configurações visuais
ax.set_title('Órbita 3D do NOAA 19 (TLE real)', fontsize=14)
ax.set_xlabel('x (km)')
ax.set_ylabel('y (km)')
ax.set_zlabel('z (km)')
ax.legend()
ax.grid(True)

# Proporção igual nos 3 eixos
max_range = max(
    max(abs(x).max(), abs(y).max(), abs(z).max()),
    7000  # para garantir a Terra visível
)
for axis in [ax.set_xlim, ax.set_ylim, ax.set_zlim]:
    axis(-max_range, max_range)

plt.tight_layout()
plt.show()
