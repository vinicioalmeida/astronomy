# Análise completa dos eventos astronômicos em Natal/RN
# Semana de 27 de janeiro a 1 de fevereiro de 2026

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from skyfield.api import load, wgs84, Star
from skyfield import almanac

# Carregar dados astronômicos
ts = load.timescale()
eph = load('de421.bsp')
terra = eph['earth']
lua = eph['moon']
jupiter = eph['jupiter barycenter']
venus = eph['venus']
mercury = eph['mercury']
sol = eph['sun']

# Coordenadas de Natal/RN
latitude = -5.795
longitude = -35.209
natal = wgs84.latlon(latitude, longitude)

# Definir estrelas fixas usando coordenadas
# Aldebaran: RA 04h 35m 55s, Dec +16° 30' 33"
aldebaran = Star(ra_hours=(4, 35, 55.2), dec_degrees=(16, 30, 33))

# Plêiades (centro aproximado): RA 03h 47m, Dec +24° 07'
pleiades = Star(ra_hours=(3, 47, 0), dec_degrees=(24, 7, 0))

print("="*70)
print("EVENTOS ASTRONÔMICOS EM NATAL/RN - 27 JAN A 1 FEV 2026")
print("="*70)

# Criar datas para análise
datas = []
for dia in range(27, 32):  # 27 a 31 de janeiro
    datas.append(datetime(2026, 1, dia))
datas.append(datetime(2026, 2, 1))  # 1 de fevereiro

# Horários de observação: 17h às 6h do dia seguinte
horarios_completos = []
for data_base in datas:
    for hora in range(17, 24):
        for minuto in range(0, 60, 15):
            horarios_completos.append(data_base + timedelta(hours=hora, minutes=minuto))
    # Adicionar madrugada (0h às 6h do dia seguinte)
    for hora in range(0, 7):
        for minuto in range(0, 60, 15):
            horarios_completos.append(data_base + timedelta(days=1, hours=hora, minutes=minuto))

# Estruturas para armazenar dados
dados_eventos = {
    '27_jan_lua_pleiades': {'horarios': [], 'alt_lua': [], 'az_lua': [], 'alt_obj': [], 'az_obj': [], 'sep': []},
    '27_jan_lua_urano': {'horarios': [], 'alt_lua': [], 'az_lua': [], 'alt_obj': [], 'az_obj': [], 'sep': []},
    '28_jan_lua_aldebaran': {'horarios': [], 'alt_lua': [], 'az_lua': [], 'alt_obj': [], 'az_obj': [], 'sep': []},
    '29_jan_venus_mercurio': {'horarios': [], 'alt_venus': [], 'az_venus': [], 'alt_merc': [], 'az_merc': [], 'sep': []},
    '30_31_jan_lua_jupiter': {'horarios': [], 'alt_lua': [], 'az_lua': [], 'alt_jup': [], 'az_jup': [], 'sep': []}
}

# Processar cada horário
for horario in horarios_completos:
    t = ts.utc(horario.year, horario.month, horario.day, horario.hour, horario.minute)
    observador = terra + natal
    
    # Calcular posição do Sol para saber se é dia ou noite
    alt_sol = observador.at(t).observe(sol).apparent().altaz()[0].degrees
    
    # Lua
    astr_lua = observador.at(t).observe(lua)
    alt_lua, az_lua, _ = astr_lua.apparent().altaz()
    alt_lua = alt_lua.degrees
    az_lua = az_lua.degrees
    
    # Júpiter
    astr_jup = observador.at(t).observe(jupiter)
    alt_jup, az_jup, _ = astr_jup.apparent().altaz()
    alt_jup = alt_jup.degrees
    az_jup = az_jup.degrees
    
    # Vênus
    astr_venus = observador.at(t).observe(venus)
    alt_venus, az_venus, _ = astr_venus.apparent().altaz()
    alt_venus = alt_venus.degrees
    az_venus = az_venus.degrees
    
    # Mercúrio
    astr_merc = observador.at(t).observe(mercury)
    alt_merc, az_merc, _ = astr_merc.apparent().altaz()
    alt_merc = alt_merc.degrees
    az_merc = az_merc.degrees
    
    # Aldebaran
    astr_ald = observador.at(t).observe(aldebaran)
    alt_ald, az_ald, _ = astr_ald.apparent().altaz()
    alt_ald = alt_ald.degrees
    az_ald = az_ald.degrees
    
    # Plêiades
    astr_plei = observador.at(t).observe(pleiades)
    alt_plei, az_plei, _ = astr_plei.apparent().altaz()
    alt_plei = alt_plei.degrees
    az_plei = az_plei.degrees
    
    # 27 de janeiro - Lua e Plêiades
    if horario.day == 27 and horario.month == 1:
        if alt_lua > 0 and alt_plei > 0 and alt_sol < -6:  # Crepúsculo náutico
            sep_lp = np.sqrt((az_lua - az_plei)**2 + (alt_lua - alt_plei)**2)
            dados_eventos['27_jan_lua_pleiades']['horarios'].append(horario)
            dados_eventos['27_jan_lua_pleiades']['alt_lua'].append(alt_lua)
            dados_eventos['27_jan_lua_pleiades']['az_lua'].append(az_lua)
            dados_eventos['27_jan_lua_pleiades']['alt_obj'].append(alt_plei)
            dados_eventos['27_jan_lua_pleiades']['az_obj'].append(az_plei)
            dados_eventos['27_jan_lua_pleiades']['sep'].append(sep_lp)
    
    # 28 de janeiro - Lua e Aldebaran
    if horario.day == 28 and horario.month == 1:
        if alt_lua > 0 and alt_ald > 0 and alt_sol < -6:
            sep_la = np.sqrt((az_lua - az_ald)**2 + (alt_lua - alt_ald)**2)
            dados_eventos['28_jan_lua_aldebaran']['horarios'].append(horario)
            dados_eventos['28_jan_lua_aldebaran']['alt_lua'].append(alt_lua)
            dados_eventos['28_jan_lua_aldebaran']['az_lua'].append(az_lua)
            dados_eventos['28_jan_lua_aldebaran']['alt_obj'].append(alt_ald)
            dados_eventos['28_jan_lua_aldebaran']['az_obj'].append(az_ald)
            dados_eventos['28_jan_lua_aldebaran']['sep'].append(sep_la)
    
    # 29 de janeiro - Vênus e Mercúrio
    if horario.day == 29 and horario.month == 1:
        if alt_venus > 0 and alt_merc > 0 and -12 < alt_sol < -1:  # Crepúsculo
            sep_vm = np.sqrt((az_venus - az_merc)**2 + (alt_venus - alt_merc)**2)
            dados_eventos['29_jan_venus_mercurio']['horarios'].append(horario)
            dados_eventos['29_jan_venus_mercurio']['alt_venus'].append(alt_venus)
            dados_eventos['29_jan_venus_mercurio']['az_venus'].append(az_venus)
            dados_eventos['29_jan_venus_mercurio']['alt_merc'].append(alt_merc)
            dados_eventos['29_jan_venus_mercurio']['az_merc'].append(az_merc)
            dados_eventos['29_jan_venus_mercurio']['sep'].append(sep_vm)
    
    # 30-31 de janeiro - Lua e Júpiter (toda a noite)
    if (horario.day == 30 and horario.month == 1) or (horario.day == 31 and horario.month == 1 and horario.hour < 12):
        if alt_lua > 0 and alt_jup > 0:
            sep_lj = np.sqrt((az_lua - az_jup)**2 + (alt_lua - alt_jup)**2)
            dados_eventos['30_31_jan_lua_jupiter']['horarios'].append(horario)
            dados_eventos['30_31_jan_lua_jupiter']['alt_lua'].append(alt_lua)
            dados_eventos['30_31_jan_lua_jupiter']['az_lua'].append(az_lua)
            dados_eventos['30_31_jan_lua_jupiter']['alt_jup'].append(alt_jup)
            dados_eventos['30_31_jan_lua_jupiter']['az_jup'].append(az_jup)
            dados_eventos['30_31_jan_lua_jupiter']['sep'].append(sep_lj)

# Análise e impressão dos resultados
print("\n27 DE JANEIRO - LUA E PLÊIADES")
print("-"*70)
if len(dados_eventos['27_jan_lua_pleiades']['sep']) > 0:
    idx_melhor = np.argmin(dados_eventos['27_jan_lua_pleiades']['sep'])
    melhor_hora = dados_eventos['27_jan_lua_pleiades']['horarios'][idx_melhor]
    print(f"Melhor horário: {melhor_hora.strftime('%H:%M')}")
    print(f"Separação: {dados_eventos['27_jan_lua_pleiades']['sep'][idx_melhor]:.1f}°")
    print(f"Altitude Lua: {dados_eventos['27_jan_lua_pleiades']['alt_lua'][idx_melhor]:.1f}°")
    print(f"Azimute: {dados_eventos['27_jan_lua_pleiades']['az_lua'][idx_melhor]:.1f}° (Oeste)")
    print("Dica: Use binóculos para ver o aglomerado completo junto à Lua")
    
    # Mostrar horários a cada hora
    print("\nPosições horárias:")
    for i, h in enumerate(dados_eventos['27_jan_lua_pleiades']['horarios']):
        if h.minute == 0:
            print(f"  {h.strftime('%H:%M')} - Alt Lua: {dados_eventos['27_jan_lua_pleiades']['alt_lua'][i]:5.1f}° "
                  f"Az: {dados_eventos['27_jan_lua_pleiades']['az_lua'][i]:6.1f}° Sep: {dados_eventos['27_jan_lua_pleiades']['sep'][i]:5.1f}°")

print("\n28 DE JANEIRO - LUA E ALDEBARAN")
print("-"*70)
if len(dados_eventos['28_jan_lua_aldebaran']['sep']) > 0:
    idx_melhor = np.argmin(dados_eventos['28_jan_lua_aldebaran']['sep'])
    melhor_hora = dados_eventos['28_jan_lua_aldebaran']['horarios'][idx_melhor]
    print(f"Melhor horário: {melhor_hora.strftime('%H:%M')}")
    print(f"Separação: {dados_eventos['28_jan_lua_aldebaran']['sep'][idx_melhor]:.1f}°")
    print(f"Altitude Lua: {dados_eventos['28_jan_lua_aldebaran']['alt_lua'][idx_melhor]:.1f}°")
    print(f"Azimute: {dados_eventos['28_jan_lua_aldebaran']['az_lua'][idx_melhor]:.1f}° (Oeste-Noroeste)")
    print("Dica: Aldebaran é a estrela alaranjada, olho do Touro. Visível a olho nu.")
    
    print("\nPosições horárias:")
    for i, h in enumerate(dados_eventos['28_jan_lua_aldebaran']['horarios']):
        if h.minute == 0:
            print(f"  {h.strftime('%H:%M')} - Alt Lua: {dados_eventos['28_jan_lua_aldebaran']['alt_lua'][i]:5.1f}° "
                  f"Az: {dados_eventos['28_jan_lua_aldebaran']['az_lua'][i]:6.1f}° Sep: {dados_eventos['28_jan_lua_aldebaran']['sep'][i]:5.1f}°")

print("\n29 DE JANEIRO - VÊNUS E MERCÚRIO")
print("-"*70)
if len(dados_eventos['29_jan_venus_mercurio']['sep']) > 0:
    idx_melhor = np.argmin(dados_eventos['29_jan_venus_mercurio']['sep'])
    melhor_hora = dados_eventos['29_jan_venus_mercurio']['horarios'][idx_melhor]
    print(f"Melhor horário: {melhor_hora.strftime('%H:%M')}")
    print(f"Separação: {dados_eventos['29_jan_venus_mercurio']['sep'][idx_melhor]:.1f}°")
    print(f"Altitude Vênus: {dados_eventos['29_jan_venus_mercurio']['alt_venus'][idx_melhor]:.1f}°")
    print(f"Azimute: {dados_eventos['29_jan_venus_mercurio']['az_venus'][idx_melhor]:.1f}° (Oeste)")
    print("Dica: Observe logo após pôr do sol. Vênus é muito brilhante. Mercúrio mais fraco.")
    print("      Precisa horizonte oeste limpo!")
    
    print("\nPosições no crepúsculo (a cada 15 min):")
    for i, h in enumerate(dados_eventos['29_jan_venus_mercurio']['horarios']):
        print(f"  {h.strftime('%H:%M')} - Alt Vênus: {dados_eventos['29_jan_venus_mercurio']['alt_venus'][i]:5.1f}° "
              f"Alt Merc: {dados_eventos['29_jan_venus_mercurio']['alt_merc'][i]:5.1f}° "
              f"Az: {dados_eventos['29_jan_venus_mercurio']['az_venus'][i]:6.1f}° Sep: {dados_eventos['29_jan_venus_mercurio']['sep'][i]:4.1f}°")

print("\n30-31 DE JANEIRO - LUA E JÚPITER")
print("-"*70)
if len(dados_eventos['30_31_jan_lua_jupiter']['sep']) > 0:
    idx_melhor = np.argmin(dados_eventos['30_31_jan_lua_jupiter']['sep'])
    melhor_hora = dados_eventos['30_31_jan_lua_jupiter']['horarios'][idx_melhor]
    print(f"Melhor horário: {melhor_hora.strftime('%d/%m %H:%M')}")
    print(f"Separação mínima: {dados_eventos['30_31_jan_lua_jupiter']['sep'][idx_melhor]:.1f}°")
    print(f"Altitude Lua: {dados_eventos['30_31_jan_lua_jupiter']['alt_lua'][idx_melhor]:.1f}°")
    print(f"Azimute: {dados_eventos['30_31_jan_lua_jupiter']['az_jup'][idx_melhor]:.1f}°")
    print("Dica: Evento visível toda a noite! Júpiter aparece como 'estrela' brilhante.")
    print("      Use telescópio para ver luas galileanas e faixas de Júpiter.")
    
    print("\nPosições ao longo da noite:")
    for i, h in enumerate(dados_eventos['30_31_jan_lua_jupiter']['horarios']):
        if h.minute == 0:
            print(f"  {h.strftime('%d/%m %H:%M')} - Alt Lua: {dados_eventos['30_31_jan_lua_jupiter']['alt_lua'][i]:5.1f}° "
                  f"Alt Jup: {dados_eventos['30_31_jan_lua_jupiter']['alt_jup'][i]:5.1f}° "
                  f"Az: {dados_eventos['30_31_jan_lua_jupiter']['az_lua'][i]:6.1f}° "
                  f"Sep: {dados_eventos['30_31_jan_lua_jupiter']['sep'][i]:5.1f}°")

# Criar visualizações
fig = plt.figure(figsize=(16, 12))

# Gráfico 1: Lua e Plêiades (27 jan)
ax1 = plt.subplot(3, 2, 1)
if len(dados_eventos['27_jan_lua_pleiades']['az_lua']) > 0:
    ax1.plot(dados_eventos['27_jan_lua_pleiades']['az_lua'], 
             dados_eventos['27_jan_lua_pleiades']['alt_lua'], 
             'o-', color='gold', linewidth=2, markersize=10, label='Lua')
    ax1.plot(dados_eventos['27_jan_lua_pleiades']['az_obj'], 
             dados_eventos['27_jan_lua_pleiades']['alt_obj'], 
             's-', color='lightblue', linewidth=2, markersize=6, label='Plêiades')
ax1.set_xlabel('Azimute (graus)', fontsize=10)
ax1.set_ylabel('Altitude (graus)', fontsize=10)
ax1.set_title('27 Jan - Lua e Plêiades', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.axhline(y=0, color='brown', linestyle='--', alpha=0.5)

# Gráfico 2: Separação Lua-Plêiades
ax2 = plt.subplot(3, 2, 2)
if len(dados_eventos['27_jan_lua_pleiades']['sep']) > 0:
    horas = [(h - dados_eventos['27_jan_lua_pleiades']['horarios'][0]).total_seconds()/3600 
             for h in dados_eventos['27_jan_lua_pleiades']['horarios']]
    ax2.plot(horas, dados_eventos['27_jan_lua_pleiades']['sep'], 
             'o-', color='purple', linewidth=2, markersize=5)
ax2.set_xlabel('Horas desde início observação', fontsize=10)
ax2.set_ylabel('Separação Angular (graus)', fontsize=10)
ax2.set_title('27 Jan - Separação Lua-Plêiades', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Gráfico 3: Lua e Aldebaran (28 jan)
ax3 = plt.subplot(3, 2, 3)
if len(dados_eventos['28_jan_lua_aldebaran']['az_lua']) > 0:
    ax3.plot(dados_eventos['28_jan_lua_aldebaran']['az_lua'], 
             dados_eventos['28_jan_lua_aldebaran']['alt_lua'], 
             'o-', color='gold', linewidth=2, markersize=10, label='Lua')
    ax3.plot(dados_eventos['28_jan_lua_aldebaran']['az_obj'], 
             dados_eventos['28_jan_lua_aldebaran']['alt_obj'], 
             's-', color='orangered', linewidth=2, markersize=6, label='Aldebaran')
ax3.set_xlabel('Azimute (graus)', fontsize=10)
ax3.set_ylabel('Altitude (graus)', fontsize=10)
ax3.set_title('28 Jan - Lua e Aldebaran', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()
ax3.axhline(y=0, color='brown', linestyle='--', alpha=0.5)

# Gráfico 4: Vênus e Mercúrio (29 jan)
ax4 = plt.subplot(3, 2, 4)
if len(dados_eventos['29_jan_venus_mercurio']['az_venus']) > 0:
    ax4.plot(dados_eventos['29_jan_venus_mercurio']['az_venus'], 
             dados_eventos['29_jan_venus_mercurio']['alt_venus'], 
             'o-', color='yellow', linewidth=2, markersize=10, label='Vênus')
    ax4.plot(dados_eventos['29_jan_venus_mercurio']['az_merc'], 
             dados_eventos['29_jan_venus_mercurio']['alt_merc'], 
             's-', color='gray', linewidth=2, markersize=6, label='Mercúrio')
ax4.set_xlabel('Azimute (graus)', fontsize=10)
ax4.set_ylabel('Altitude (graus)', fontsize=10)
ax4.set_title('29 Jan - Vênus e Mercúrio (Crepúsculo)', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()
ax4.axhline(y=0, color='brown', linestyle='--', alpha=0.5)

# Gráfico 5: Lua e Júpiter - Trajetória (30-31 jan)
ax5 = plt.subplot(3, 2, 5)
if len(dados_eventos['30_31_jan_lua_jupiter']['az_lua']) > 0:
    ax5.plot(dados_eventos['30_31_jan_lua_jupiter']['az_lua'], 
             dados_eventos['30_31_jan_lua_jupiter']['alt_lua'], 
             'o-', color='gold', linewidth=2, markersize=8, label='Lua')
    ax5.plot(dados_eventos['30_31_jan_lua_jupiter']['az_jup'], 
             dados_eventos['30_31_jan_lua_jupiter']['alt_jup'], 
             's-', color='orange', linewidth=2, markersize=6, label='Júpiter')
ax5.set_xlabel('Azimute (graus)', fontsize=10)
ax5.set_ylabel('Altitude (graus)', fontsize=10)
ax5.set_title('30-31 Jan - Lua e Júpiter (Noite Toda)', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.legend()
ax5.axhline(y=0, color='brown', linestyle='--', alpha=0.5)

# Gráfico 6: Separação Lua-Júpiter ao longo do tempo
ax6 = plt.subplot(3, 2, 6)
if len(dados_eventos['30_31_jan_lua_jupiter']['sep']) > 0:
    horas = [(h - dados_eventos['30_31_jan_lua_jupiter']['horarios'][0]).total_seconds()/3600 
             for h in dados_eventos['30_31_jan_lua_jupiter']['horarios']]
    ax6.plot(horas, dados_eventos['30_31_jan_lua_jupiter']['sep'], 
             'o-', color='purple', linewidth=2, markersize=5)
    ax6.axhline(y=min(dados_eventos['30_31_jan_lua_jupiter']['sep']), 
                color='red', linestyle='--', alpha=0.5, label='Separação mínima')
ax6.set_xlabel('Horas desde início (30/jan 17h)', fontsize=10)
ax6.set_ylabel('Separação Angular (graus)', fontsize=10)
ax6.set_title('30-31 Jan - Separação Lua-Júpiter', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)
ax6.legend()

plt.tight_layout()
plt.show()

print("\n" + "="*70)
print("RESUMO DA SEMANA")
print("="*70)
print("27 Jan: Lua + Plêiades (início da noite, oeste)")
print("28 Jan: Lua + Aldebaran (início da noite, oeste-noroeste)")
print("29 Jan: Vênus + Mercúrio (crepúsculo, oeste - HORIZONTE LIMPO!)")
print("30-31 Jan: Lua + Júpiter (TODA A NOITE - melhor evento!)")
print("\nTodos os eventos visíveis de Natal sem instrumentos especiais.")
print("Binóculos melhoram muito a experiência, telescópio revela detalhes.")
print("="*70)