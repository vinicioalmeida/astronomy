import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import math

class CelestialBody:
    def __init__(self, name, distance, period, radius, color, orbital_inclination=0, eccentricity=0, parent=None):
        self.name = name
        self.distance = distance  # Distância média em UA (escalonada para visualização)
        self.period = period      # Período orbital em dias terrestres
        self.radius = radius      # Raio visual
        self.color = color
        self.orbital_inclination = np.radians(orbital_inclination)  # Inclinação orbital
        self.eccentricity = eccentricity  # Excentricidade da órbita
        self.parent = parent      # Corpo pai (para luas)
        
        # Posição inicial aleatória
        self.angle = np.random.uniform(0, 2*np.pi)
        self.x = 0
        self.y = 0
        self.trail_x = []
        self.trail_y = []
        
    def update_position(self, time_days):
        # Velocidade angular (rad/dia)
        angular_velocity = 2 * np.pi / self.period
        
        # Posição atual
        current_angle = self.angle + angular_velocity * time_days
        
        # Distância com excentricidade (aproximação simples)
        r = self.distance * (1 - self.eccentricity * np.cos(current_angle))
        
        if self.parent is None:  # Planeta orbitando o Sol
            self.x = r * np.cos(current_angle)
            self.y = r * np.sin(current_angle) * np.cos(self.orbital_inclination)
        else:  # Lua orbitando um planeta
            # Posição relativa ao planeta pai
            rel_x = r * np.cos(current_angle)
            rel_y = r * np.sin(current_angle)
            
            # Posição absoluta
            self.x = self.parent.x + rel_x
            self.y = self.parent.y + rel_y
        
        # Adicionar à trilha
        self.trail_x.append(self.x)
        self.trail_y.append(self.y)
        
        # Limitar tamanho da trilha
        if len(self.trail_x) > 500:
            self.trail_x.pop(0)
            self.trail_y.pop(0)

class SolarSystem:
    def __init__(self):
        self.time = 0
        self.speed = 1
        self.show_trails = True
        self.show_orbits = True
        self.zoom = 1.0
        
        self.setup_bodies()
        self.setup_plot()
        
    def setup_bodies(self):
        self.bodies = []
        
        # Sol
        self.sun = CelestialBody("Sol", 0, 0, 20, '#FDB813')
        self.bodies.append(self.sun)
        
        # Planetas internos
        mercury = CelestialBody("Mercúrio", 0.8, 88, 3, '#FFA500', 7.0, 0.206)
        venus = CelestialBody("Vênus", 1.2, 225, 4, '#FFC649', 3.4, 0.007)
        earth = CelestialBody("Terra", 1.8, 365, 5, '#6B93D6', 0.0, 0.017)
        mars = CelestialBody("Marte", 2.5, 687, 4, '#C1440E', 1.9, 0.093)
        
        self.bodies.extend([mercury, venus, earth, mars])
        
        # Planetas externos (distâncias ajustadas para visualização)
        jupiter = CelestialBody("Júpiter", 4.0, 4333, 12, '#D8CA9D', 1.3, 0.049)
        saturn = CelestialBody("Saturno", 5.5, 10759, 10, '#FAD5A5', 2.5, 0.057)
        uranus = CelestialBody("Urano", 7.0, 30687, 8, '#4FD0E7', 0.8, 0.046)
        neptune = CelestialBody("Netuno", 8.5, 60190, 8, '#4B70DD', 1.8, 0.010)
        
        self.bodies.extend([jupiter, saturn, uranus, neptune])
        
        # Planetas anões
        pluto = CelestialBody("Plutão", 9.5, 90560, 2, '#DEB887', 17.2, 0.244)
        ceres = CelestialBody("Ceres", 3.2, 1682, 1, '#C7C5B8', 10.6, 0.076)
        eris = CelestialBody("Éris", 12.0, 203830, 2, '#E6E6FA', 44.2, 0.442)
        makemake = CelestialBody("Makemake", 11.0, 112897, 1.5, '#D2691E', 29.0, 0.159)
        haumea = CelestialBody("Haumea", 10.5, 103410, 1.5, '#F5DEB3', 28.2, 0.195)
        
        self.bodies.extend([pluto, ceres, eris, makemake, haumea])
        
        # Luas principais
        # Lua da Terra
        moon = CelestialBody("Lua", 0.15, 27.3, 2, '#C0C0C0', 5.1, 0.055, earth)
        
        # Luas de Júpiter (Galileanas)
        io = CelestialBody("Io", 0.25, 1.8, 1.5, '#FFFF99', 0.0, 0.004, jupiter)
        europa = CelestialBody("Europa", 0.35, 3.6, 1.5, '#87CEEB', 0.5, 0.009, jupiter)
        ganimedes = CelestialBody("Ganimedes", 0.50, 7.2, 2, '#8B7D6B', 0.2, 0.001, jupiter)
        calisto = CelestialBody("Calisto", 0.70, 16.7, 2, '#4A4A4A', 0.2, 0.007, jupiter)
        
        # Luas de Saturno
        titan = CelestialBody("Titã", 0.60, 16.0, 2, '#FFA500', 0.3, 0.029, saturn)
        enceladus = CelestialBody("Encélado", 0.30, 1.4, 1, '#FFFFFF', 0.0, 0.005, saturn)
        
        # Luas de Urano
        titania = CelestialBody("Titânia", 0.40, 8.7, 1.5, '#C0C0C0', 0.3, 0.001, uranus)
        oberon = CelestialBody("Oberon", 0.55, 13.5, 1.5, '#8B7D6B', 0.1, 0.001, uranus)
        
        # Lua de Netuno
        triton = CelestialBody("Tritão", 0.35, -5.9, 1.5, '#FFB6C1', 157, 0.000, neptune)
        
        # Lua de Plutão
        charon = CelestialBody("Caronte", 0.08, 6.4, 1, '#8B7D6B', 0.0, 0.003, pluto)
        
        self.bodies.extend([moon, io, europa, ganimedes, calisto, titan, enceladus, 
                           titania, oberon, triton, charon])
        
        # Asteroides principais (Cinturão de Asteroides)
        asteroid_names = ["Vesta", "Pallas", "Juno", "Hygiea", "Iris", "Flora"]
        for i, name in enumerate(asteroid_names):
            distance = np.random.uniform(2.8, 3.5)  # Cinturão de asteroides
            period = distance ** 1.5 * 365  # Lei de Kepler aproximada
            inclination = np.random.uniform(0, 15)
            eccentricity = np.random.uniform(0.05, 0.25)
            asteroid = CelestialBody(name, distance, period, 0.5, '#8C7853', 
                                   inclination, eccentricity)
            self.bodies.append(asteroid)
        
        # Cometas (órbitas muito excêntricas)
        halley = CelestialBody("Halley", 15.0, 27375, 1, '#87CEEB', 162.3, 0.967)
        self.bodies.append(halley)
        
    def setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 10), facecolor='black')
        self.ax.set_facecolor('black')
        self.ax.set_aspect('equal')
        
        # Configurações visuais
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-12, 12)
        self.ax.grid(True, alpha=0.2, color='white')
        self.ax.set_title('Sistema Solar Completo - Simulação Detalhada', 
                         color='white', fontsize=16, fontweight='bold')
        
        # Remover ticks
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # Adicionar estrelas de fundo
        self.add_background_stars()
        
    def add_background_stars(self):
        np.random.seed(42)  # Para reprodutibilidade
        star_x = np.random.uniform(-15, 15, 200)
        star_y = np.random.uniform(-12, 12, 200)
        star_sizes = np.random.uniform(0.1, 2, 200)
        self.ax.scatter(star_x, star_y, s=star_sizes, c='white', alpha=0.6, marker='*')
        
    def animate(self, frame):
        self.ax.clear()
        self.ax.set_facecolor('black')
        self.ax.set_aspect('equal')
        
        # Reconfigurar limites e título
        zoom_factor = self.zoom
        self.ax.set_xlim(-15/zoom_factor, 15/zoom_factor)
        self.ax.set_ylim(-12/zoom_factor, 12/zoom_factor)
        self.ax.set_title(f'Sistema Solar - Dia {self.time:.0f} | Velocidade: {self.speed:.1f}x', 
                         color='white', fontsize=14)
        
        # Re-adicionar estrelas
        self.add_background_stars()
        
        # Atualizar tempo
        self.time += self.speed
        
        # Desenhar órbitas (círculos aproximados)
        if self.show_orbits:
            for body in self.bodies:
                if body.parent is None and body.name != "Sol":
                    orbit = Circle((0, 0), body.distance, fill=False, 
                                 color='gray', alpha=0.3, linestyle='--', linewidth=0.5)
                    self.ax.add_patch(orbit)
        
        # Atualizar e desenhar todos os corpos
        for body in self.bodies:
            if body.name != "Sol":
                body.update_position(self.time)
            
            # Desenhar trilhas
            if self.show_trails and len(body.trail_x) > 1:
                self.ax.plot(body.trail_x, body.trail_y, color=body.color, 
                           alpha=0.4, linewidth=0.8)
            
            # Desenhar corpo celeste
            self.ax.scatter(body.x, body.y, s=body.radius**2, c=body.color, 
                          alpha=0.9, edgecolors='white', linewidth=0.5)
            
            # Adicionar rótulos para objetos principais
            if body.radius > 3 or body.name in ["Lua", "Titã", "Ganimedes", "Plutão"]:
                self.ax.annotate(body.name, (body.x, body.y), 
                               xytext=(5, 5), textcoords='offset points',
                               color='white', fontsize=8, alpha=0.8)
        
        # Informações no canto
        info_text = f"Objetos: {len(self.bodies)}\n"
        info_text += "Planetas: 8 | Anões: 5 | Luas: 12\n"
        info_text += "Asteroides: 6 | Cometas: 1"
        
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    verticalalignment='top', color='cyan', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        # Controles
        controls_text = "Controles:\nSPACE: Pausar\n+/-: Velocidade\nT: Trilhas\nO: Órbitas\nZ/X: Zoom"
        self.ax.text(0.98, 0.02, controls_text, transform=self.ax.transAxes,
                    verticalalignment='bottom', horizontalalignment='right',
                    color='yellow', fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
    def on_key_press(self, event):
        if event.key == ' ':  # Pausar/despausar
            if hasattr(self, 'ani'):
                if self.ani.event_source:
                    self.ani.event_source.stop()
                    self.ani.event_source = None
                else:
                    self.ani.event_source = self.fig.canvas.new_timer()
                    self.ani.event_source.add_callback(self.ani._step)
                    self.ani.event_source.start()
        elif event.key == '+' or event.key == '=':  # Aumentar velocidade
            self.speed = min(self.speed * 1.5, 50)
        elif event.key == '-':  # Diminuir velocidade
            self.speed = max(self.speed / 1.5, 0.1)
        elif event.key == 't':  # Toggle trilhas
            self.show_trails = not self.show_trails
        elif event.key == 'o':  # Toggle órbitas
            self.show_orbits = not self.show_orbits
        elif event.key == 'z':  # Zoom in
            self.zoom = min(self.zoom * 1.2, 5.0)
        elif event.key == 'x':  # Zoom out
            self.zoom = max(self.zoom / 1.2, 0.2)
        elif event.key == 'r':  # Reset
            self.time = 0
            for body in self.bodies:
                body.trail_x.clear()
                body.trail_y.clear()
                body.angle = np.random.uniform(0, 2*np.pi)

    def run(self):
        # Conectar eventos de teclado
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Criar animação
        self.ani = animation.FuncAnimation(self.fig, self.animate, 
                                          frames=None, interval=50, 
                                          blit=False, repeat=True)
        
        plt.tight_layout()
        plt.show()

# Executar simulação
if __name__ == "__main__":
    print("🌌 Sistema Solar Completo - Simulação Detalhada")
    print("=" * 50)
    print("Objetos incluídos:")
    print("• 8 Planetas + Sol")
    print("• 5 Planetas anões (Plutão, Ceres, Éris, Makemake, Haumea)")
    print("• 12 Luas principais")
    print("• 6 Asteroides do cinturão principal")
    print("• 1 Cometa (Halley)")
    print("\nControles:")
    print("• SPACE: Pausar/Despausar")
    print("• +/-: Aumentar/Diminuir velocidade")
    print("• T: Mostrar/Ocultar trilhas")
    print("• O: Mostrar/Ocultar órbitas")
    print("• Z/X: Zoom in/out")
    print("• R: Reset simulação")
    print("\nIniciando simulação...")
    
    sistema = SolarSystem()
    sistema.run()