# Detector semanal de eventos astronomicos para o ceu de Natal/RN
# Varre a janela dos proximos 7 dias, identifica aproximacoes (conjuncoes)
# entre Lua, planetas, estrelas, aglomerados e objetos de ceu profundo,
# calcula um indice de qualidade de observacao para cada evento, agrupa os
# alvos por tipo de sessao e monta um roteiro para a melhor noite da semana.

import os
import numpy as np
import itertools
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from skyfield.api import Loader, wgs84, Star
from skyfield import almanac

pasta_saida = r'C:\repo\astronomy'

carrega = Loader(pasta_saida)
ts = carrega.timescale()
eph = carrega('de421.bsp')
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

# Catalogo de corpos a testar: nome, categoria, objeto skyfield.
# A categoria serve tanto para decidir quais pares comparar quanto para
# classificar o tipo de sessao: sol, lua, planeta, estrela (referencia),
# aglomerado (bom para binoculo) e profundo (ceu profundo, Messier).
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
catalogo.append(('Albireo', 'estrela', Star(ra_hours=(19, 30, 43.3), dec_degrees=(27, 57, 35))))
catalogo.append(('Pleiades', 'aglomerado', Star(ra_hours=(3, 47, 0), dec_degrees=(24, 7, 0))))
catalogo.append(('Hyades', 'aglomerado', Star(ra_hours=(4, 27, 0), dec_degrees=(15, 52, 0))))
catalogo.append(('M8', 'profundo', Star(ra_hours=(18, 3, 48), dec_degrees=(-24, 23, 12))))
catalogo.append(('M22', 'profundo', Star(ra_hours=(18, 36, 24), dec_degrees=(-23, 54, 12))))
catalogo.append(('M13', 'profundo', Star(ra_hours=(16, 41, 42), dec_degrees=(36, 28, 12))))
catalogo.append(('M31', 'profundo', Star(ra_hours=(0, 42, 44), dec_degrees=(41, 16, 9))))

# Magnitude aparente aproximada dos alvos nao-lunares. Usada para estimar a
# facilidade de observacao (componente "magnitude" do indice de qualidade) e
# para separar sessoes de iniciante de sessoes de desafio.
magnitude_aproximada = {
    'Mercurio': 0.5, 'Venus': -4.0, 'Marte': 0.5, 'Jupiter': -2.2, 'Saturno': 0.6,
    'Urano': 5.8, 'Netuno': 7.8,
    'Aldebaran': 0.85, 'Antares': 1.09, 'Regulus': 1.35, 'Spica': 0.97, 'Pollux': 1.14,
    'Albireo': 3.1, 'Pleiades': 1.6, 'Hyades': 0.5,
    'M8': 6.0, 'M22': 5.1, 'M13': 5.8, 'M31': 3.4,
}

# Calcula, de uma vez (vetorizado sobre toda a grade de tempo), a posicao
# aparente de cada corpo do catalogo.
posicoes = {}
for nome, categoria, corpo in catalogo:
    astrometrico = observador.at(t).observe(corpo).apparent()
    alt, az, _ = astrometrico.altaz()
    posicoes[nome] = {'categoria': categoria, 'alt': alt.degrees, 'az': az.degrees, 'apparent': astrometrico}

alt_sol = posicoes['Sol']['alt']
brilhantes = {'Lua', 'Venus', 'Jupiter', 'Mercurio'}
fixos = {'estrela', 'aglomerado', 'profundo'}  # categorias cuja posicao relativa entre si nao muda

nomes_para_comparar = [nome for nome, categoria, corpo in catalogo if categoria != 'sol']

eventos = []

for nome_a, nome_b in itertools.combinations(nomes_para_comparar, 2):
    if posicoes[nome_a]['categoria'] in fixos and posicoes[nome_b]['categoria'] in fixos:
        continue  # dois objetos fixos nunca formam conjuncao, a distancia entre eles nao muda

    separacao = posicoes[nome_a]['apparent'].separation_from(posicoes[nome_b]['apparent']).degrees

    par_tem_corpo_brilhante = (nome_a in brilhantes) or (nome_b in brilhantes)
    limite_crepusculo = -1 if par_tem_corpo_brilhante else -12

    visivel = (posicoes[nome_a]['alt'] > 5) & (posicoes[nome_b]['alt'] > 5) & (alt_sol < limite_crepusculo)

    if not visivel.any():
        continue

    separacao_visivel = np.where(visivel, separacao, 999)
    indice_minimo = int(np.argmin(separacao_visivel))
    separacao_minima = separacao_visivel[indice_minimo]

    if separacao_minima >= 15:
        continue

    alt_a = posicoes[nome_a]['alt'][indice_minimo]
    alt_b = posicoes[nome_b]['alt'][indice_minimo]
    altitude_media = (alt_a + alt_b) / 2
    altitude_minima = min(alt_a, alt_b)

    fracao_lua = None
    if nome_a == 'Lua' or nome_b == 'Lua':
        fracao_lua = almanac.fraction_illuminated(eph, 'moon', t[indice_minimo])

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

    tempo_acima_30 = np.sum(
        visivel & (posicoes[nome_a]['alt'] > 30) & (posicoes[nome_b]['alt'] > 30)
    ) * passo_minutos / 60

    # Indice de qualidade da observacao, de 0 a 100, seguindo a ponderacao
    # altitude 0,35 + ausencia da Lua 0,25 + magnitude 0,15 + tempo acima de
    # 30 graus 0,15 + distancia do horizonte 0,10. Seeing, cobertura de
    # nuvens, transparencia, umidade e vento nao entram ainda porque exigem
    # uma previsao meteorologica ao vivo (por exemplo via Open-Meteo), o que
    # fica bem como proximo passo separado deste script.
    altitude_norm = min(altitude_media / 90, 1)
    ausencia_lua = 1 - fracao_lua if fracao_lua is not None else 1
    magnitude_norm = min(max((8 - magnitude_do_alvo) / 12, 0), 1) if magnitude_do_alvo is not None else 0.5
    tempo_norm = min(tempo_acima_30 / 5, 1)
    horizonte_norm = min(max(altitude_minima / 45, 0), 1)

    score = 100 * (
        0.35 * altitude_norm +
        0.25 * ausencia_lua +
        0.15 * magnitude_norm +
        0.15 * tempo_norm +
        0.10 * horizonte_norm
    )

    eventos.append({
        'par': nome_a + ' - ' + nome_b,
        'horario': horarios[indice_minimo],
        'separacao': separacao_minima,
        'alt_a': alt_a, 'alt_b': alt_b,
        'az_a': posicoes[nome_a]['az'][indice_minimo], 'az_b': posicoes[nome_b]['az'][indice_minimo],
        'fracao_lua': fracao_lua,
        'precisa_telescopio': precisa_telescopio,
        'score': score,
    })

eventos.sort(key=lambda e: e['score'], reverse=True)

print('=' * 70)
print('EVENTOS ASTRONOMICOS EM NATAL/RN')
print(inicio.strftime('%d/%m/%Y') + ' a ' + fim.strftime('%d/%m/%Y'))
print('=' * 70)

for evento in eventos:
    print('')
    print(evento['par'])
    print('Horario local (UTC-3): ' + (evento['horario'] - timedelta(hours=3)).strftime('%d/%m %H:%M'))
    print('Separacao angular: {:.1f} graus   Indice de qualidade: {:.1f}'.format(
        evento['separacao'], evento['score']))
    print('Altitude: {:.1f} / {:.1f} graus   Azimute: {:.1f} / {:.1f} graus'.format(
        evento['alt_a'], evento['alt_b'], evento['az_a'], evento['az_b']))
    if evento['fracao_lua'] is not None:
        print('Lua iluminada: {:.0f}%'.format(evento['fracao_lua'] * 100))
    if evento['precisa_telescopio']:
        print('Alvo fraco, o binoculo pode nao ser suficiente, telescopio ajuda bastante aqui')

if len(eventos) == 0:
    print('Nenhum evento com separacao menor que 15 graus nesta semana')

# Grafico com a separacao angular ao longo do tempo para os 5 eventos de maior indice de qualidade
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
    plt.savefig(os.path.join(pasta_saida, 'separacao_semanal.png'), dpi=120)
    plt.show()

# Painel da melhor noite da semana, no estilo "Observatorio Almeida"
if len(eventos) > 0:
    melhor_evento = eventos[0]
    horario_local_melhor = melhor_evento['horario'] - timedelta(hours=3)
    # um evento de madrugada (antes do meio-dia local) pertence a noite que
    # comecou no dia anterior, entao a data da noite recua um dia nesse caso
    if horario_local_melhor.hour < 12:
        noite_data = (horario_local_melhor - timedelta(days=1)).date()
    else:
        noite_data = horario_local_melhor.date()

    objetos_da_noite = []
    for evento in eventos:
        horario_local_evento = evento['horario'] - timedelta(hours=3)
        if horario_local_evento.hour < 12:
            data_evento = (horario_local_evento - timedelta(days=1)).date()
        else:
            data_evento = horario_local_evento.date()
        if data_evento == noite_data:
            for nome_obj in evento['par'].split(' - '):
                if nome_obj not in objetos_da_noite:
                    objetos_da_noite.append(nome_obj)

    classificacao = min(5, max(1, round(melhor_evento['score'] / 20)))

    print('')
    print('=' * 70)
    print('OBSERVATORIO ALMEIDA')
    print('=' * 70)
    print('Noite da semana: ' + noite_data.strftime('%d/%m') + ' para ' + (noite_data + timedelta(days=1)).strftime('%d/%m'))
    print('Classificacao: ' + '*' * classificacao + '.' * (5 - classificacao) + ' (' + str(classificacao) + '/5)')
    print('Objetos:')
    for nome_obj in objetos_da_noite:
        print('  ' + nome_obj)
    print('Score: {:.1f}'.format(melhor_evento['score']))

# Classificacao das sessoes: agrupa o catalogo por tipo de alvo e por dificuldade
sessao_planetaria = [nome for nome, categoria, corpo in catalogo if categoria in ('planeta', 'lua')]
sessao_ceu_profundo = [nome for nome, categoria, corpo in catalogo if categoria == 'profundo']
sessao_binoculo = [nome for nome, categoria, corpo in catalogo if categoria == 'aglomerado']

iniciantes = []
desafio = []
for nome, categoria, corpo in catalogo:
    if categoria == 'sol':
        continue
    if nome == 'Lua':
        iniciantes.append(nome)
        continue
    magnitude_nome = magnitude_aproximada.get(nome)
    if magnitude_nome is not None and magnitude_nome <= 3.0:
        iniciantes.append(nome)
    elif magnitude_nome is not None:
        desafio.append(nome)

print('')
print('=' * 70)
print('SESSOES DE OBSERVACAO')
print('=' * 70)
print('Sessao Planetaria')
for nome_obj in sessao_planetaria:
    print('  ' + nome_obj)
print('Ceu Profundo')
for nome_obj in sessao_ceu_profundo:
    print('  ' + nome_obj)
print('Binoculo')
for nome_obj in sessao_binoculo:
    print('  ' + nome_obj)
print('Iniciantes')
for nome_obj in iniciantes:
    print('  ' + nome_obj)
print('Desafio')
for nome_obj in desafio:
    print('  ' + nome_obj)

# Roteiro de observacao para a melhor noite da semana: varre a janela escura
# dessa noite em passos de 30 minutos e, a cada passo, aloca o alvo ainda nao
# observado que estiver mais alto no ceu naquele momento, acima de 25 graus.
# inicio_noite e fim_noite ja saem em horario UTC (mesma referencia de
# "horarios") porque somamos 3 horas ao horario local desejado.
if len(eventos) > 0:
    inicio_noite = datetime(noite_data.year, noite_data.month, noite_data.day, 18, 0) + timedelta(hours=3)
    fim_noite = inicio_noite + timedelta(hours=12)

    indices_noite = [i for i, h in enumerate(horarios) if inicio_noite <= h < fim_noite and alt_sol[i] < -12]
    indices_slots = indices_noite[::3]  # um slot a cada 30 minutos (passo original de 10 min)

    ja_observados = set()
    roteiro = []
    for indice in indices_slots:
        candidatos = [
            nome for nome in nomes_para_comparar
            if nome not in ja_observados and posicoes[nome]['alt'][indice] > 25
        ]
        if len(candidatos) == 0:
            continue
        alturas_candidatos = [posicoes[nome]['alt'][indice] for nome in candidatos]
        escolhido = candidatos[int(np.argmax(alturas_candidatos))]
        ja_observados.add(escolhido)
        hora_local = (horarios[indice] - timedelta(hours=3)).strftime('%H:%M')
        roteiro.append((hora_local, escolhido))
        if len(roteiro) >= 8:
            break

    print('')
    print('=' * 70)
    print('ROTEIRO DA NOITE - ' + noite_data.strftime('%d/%m') + ' para ' + (noite_data + timedelta(days=1)).strftime('%d/%m'))
    print('=' * 70)
    if len(roteiro) > 0:
        for indice_item, (hora_local, nome_obj) in enumerate(roteiro):
            print(hora_local + '  ' + nome_obj)
            if indice_item < len(roteiro) - 1:
                print('   |')
                print('   v')
    else:
        print('Nao foi possivel montar um roteiro para essa noite')