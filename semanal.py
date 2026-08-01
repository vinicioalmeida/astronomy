# Detector semanal de eventos astronomicos para o ceu de Natal/RN
# Varre a janela dos proximos 7 dias e identifica aproximacoes (conjuncoes)
# entre Lua, planetas e estrelas brilhantes, filtrando por visibilidade real
# (altitude acima do horizonte e ceu escuro o suficiente).
#
# Para rodar toda semana, basta reexecutar o script: ele sempre parte de "hoje".

import numpy as np
import itertools
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from skyfield.api import load, wgs84, Star
from skyfield import almanac

ts = load.timescale()
eph = load('de421.bsp')
terra = eph['earth']

# Coordenadas de Natal/RN
latitude = -5.795
longitude = -35.209
natal = wgs84.latlon(latitude, longitude)
observador = terra + natal

# Janela de varredura: hoje 00h UTC ate 7 dias depois, passo de 10 minutos
inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
fim = inicio + timedelta(days=7)
passo_minutos = 10
n_passos = int((fim - inicio).total_seconds() / 60 / passo_minutos)
horarios = [inicio + timedelta(minutes=i * passo_minutos) for i in range(n_passos)]
t = ts.utc(
    [h.year for h in horarios], [h.month for h in horarios], [h.day for h in horarios],
    [h.hour for h in horarios], [h.minute for h in horarios]
)

# Catalogo de corpos a testar: nome, categoria, objeto skyfield
# Para incluir mais estrelas, basta adicionar uma linha com RA/Dec (J2000)
catalogo = []
catalogo.append(('Sol', 'sol', eph['sun']))
catalogo.append(('Lua', 'lua', eph['moon']))
catalogo.append(('Mercurio', 'planeta', eph['mercury']))
catalogo.append(('Venus', 'planeta', eph['venus']))
catalogo.append(('Marte', 'planeta', eph['mars']))
catalogo.append(('Jupiter', 'planeta', eph['jupiter barycenter']))
catalogo.append(('Saturno', 'planeta', eph['saturn barycenter']))
catalogo.append(('Urano', 'planeta', eph['uranus barycenter']))
catalogo.append(('Netuno', 'planeta', eph['neptune barycenter']))
catalogo.append(('Aldebaran', 'estrela', Star(ra_hours=(4, 35, 55.2), dec_degrees=(16, 30, 33))))
catalogo.append(('Antares', 'estrela', Star(ra_hours=(16, 29, 24.4), dec_degrees=(-26, 25, 55))))
catalogo.append(('Regulus', 'estrela', Star(ra_hours=(10, 8, 22.3), dec_degrees=(11, 58, 2))))
catalogo.append(('Spica', 'estrela', Star(ra_hours=(13, 25, 11.6), dec_degrees=(-11, 9, 41))))
catalogo.append(('Pollux', 'estrela', Star(ra_hours=(7, 45, 18.9), dec_degrees=(28, 1, 34))))
catalogo.append(('Pleiades', 'estrela', Star(ra_hours=(3, 47, 0), dec_degrees=(24, 7, 0))))

# Calcula, de uma vez (vetorizado sobre toda a grade de tempo), a posicao
# aparente de cada corpo. Guarda tambem o objeto "apparent" para usar depois
# no calculo de separacao angular verdadeira entre pares.
posicoes = {}
for nome, categoria, corpo in catalogo:
    astrometrico = observador.at(t).observe(corpo).apparent()
    alt, az, _ = astrometrico.altaz()
    posicoes[nome] = {'categoria': categoria, 'alt': alt.degrees, 'az': az.degrees, 'apparent': astrometrico}

alt_sol = posicoes['Sol']['alt']

# Corpos brilhantes o suficiente para serem vistos ainda no crepusculo civil
brilhantes = {'Lua', 'Venus', 'Jupiter', 'Mercurio'}

nomes_para_comparar = [nome for nome, categoria, corpo in catalogo if categoria != 'sol']

eventos = []

for nome_a, nome_b in itertools.combinations(nomes_para_comparar, 2):
    if posicoes[nome_a]['categoria'] == 'estrela' and posicoes[nome_b]['categoria'] == 'estrela':
        continue  # duas estrelas fixas nao formam conjuncao, a distancia entre elas nao muda

    # separacao angular verdadeira no ceu, nao a distancia euclidiana entre alt/az
    separacao = posicoes[nome_a]['apparent'].separation_from(posicoes[nome_b]['apparent']).degrees

    par_tem_corpo_brilhante = (nome_a in brilhantes) or (nome_b in brilhantes)
    limite_crepusculo = -1 if par_tem_corpo_brilhante else -12

    visivel = (posicoes[nome_a]['alt'] > 5) & (posicoes[nome_b]['alt'] > 5) & (alt_sol < limite_crepusculo)

    if not visivel.any():
        continue

    separacao_visivel = np.where(visivel, separacao, 999)
    indice_minimo = int(np.argmin(separacao_visivel))
    separacao_minima = separacao_visivel[indice_minimo]

    if separacao_minima < 15:
        fracao_lua = None
        if nome_a == 'Lua' or nome_b == 'Lua':
            fracao_lua = almanac.fraction_illuminated(eph, 'moon', t[indice_minimo])

        eventos.append({
            'par': nome_a + ' - ' + nome_b,
            'horario': horarios[indice_minimo],
            'separacao': separacao_minima,
            'alt_a': posicoes[nome_a]['alt'][indice_minimo],
            'alt_b': posicoes[nome_b]['alt'][indice_minimo],
            'az_a': posicoes[nome_a]['az'][indice_minimo],
            'az_b': posicoes[nome_b]['az'][indice_minimo],
            'fracao_lua': fracao_lua,
        })

eventos.sort(key=lambda e: e['separacao'])

print('=' * 70)
print('EVENTOS ASTRONOMICOS EM NATAL/RN')
print(inicio.strftime('%d/%m/%Y') + ' a ' + fim.strftime('%d/%m/%Y'))
print('=' * 70)

for evento in eventos:
    print('')
    print(evento['par'])
    print('Horario local (UTC-3): ' + (evento['horario'] - timedelta(hours=3)).strftime('%d/%m %H:%M'))
    print('Separacao angular: {:.1f} graus'.format(evento['separacao']))
    print('Altitude: {:.1f} / {:.1f} graus   Azimute: {:.1f} / {:.1f} graus'.format(
        evento['alt_a'], evento['alt_b'], evento['az_a'], evento['az_b']))
    if evento['fracao_lua'] is not None:
        print('Lua iluminada: {:.0f}%'.format(evento['fracao_lua'] * 100))
    if evento['separacao'] < 1:
        print('Conjuncao bem fechada, cabe no mesmo campo de um telescopio de baixo aumento')
    elif evento['separacao'] < 6:
        print('Cabe no campo de um binoculo comum')
    else:
        print('Melhor apreciado a olho nu, campo largo')

if len(eventos) == 0:
    print('Nenhum evento com separacao menor que 15 graus nesta semana')

# Grafico com a separacao angular ao longo do tempo para os 5 eventos mais fechados
top_eventos = eventos[:5]
if len(top_eventos) > 0:
    plt.figure(figsize=(10, 6))
    for evento in top_eventos:
        nome_a, nome_b = evento['par'].split(' - ')
        separacao_completa = posicoes[nome_a]['apparent'].separation_from(posicoes[nome_b]['apparent']).degrees
        horas_desde_inicio = [(h - inicio).total_seconds() / 3600 for h in horarios]
        plt.plot(horas_desde_inicio, separacao_completa, label=evento['par'])
    plt.xlabel('Horas desde ' + inicio.strftime('%d/%m 00h UTC'))
    plt.ylabel('Separacao angular (graus)')
    plt.title('Separacao angular ao longo da semana - Natal/RN')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('separacao_semanal.png', dpi=120)
    plt.show()

# Recomendacao final: separacao angular sozinha nao diz se o evento vale a pena.
# Um alvo baixo no horizonte, uma Lua muito iluminada ofuscando o campo, ou um
# objeto fraco demais para binoculo pesam contra o evento mesmo que a separacao
# seja pequena. Esta secao monta uma pontuacao simples somando essas penalidades
# (quanto menor a pontuacao, melhor a noite) e imprime a recomendacao da semana.

# magnitude aparente aproximada dos alvos nao-lunares, usada so para saber se
# o objeto e visivel a olho nu/binoculo (magnitude baixa) ou exige telescopio
# (magnitude alta). Valores tipicos, planetas variam um pouco ao longo do ano.
magnitude_aproximada = {
    'Mercurio': 0.5,
    'Venus': -4.0,
    'Marte': 0.5,
    'Jupiter': -2.2,
    'Saturno': 0.6,
    'Urano': 5.8,
    'Netuno': 7.8,
    'Aldebaran': 0.85,
    'Antares': 1.09,
    'Regulus': 1.35,
    'Spica': 0.97,
    'Pollux': 1.14,
    'Pleiades': 1.6,
}

for evento in eventos:
    nome_a, nome_b = evento['par'].split(' - ')
    altitude_minima = min(evento['alt_a'], evento['alt_b'])

    pontuacao = evento['separacao']

    if altitude_minima < 15:
        pontuacao += (15 - altitude_minima) * 0.3  # alvo baixo no horizonte penaliza

    if evento['fracao_lua'] is not None:
        pontuacao += evento['fracao_lua'] * 5  # Lua muito iluminada ofusca o campo

    if nome_a == 'Lua':
        outro_nome = nome_b
    elif nome_b == 'Lua':
        outro_nome = nome_a
    else:
        outro_nome = None

    if outro_nome is not None and outro_nome in magnitude_aproximada:
        magnitude_do_alvo = magnitude_aproximada[outro_nome]
    else:
        magnitudes_do_par = [magnitude_aproximada[n] for n in (nome_a, nome_b) if n in magnitude_aproximada]
        magnitude_do_alvo = max(magnitudes_do_par) if len(magnitudes_do_par) > 0 else None

    precisa_telescopio = magnitude_do_alvo is not None and magnitude_do_alvo > 5.5
    if precisa_telescopio:
        pontuacao += (magnitude_do_alvo - 5.5) * 2  # alvo fraco penaliza mais forte

    evento['pontuacao'] = pontuacao
    evento['precisa_telescopio'] = precisa_telescopio

eventos_recomendados = sorted(eventos, key=lambda e: e['pontuacao'])

print('')
print('=' * 70)
print('RECOMENDACAO DA SEMANA')
print('=' * 70)

if len(eventos_recomendados) > 0:
    melhor = eventos_recomendados[0]
    print('')
    print('Melhor opcao: ' + melhor['par'])
    print('Horario local (UTC-3): ' + (melhor['horario'] - timedelta(hours=3)).strftime('%d/%m %H:%M'))
    print('Separacao: {:.1f} graus, altitude minima: {:.1f} graus'.format(
        melhor['separacao'], min(melhor['alt_a'], melhor['alt_b'])))
    if melhor['fracao_lua'] is not None:
        print('Lua com {:.0f}% de iluminacao nesse horario'.format(melhor['fracao_lua'] * 100))
    if melhor['precisa_telescopio']:
        print('Um dos alvos e fraco, o binoculo pode nao ser suficiente, telescopio ajuda bastante aqui')
    else:
        print('Boa combinacao de altura, separacao e brilho, deve ficar bem visivel em binoculo ou olho nu')

    print('')
    print('Outras opcoes da semana, da mais recomendada para a menos recomendada:')
    for evento in eventos_recomendados[1:6]:
        aviso = ' (provavelmente precisa de telescopio)' if evento['precisa_telescopio'] else ''
        horario_local = (evento['horario'] - timedelta(hours=3)).strftime('%d/%m %H:%M')
        print('  ' + evento['par'] + ' em ' + horario_local + aviso)
else:
    print('Nenhum evento recomendavel encontrado nesta semana')