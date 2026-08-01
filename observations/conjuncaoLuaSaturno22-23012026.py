# Código para observação da conjunção Lua-Saturno em Natal/RN
# 22 e 23 de janeiro de 2026

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from skyfield.api import load, wgs84

# Carregar dados astronômicos
ts = load.timescale()
# Usar de440s.bsp que tem mais planetas, ou usar saturn barycenter
eph = load('de421.bsp')
terra = eph['earth']
lua = eph['moon']
saturno = eph['saturn barycenter']  # Usar o baricentro

# Coordenadas de Natal/RN
latitude = -5.795
longitude = -35.209
natal = wgs84.latlon(latitude, longitude)

# Datas de interesse
data_22 = datetime(2026, 1, 22)
data_23 = datetime(2026, 1, 23)

# Criar horários de observação (das 17h às 23h) para cada dia
horarios_22 = [data_22 + timedelta(hours=h, minutes=m) 
               for h in range(17, 24) for m in range(0, 60, 15)]
horarios_23 = [data_23 + timedelta(hours=h, minutes=m) 
               for h in range(17, 24) for m in range(0, 60, 15)]

# Função para calcular posição
def calcular_posicao(corpo, observador, tempo_skyfield):
    astrometrico = observador.at(tempo_skyfield).observe(corpo)
    alt, az, distancia = astrometrico.apparent().altaz()
    return alt.degrees, az.degrees

# Análise para 22 de janeiro
print("="*60)
print("CONJUNÇÃO LUA-SATURNO EM NATAL/RN")
print("="*60)
print("\n22 DE JANEIRO DE 2026:")
print("-"*60)

altitudes_lua_22 = []
azimutes_lua_22 = []
altitudes_saturno_22 = []
azimutes_saturno_22 = []
separacoes_22 = []
horarios_plot_22 = []

for horario in horarios_22:
    t = ts.utc(horario.year, horario.month, horario.day, 
               horario.hour, horario.minute)
    
    observador = terra + natal
    
    alt_lua, az_lua = calcular_posicao(lua, observador, t)
    alt_sat, az_sat = calcular_posicao(saturno, observador, t)
    
    # Calcular separação angular
    separacao = np.sqrt((az_lua - az_sat)**2 + (alt_lua - alt_sat)**2)
    
    if alt_lua > 0 and alt_sat > 0:  # Apenas quando ambos estão acima do horizonte
        altitudes_lua_22.append(alt_lua)
        azimutes_lua_22.append(az_lua)
        altitudes_saturno_22.append(alt_sat)
        azimutes_saturno_22.append(az_sat)
        separacoes_22.append(separacao)
        horarios_plot_22.append(horario)
        
        if horario.minute == 0:  # Mostrar apenas horas cheias
            print(f"{horario.strftime('%H:%M')} - Lua: Alt={alt_lua:.1f}° Az={az_lua:.1f}° | "
                  f"Saturno: Alt={alt_sat:.1f}° Az={az_sat:.1f}° | "
                  f"Separação: {separacao:.2f}°")

# Análise para 23 de janeiro
print("\n23 DE JANEIRO DE 2026:")
print("-"*60)

altitudes_lua_23 = []
azimutes_lua_23 = []
altitudes_saturno_23 = []
azimutes_saturno_23 = []
separacoes_23 = []
horarios_plot_23 = []

for horario in horarios_23:
    t = ts.utc(horario.year, horario.month, horario.day, 
               horario.hour, horario.minute)
    
    observador = terra + natal
    
    alt_lua, az_lua = calcular_posicao(lua, observador, t)
    alt_sat, az_sat = calcular_posicao(saturno, observador, t)
    
    separacao = np.sqrt((az_lua - az_sat)**2 + (alt_lua - alt_sat)**2)
    
    if alt_lua > 0 and alt_sat > 0:
        altitudes_lua_23.append(alt_lua)
        azimutes_lua_23.append(az_lua)
        altitudes_saturno_23.append(alt_sat)
        azimutes_saturno_23.append(az_sat)
        separacoes_23.append(separacao)
        horarios_plot_23.append(horario)
        
        if horario.minute == 0:
            print(f"{horario.strftime('%H:%M')} - Lua: Alt={alt_lua:.1f}° Az={az_lua:.1f}° | "
                  f"Saturno: Alt={alt_sat:.1f}° Az={az_sat:.1f}° | "
                  f"Separação: {separacao:.2f}°")

# Encontrar melhor momento (menor separação)
if len(separacoes_22) > 0:
    idx_melhor_22 = np.argmin(separacoes_22)
    print(f"\n🌙 MELHOR MOMENTO em 22/01: {horarios_plot_22[idx_melhor_22].strftime('%H:%M')}")
    print(f"   Separação mínima: {separacoes_22[idx_melhor_22]:.2f}°")
    print(f"   Altitude Lua: {altitudes_lua_22[idx_melhor_22]:.1f}°")
    print(f"   Direção (azimute): {azimutes_lua_22[idx_melhor_22]:.1f}° "
          f"({'O' if 225 < azimutes_lua_22[idx_melhor_22] < 315 else 'SO' if 180 < azimutes_lua_22[idx_melhor_22] < 270 else 'OSO'})")

if len(separacoes_23) > 0:
    idx_melhor_23 = np.argmin(separacoes_23)
    print(f"\n🌙 MELHOR MOMENTO em 23/01: {horarios_plot_23[idx_melhor_23].strftime('%H:%M')}")
    print(f"   Separação mínima: {separacoes_23[idx_melhor_23]:.2f}°")
    print(f"   Altitude Lua: {altitudes_lua_23[idx_melhor_23]:.1f}°")
    print(f"   Direção (azimute): {azimutes_lua_23[idx_melhor_23]:.1f}° "
          f"({'O' if 225 < azimutes_lua_23[idx_melhor_23] < 315 else 'SO' if 180 < azimutes_lua_23[idx_melhor_23] < 270 else 'OSO'})")

# Visualização
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Conjunção Lua-Saturno vista de Natal/RN', fontsize=16, fontweight='bold')

# Gráfico 1: Trajetória no céu - 22/01
ax1 = axes[0, 0]
ax1.plot(azimutes_lua_22, altitudes_lua_22, 'o-', label='Lua', color='gold', linewidth=2, markersize=8)
ax1.plot(azimutes_saturno_22, altitudes_saturno_22, 's-', label='Saturno', color='sandybrown', linewidth=2, markersize=6)
ax1.set_xlabel('Azimute (graus)', fontsize=11)
ax1.set_ylabel('Altitude (graus)', fontsize=11)
ax1.set_title('22 de Janeiro - Trajetória no Céu', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)
ax1.set_xlim([180, 300])
ax1.axhline(y=0, color='brown', linestyle='--', alpha=0.5, label='Horizonte')

# Gráfico 2: Separação angular ao longo do tempo - 22/01
ax2 = axes[0, 1]
horas_22 = [(h - horarios_plot_22[0]).total_seconds()/3600 for h in horarios_plot_22]
ax2.plot(horas_22, separacoes_22, 'o-', color='purple', linewidth=2, markersize=6)
ax2.set_xlabel('Tempo desde 17h (horas)', fontsize=11)
ax2.set_ylabel('Separação Angular (graus)', fontsize=11)
ax2.set_title('22 de Janeiro - Separação Lua-Saturno', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=min(separacoes_22), color='red', linestyle='--', alpha=0.5)

# Gráfico 3: Trajetória no céu - 23/01
ax3 = axes[1, 0]
ax3.plot(azimutes_lua_23, altitudes_lua_23, 'o-', label='Lua', color='gold', linewidth=2, markersize=8)
ax3.plot(azimutes_saturno_23, altitudes_saturno_23, 's-', label='Saturno', color='sandybrown', linewidth=2, markersize=6)
ax3.set_xlabel('Azimute (graus)', fontsize=11)
ax3.set_ylabel('Altitude (graus)', fontsize=11)
ax3.set_title('23 de Janeiro - Trajetória no Céu', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=10)
ax3.set_xlim([180, 300])
ax3.axhline(y=0, color='brown', linestyle='--', alpha=0.5, label='Horizonte')

# Gráfico 4: Separação angular ao longo do tempo - 23/01
ax4 = axes[1, 1]
horas_23 = [(h - horarios_plot_23[0]).total_seconds()/3600 for h in horarios_plot_23]
ax4.plot(horas_23, separacoes_23, 'o-', color='purple', linewidth=2, markersize=6)
ax4.set_xlabel('Tempo desde 17h (horas)', fontsize=11)
ax4.set_ylabel('Separação Angular (graus)', fontsize=11)
ax4.set_title('23 de Janeiro - Separação Lua-Saturno', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.axhline(y=min(separacoes_23), color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

print("\n" + "="*60)
print("DICAS DE OBSERVAÇÃO:")
print("="*60)
print("• Olhe para OESTE/SUDOESTE após o pôr do sol")
print("• Altitude baixa no céu (10-30° acima do horizonte)")
print("• Procure local com horizonte desobstruído")
print("• Lua crescente será o objeto mais brilhante")
print("• Saturno aparecerá como 'estrela' amarelada próxima à Lua")
print("• Use binóculos para ver os anéis de Saturno")
print("• Referência: azimute ~240-260° = Oeste-Sudoeste")
print("="*60)