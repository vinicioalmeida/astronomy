# Observatorio Primeira Luz - painel Streamlit
# Dois modos de uso:
#   1) Panorama dos proximos dias: eventos (aproximacoes entre Lua, planetas e
#      alvos de ceu profundo), indice de qualidade e melhor noite do periodo.
#   2) Planejar uma noite: voce escolhe a data e o local e recebe o plano
#      completo da noite (horarios do Sol e da Lua, alvos visiveis, roteiro com
#      horarios, mapa do ceu e altura dos alvos ao longo da noite).
#
# Para rodar localmente: streamlit run observatorio_primeira_luz.py
# Para publicar: subir este arquivo e o requirements.txt para o repositorio
# conectado ao Streamlit Cloud.

import os
import itertools
from operator import itemgetter
from datetime import datetime, timedelta, timezone, date

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from skyfield.api import Loader, wgs84, Star
from skyfield import almanac

st.set_page_config(page_title='Observatório Primeira Luz', layout='wide')

# Pasta de dados: usa a pasta onde este arquivo esta salvo, para funcionar
# tanto rodando localmente quanto publicado no Streamlit Cloud.
pasta_dados = os.path.dirname(os.path.abspath(__file__))

# O servidor do Streamlit Cloud roda em UTC. Todo calculo de "hoje" usa o
# horario local (UTC-3, sem horario de verao), senao depois das 21h o app
# pularia para o dia seguinte.
fuso = timedelta(hours=3)
agora_local = datetime.now(timezone.utc).replace(tzinfo=None) - fuso
hoje_local = agora_local.date()

pontos_cardeais = ['Norte', 'Nordeste', 'Leste', 'Sudeste', 'Sul', 'Sudoeste', 'Oeste', 'Noroeste']
siglas_cardeais = ['N', 'NE', 'L', 'SE', 'S', 'SO', 'O', 'NO']

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
st.sidebar.header('Modo')
modo = st.sidebar.radio('O que você quer ver', ['Panorama dos próximos dias', 'Planejar uma noite'])
modo_panorama = modo == 'Panorama dos próximos dias'

st.sidebar.header('Local')
locais = {
    'Natal/RN': (-5.795, -35.209),
    'São Miguel do Gostoso/RN (Urca do Tubarão)': (-5.1372, -35.5679),
    'Outro local': None,
}
nome_local = st.sidebar.selectbox('Local de observação', list(locais.keys()))
if locais[nome_local] is None:
    latitude = st.sidebar.number_input('Latitude (graus, sul negativo)', value=-5.795, min_value=-90.0, max_value=90.0, format='%.4f')
    longitude = st.sidebar.number_input('Longitude (graus, oeste negativo)', value=-35.209, min_value=-180.0, max_value=180.0, format='%.4f')
else:
    latitude, longitude = locais[nome_local]

# Limite de magnitude aproximado de cada equipamento. Sao valores tipicos de
# referencia (ceu com alguma poluicao luminosa) - a noite real pode variar,
# principalmente para objetos extensos como nebulosas e galaxias, que parecem
# mais fracos do que a magnitude catalogada sugere (o app desconta 2
# magnitudes desses alvos).
alcance_equipamento = {
    'Olho nu': 6.0,
    'Binóculo': 9.5,
    'Dobson 150mm': 12.5,
}
st.sidebar.header('Equipamento')
equipamento_atual = st.sidebar.selectbox('Equipamento disponível', list(alcance_equipamento.keys()), index=2)
limite_magnitude_atual = alcance_equipamento[equipamento_atual]

if modo_panorama:
    st.sidebar.header('Janela de cálculo')
    dias_para_frente = st.sidebar.slider('Dias à frente', 3, 14, 7)
    separacao_maxima = st.sidebar.slider('Separação máxima considerada (graus)', 5, 30, 15)
    variacao_minima = st.sidebar.slider(
        'Variação mínima para contar como evento (graus)', 0, 10, 3,
        help='Pares com separação quase constante no período (como um planeta lento parado perto de uma estrela fixa há semanas) são tratados como alinhamento persistente, não como evento.'
    )
else:
    st.sidebar.header('Noite')
    data_escolhida = st.sidebar.date_input(
        'Data da noite', value=hoje_local,
        min_value=date(2000, 1, 1), max_value=date(2049, 12, 31), format='DD/MM/YYYY',
        help='A noite começa no pôr do sol da data escolhida e termina no amanhecer do dia seguinte.'
    )
    dias_para_frente = 1
    separacao_maxima = st.sidebar.slider('Separação máxima considerada (graus)', 5, 30, 15)
    variacao_minima = 0

altitude_minima_visivel = st.sidebar.slider('Altitude mínima para considerar visível (graus)', 0, 20, 5)

st.sidebar.header('Roteiro da noite')
altura_roteiro = st.sidebar.slider(
    'Altura mínima para entrar no roteiro (graus)', 10, 45, 25,
    help='Alvos mais baixos que isso (por exemplo, atrás de árvores ou prédios) ficam fora do roteiro.'
)
tempo_por_objeto = st.sidebar.select_slider('Tempo por objeto (minutos)', options=[15, 20, 30, 45, 60], value=30)

# ---------------------------------------------------------------------------
# Janela de tempo
# ---------------------------------------------------------------------------
# A janela sempre comeca ao meio-dia local, para que cada noite fique inteira
# dentro dela (por do sol, madrugada e amanhecer).
if modo_panorama:
    inicio_local = datetime(hoje_local.year, hoje_local.month, hoje_local.day, 12, 0)
    passo_minutos = 10
else:
    inicio_local = datetime(data_escolhida.year, data_escolhida.month, data_escolhida.day, 12, 0)
    passo_minutos = 5

inicio = inicio_local + fuso  # horario UTC
fim = inicio + timedelta(days=dias_para_frente)
rotulo_periodo = 'da semana' if dias_para_frente == 7 else 'dos próximos ' + str(dias_para_frente) + ' dias'
n_passos = int(dias_para_frente * 24 * 60 / passo_minutos)
horarios = [inicio + timedelta(minutes=i * passo_minutos) for i in range(n_passos)]

with st.spinner('Carregando efemérides e calculando posições...'):
    carrega = Loader(pasta_dados)
    ts = carrega.timescale()
    eph = carrega('de421.bsp')
    terra = eph['earth']
    observador = terra + wgs84.latlon(latitude, longitude)

    t = ts.utc(
        [h.year for h in horarios], [h.month for h in horarios], [h.day for h in horarios],
        [h.hour for h in horarios], [h.minute for h in horarios]
    )

    # -----------------------------------------------------------------------
    # Catalogo
    # -----------------------------------------------------------------------
    objetos = []

    dados_moveis = [
        # chave, rotulo, categoria, subtipo, corpo no JPL, magnitude, interesse, dica
        ('Sol', 'Sol', 'sol', 'Sol', 'sun', None, 0, ''),
        ('Lua', 'Lua', 'lua', 'Lua', 'moon', None, 4,
         'Passeie ao longo do terminador, onde as sombras realçam crateras e montanhas.'),
        ('Mercurio', 'Mercúrio', 'planeta', 'Planeta', 'mercury', 0.5, 2,
         'Fica baixo, no crepúsculo; precisa de horizonte limpo e é observado antes do céu escurecer.'),
        ('Venus', 'Vênus', 'planeta', 'Planeta', 'venus', -4.0, 4,
         'Mostra fases como a Lua; observe ainda no crepúsculo, com o céu claro, para reduzir o brilho.'),
        ('Marte', 'Marte', 'planeta', 'Planeta', 'mars', 0.5, 3,
         'Disco pequeno; só mostra detalhes com aumento alto e ar estável.'),
        ('Jupiter', 'Júpiter', 'planeta', 'Planeta', 'jupiter barycenter', -2.2, 5,
         'Faixas de nuvens e as quatro luas galileanas; use aumento médio.'),
        ('Saturno', 'Saturno', 'planeta', 'Planeta', 'saturn barycenter', 0.6, 5,
         'Anéis e a lua Titã; com 150 mm e ar estável, tente a divisão de Cassini com a ocular de 6 mm.'),
        ('Urano', 'Urano', 'planeta', 'Planeta', 'uranus barycenter', 5.8, 3,
         'Disquinho azul-esverdeado sem detalhes; localize com mapa ou goto.'),
        ('Netuno', 'Netuno', 'planeta', 'Planeta', 'neptune barycenter', 7.8, 2,
         'Pontinho azulado sem detalhes; o desafio é localizá-lo.'),
    ]
    for chave, rotulo, categoria, subtipo, corpo_jpl, magnitude, interesse, dica in dados_moveis:
        objetos.append({
            'chave': chave, 'rotulo': rotulo, 'categoria': categoria, 'subtipo': subtipo,
            'corpo': eph[corpo_jpl], 'magnitude': magnitude, 'interesse': interesse,
            'extenso': False, 'no_roteiro': categoria == 'sol', 'dica': dica,
        })

    dados_fixos = [
        # chave, rotulo, categoria, subtipo, magnitude, interesse, extenso,
        # (ra h, m, s), (sinal, dec graus, min, seg), dica, fora do roteiro
        ('Aldebaran', 'Aldebaran', 'estrela', 'Estrela', 0.85, 1, False, (4, 35, 55.2), (1, 16, 30, 33), '', True),
        ('Antares', 'Antares', 'estrela', 'Estrela', 1.09, 1, False, (16, 29, 24.4), (-1, 26, 25, 55), '', True),
        ('Regulus', 'Regulus', 'estrela', 'Estrela', 1.35, 1, False, (10, 8, 22.3), (1, 11, 58, 2), '', True),
        ('Spica', 'Spica', 'estrela', 'Estrela', 0.97, 1, False, (13, 25, 11.6), (-1, 11, 9, 41), '', True),
        ('Pollux', 'Pollux', 'estrela', 'Estrela', 1.14, 1, False, (7, 45, 18.9), (1, 28, 1, 34), '', True),
        ('Albireo', 'Albireo', 'estrela', 'Estrela dupla', 3.1, 4, False, (19, 30, 43.3), (1, 27, 57, 35),
         'Dupla de cores contrastantes, dourada e azulada; use aumento médio.', False),
        ('Pleiades', 'Plêiades (M45)', 'aglomerado', 'Aglomerado aberto', 1.6, 4, False, (3, 47, 0), (1, 24, 7, 0),
         'Melhor com aumento baixo ou binóculo, para caber o aglomerado inteiro no campo.', False),
        ('Hyades', 'Híades', 'aglomerado', 'Aglomerado aberto', 0.5, 3, False, (4, 27, 0), (1, 15, 52, 0),
         'Muito grande para o telescópio; fica melhor no binóculo.', False),
        ('M35', 'M35', 'aglomerado', 'Aglomerado aberto', 5.3, 3, False, (6, 8, 54), (1, 24, 20, 0),
         'Aglomerado aberto rico; aumento baixo.', False),
        ('M44', 'Presépio (M44)', 'aglomerado', 'Aglomerado aberto', 3.7, 3, False, (8, 40, 24), (1, 19, 40, 0),
         'Grande, cabe no binóculo ou no telescópio com aumento mínimo.', False),
        ('M6', 'M6 (Borboleta)', 'aglomerado', 'Aglomerado aberto', 4.2, 3, False, (17, 40, 20), (-1, 32, 15, 12),
         'Aglomerado aberto no Escorpião; aumento baixo.', False),
        ('M7', 'M7 (Ptolomeu)', 'aglomerado', 'Aglomerado aberto', 3.3, 3, False, (17, 53, 51), (-1, 34, 47, 34),
         'Aglomerado aberto grande e brilhante; aumento baixo.', False),
        ('M24', 'M24 (Nuvem de Sagitário)', 'aglomerado', 'Nuvem estelar', 4.6, 3, False, (18, 16, 54), (-1, 18, 33, 0),
         'Trecho denso da Via Láctea; varra com aumento baixo.', False),
        ('M11', 'M11 (Pato Selvagem)', 'aglomerado', 'Aglomerado aberto', 6.3, 3, False, (18, 51, 5), (-1, 6, 16, 12),
         'Aglomerado aberto denso, em forma de leque.', False),
        ('NGC4755', 'Caixa de Joias (NGC 4755)', 'aglomerado', 'Aglomerado aberto', 4.2, 4, False, (12, 53, 36), (-1, 60, 20, 0),
         'Perto do Cruzeiro do Sul, com estrelas de cores variadas; fica baixo no horizonte sul.', False),
        ('M42', 'M42 (Nebulosa de Órion)', 'profundo', 'Nebulosa', 4.0, 5, True, (5, 35, 17.3), (-1, 5, 23, 28),
         'Nebulosa brilhante com o Trapézio no centro; aumento médio.', False),
        ('M8', 'M8 (Lagoa)', 'profundo', 'Nebulosa', 6.0, 4, True, (18, 3, 48), (-1, 24, 23, 12),
         'Nebulosa com aglomerado aberto; aumento baixo e céu escuro.', False),
        ('M20', 'M20 (Trífida)', 'profundo', 'Nebulosa', 6.3, 3, True, (18, 2, 42), (-1, 23, 1, 48),
         'Sutil; precisa de céu escuro e olhar indireto.', False),
        ('M16', 'M16 (Águia)', 'profundo', 'Nebulosa', 6.0, 3, True, (18, 18, 48), (-1, 13, 49, 0),
         'O aglomerado aparece fácil; a nebulosa pede céu escuro.', False),
        ('M17', 'M17 (Ômega)', 'profundo', 'Nebulosa', 6.0, 4, True, (18, 20, 47), (-1, 16, 10, 36),
         'Nebulosa em forma de cisne ou ômega; boa com aumento baixo.', False),
        ('M27', 'M27 (Dumbbell)', 'profundo', 'Nebulosa planetária', 7.5, 4, True, (19, 59, 36), (1, 22, 43, 16),
         'Nebulosa planetária brilhante, em forma de maçã mordida.', False),
        ('M57', 'M57 (Anel)', 'profundo', 'Nebulosa planetária', 8.8, 4, True, (18, 53, 35), (1, 33, 1, 45),
         'Pequeno anel; use aumento alto.', False),
        ('M22', 'M22', 'profundo', 'Aglomerado globular', 5.1, 5, False, (18, 36, 24), (-1, 23, 54, 12),
         'Um dos melhores globulares do céu; com 150 mm começa a resolver estrelas na borda.', False),
        ('M4', 'M4', 'profundo', 'Aglomerado globular', 5.6, 3, False, (16, 23, 35.4), (-1, 26, 31, 33),
         'Globular próximo de Antares, pouco concentrado.', False),
        ('M13', 'M13', 'profundo', 'Aglomerado globular', 5.8, 4, False, (16, 41, 42), (1, 36, 28, 12),
         'Globular do Hércules; resolve estrelas com aumento alto.', False),
        ('M5', 'M5', 'profundo', 'Aglomerado globular', 5.7, 4, False, (15, 18, 33.8), (1, 2, 4, 52),
         'Globular brilhante e compacto.', False),
        ('M3', 'M3', 'profundo', 'Aglomerado globular', 6.2, 3, False, (13, 42, 11.2), (1, 28, 22, 38),
         'Globular grande e simétrico.', False),
        ('M2', 'M2', 'profundo', 'Aglomerado globular', 6.5, 3, False, (21, 33, 27), (-1, 0, 49, 24),
         'Globular compacto e brilhante.', False),
        ('M15', 'M15', 'profundo', 'Aglomerado globular', 6.2, 4, False, (21, 29, 58), (1, 12, 10, 1),
         'Globular de núcleo muito denso.', False),
        ('M30', 'M30', 'profundo', 'Aglomerado globular', 7.2, 3, False, (21, 40, 22), (-1, 23, 10, 47),
         'Globular menor, com fileiras de estrelas na borda.', False),
        ('OmegaCen', 'Ômega Centauri', 'profundo', 'Aglomerado globular', 3.9, 5, False, (13, 26, 47), (-1, 47, 28, 46),
         'O maior globular do céu; fica baixo no sul, vale com horizonte limpo.', False),
        ('M31', 'M31 (Andrômeda)', 'profundo', 'Galáxia', 3.4, 4, True, (0, 42, 44), (1, 41, 16, 9),
         'Núcleo brilhante e halo; use aumento baixo e céu escuro.', False),
        ('M33', 'M33 (Triângulo)', 'profundo', 'Galáxia', 5.7, 3, True, (1, 33, 51), (1, 30, 39, 37),
         'Muito difusa; só com céu bem escuro e aumento baixo.', False),
        ('NGC253', 'NGC 253 (Escultor)', 'profundo', 'Galáxia', 7.1, 4, True, (0, 47, 33), (-1, 25, 17, 18),
         'Galáxia alongada, uma das mais brilhantes do céu do sul.', False),
        ('M83', 'M83', 'profundo', 'Galáxia', 7.5, 3, True, (13, 37, 0), (-1, 29, 51, 56),
         'Galáxia espiral difusa; precisa de céu escuro.', False),
        ('M104', 'M104 (Sombreiro)', 'profundo', 'Galáxia', 8.0, 3, True, (12, 39, 59), (-1, 11, 37, 23),
         'Galáxia com faixa de poeira; precisa de céu escuro.', False),
    ]
    for (chave, rotulo, categoria, subtipo, magnitude, interesse, extenso,
         ra, dec, dica, fora_do_roteiro) in dados_fixos:
        estrela_fixa = Star(
            ra_hours=ra[0] + ra[1] / 60 + ra[2] / 3600,
            dec_degrees=dec[0] * (dec[1] + dec[2] / 60 + dec[3] / 3600)
        )
        objetos.append({
            'chave': chave, 'rotulo': rotulo, 'categoria': categoria, 'subtipo': subtipo,
            'corpo': estrela_fixa, 'magnitude': magnitude, 'interesse': interesse,
            'extenso': extenso, 'no_roteiro': fora_do_roteiro, 'dica': dica,
        })

    info = {item['chave']: item for item in objetos}

    # Posicao aparente de cada objeto em toda a grade de tempo (vetorizado)
    posicoes = {}
    for item in objetos:
        astrometrico = observador.at(t).observe(item['corpo']).apparent()
        alt, az, _ = astrometrico.altaz()
        posicoes[item['chave']] = {'alt': alt.degrees, 'az': az.degrees, 'apparent': astrometrico}

    alt_sol = posicoes['Sol']['alt']
    alt_lua = posicoes['Lua']['alt']
    frac_lua_serie = almanac.fraction_illuminated(eph, 'moon', t)
    fase_lua_serie = almanac.moon_phase(eph, t).degrees

    brilhantes = {'Lua', 'Venus', 'Jupiter', 'Mercurio'}
    fixos = {'estrela', 'aglomerado', 'profundo'}
    nomes_para_comparar = [item['chave'] for item in objetos if item['categoria'] != 'sol']

    # -----------------------------------------------------------------------
    # Eventos: aproximacoes entre dois corpos, com indice de qualidade
    # -----------------------------------------------------------------------
    eventos = []
    persistentes = []
    for chave_a, chave_b in itertools.combinations(nomes_para_comparar, 2):
        info_a = info[chave_a]
        info_b = info[chave_b]
        if info_a['categoria'] in fixos and info_b['categoria'] in fixos:
            continue  # dois objetos fixos nunca formam uma aproximacao

        par_tem_corpo_brilhante = (chave_a in brilhantes) or (chave_b in brilhantes)
        limite_crepusculo = -1 if par_tem_corpo_brilhante else -12

        visivel = (
            (posicoes[chave_a]['alt'] > altitude_minima_visivel) &
            (posicoes[chave_b]['alt'] > altitude_minima_visivel) &
            (alt_sol < limite_crepusculo)
        )
        if not visivel.any():
            continue

        separacao = posicoes[chave_a]['apparent'].separation_from(posicoes[chave_b]['apparent']).degrees
        separacao_visivel = np.where(visivel, separacao, 999)
        indice_minimo = int(np.argmin(separacao_visivel))
        separacao_minima = float(separacao_visivel[indice_minimo])
        if separacao_minima >= separacao_maxima:
            continue

        alt_a = float(posicoes[chave_a]['alt'][indice_minimo])
        alt_b = float(posicoes[chave_b]['alt'][indice_minimo])
        altitude_media = (alt_a + alt_b) / 2
        altitude_minima_evento = min(alt_a, alt_b)

        fracao_lua = None
        if chave_a == 'Lua' or chave_b == 'Lua':
            fracao_lua = float(frac_lua_serie[indice_minimo])

        if chave_a == 'Lua':
            outra_chave = chave_b
        elif chave_b == 'Lua':
            outra_chave = chave_a
        else:
            outra_chave = None

        if outra_chave is not None and info[outra_chave]['magnitude'] is not None:
            magnitude_do_alvo = info[outra_chave]['magnitude']
        else:
            magnitudes_do_par = [info[c]['magnitude'] for c in (chave_a, chave_b) if info[c]['magnitude'] is not None]
            magnitude_do_alvo = max(magnitudes_do_par) if len(magnitudes_do_par) > 0 else None

        if magnitude_do_alvo is not None and magnitude_do_alvo > limite_magnitude_atual:
            continue  # alvo fraco demais para o equipamento selecionado

        separacoes_visiveis = separacao[visivel]
        amplitude_evento = float(separacoes_visiveis.max() - separacoes_visiveis.min())
        if amplitude_evento < variacao_minima:
            # separacao quase constante no periodo: nao e um evento desta
            # janela, e um alinhamento que ja estava acontecendo e continua
            persistentes.append({
                'par': info_a['rotulo'] + ' - ' + info_b['rotulo'],
                'separacao': separacao_minima,
                'altitude_minima': altitude_minima_evento,
                'magnitude_do_alvo': magnitude_do_alvo,
            })
            continue

        tempo_acima_30 = np.sum(
            visivel & (posicoes[chave_a]['alt'] > 30) & (posicoes[chave_b]['alt'] > 30)
        ) * passo_minutos / 60

        altitude_norm = min(altitude_media / 90, 1)
        ausencia_lua = 1 - fracao_lua if fracao_lua is not None else 1
        # magnitude relativa ao proprio equipamento: um alvo bem dentro do
        # alcance pontua alto; um alvo raspando o limite pontua baixo
        faixa_magnitude = limite_magnitude_atual - (-4)
        if magnitude_do_alvo is not None:
            magnitude_norm = min(max((limite_magnitude_atual - magnitude_do_alvo) / faixa_magnitude, 0), 1)
        else:
            magnitude_norm = 0.5
        tempo_norm = min(tempo_acima_30 / 5, 1)
        horizonte_norm = min(max(altitude_minima_evento / 45, 0), 1)

        score = 100 * (
            0.35 * altitude_norm +
            0.25 * ausencia_lua +
            0.15 * magnitude_norm +
            0.15 * tempo_norm +
            0.10 * horizonte_norm
        )

        # um evento de madrugada (antes do meio-dia local) pertence a noite
        # que comecou no dia anterior
        horario_local_evento = horarios[indice_minimo] - fuso
        if horario_local_evento.hour < 12:
            data_noite_evento = (horario_local_evento - timedelta(days=1)).date()
        else:
            data_noite_evento = horario_local_evento.date()

        eventos.append({
            'par': info_a['rotulo'] + ' - ' + info_b['rotulo'],
            'chave_a': chave_a, 'chave_b': chave_b,
            'horario': horarios[indice_minimo],
            'data_noite': data_noite_evento,
            'separacao': separacao_minima,
            'alt_a': alt_a, 'alt_b': alt_b,
            'fracao_lua': fracao_lua,
            'magnitude_do_alvo': magnitude_do_alvo,
            'score': score,
        })

    eventos.sort(key=itemgetter('score'), reverse=True)

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------
st.title('Observatório Primeira Luz')
if modo_panorama:
    ultima_noite = hoje_local + timedelta(days=dias_para_frente - 1)
    st.caption(f'Eventos astronômicos em {nome_local}, noites de {hoje_local:%d/%m/%Y} a {ultima_noite:%d/%m/%Y}')
else:
    st.caption(f'Planejamento de observação em {nome_local}')
st.caption(f'Equipamento selecionado: {equipamento_atual} (alcance até magnitude ~{limite_magnitude_atual})')

# ---------------------------------------------------------------------------
# Panorama: melhor noite, tabela de eventos e grafico de separacao
# ---------------------------------------------------------------------------
noite_alvo = hoje_local if modo_panorama else data_escolhida

if modo_panorama:
    if len(eventos) == 0:
        st.warning('Nenhum evento encontrado com os parâmetros atuais. Tente aumentar a separação máxima na barra lateral. O planejamento de hoje aparece abaixo.')
    else:
        melhor_evento = eventos[0]
        noite_alvo = melhor_evento['data_noite']

        objetos_da_noite = []
        for evento in eventos:
            if evento['data_noite'] == noite_alvo:
                for chave_obj in (evento['chave_a'], evento['chave_b']):
                    if info[chave_obj]['rotulo'] not in objetos_da_noite:
                        objetos_da_noite.append(info[chave_obj]['rotulo'])

        classificacao = min(5, max(1, round(melhor_evento['score'] / 20)))

        st.header(f'Melhor noite {rotulo_periodo}: {noite_alvo:%d/%m} para {noite_alvo + timedelta(days=1):%d/%m}')
        coluna_score, coluna_objetos = st.columns(2)
        with coluna_score:
            st.metric('Índice de qualidade', f"{melhor_evento['score']:.1f}")
            st.write('Classificação: ' + '*' * classificacao + '.' * (5 - classificacao) + f' ({classificacao}/5)')
            st.write('Evento principal: ' + melhor_evento['par'])
            st.write(f"Separação: {melhor_evento['separacao']:.1f} graus")
        with coluna_objetos:
            st.write('Objetos dessa noite:')
            for rotulo_obj in objetos_da_noite:
                st.write('- ' + rotulo_obj)

        st.divider()
        st.subheader('Todos os eventos ' + rotulo_periodo)
        linhas_tabela = []
        for evento in eventos:
            linhas_tabela.append({
                'Par': evento['par'],
                'Horário local': (evento['horario'] - fuso).strftime('%d/%m %H:%M'),
                'Separação (graus)': round(evento['separacao'], 1),
                'Índice de qualidade': round(evento['score'], 1),
                'Altitude mínima': round(min(evento['alt_a'], evento['alt_b']), 1),
                'Lua iluminada': round(evento['fracao_lua'] * 100, 0) if evento['fracao_lua'] is not None else None,
                'Magnitude do alvo': round(evento['magnitude_do_alvo'], 1) if evento['magnitude_do_alvo'] is not None else None,
            })
        st.dataframe(pd.DataFrame(linhas_tabela), width='stretch', hide_index=True)

        if len(persistentes) > 0:
            st.caption(
                f'Além disso, {len(persistentes)} par(es) estão próximos mas com separação praticamente '
                'constante no período. Não são eventos desta janela, são alinhamentos que já estavam acontecendo.'
            )
            with st.expander('Ver alinhamentos persistentes'):
                linhas_persistentes = []
                for item_p in persistentes:
                    linhas_persistentes.append({
                        'Par': item_p['par'],
                        'Separação atual (graus)': round(item_p['separacao'], 1),
                        'Altitude mínima': round(item_p['altitude_minima'], 1),
                        'Magnitude do alvo': round(item_p['magnitude_do_alvo'], 1) if item_p['magnitude_do_alvo'] is not None else None,
                    })
                st.dataframe(pd.DataFrame(linhas_persistentes), width='stretch', hide_index=True)

        st.divider()
        st.subheader('Separação angular ao longo ' + rotulo_periodo + ' - top 5 eventos')
        figura_separacao, eixo_separacao = plt.subplots(figsize=(10, 5))
        horas_desde_inicio = [(h - inicio).total_seconds() / 3600 for h in horarios]
        for evento in eventos[:5]:
            separacao_completa = posicoes[evento['chave_a']]['apparent'].separation_from(
                posicoes[evento['chave_b']]['apparent']).degrees
            eixo_separacao.plot(horas_desde_inicio, separacao_completa, label=evento['par'])
        eixo_separacao.set_xlabel(f'Horas desde {inicio_local:%d/%m %H:%M} (horário local)')
        eixo_separacao.set_ylabel('Separação angular (graus)')
        eixo_separacao.legend()
        eixo_separacao.grid(True, alpha=0.3)
        st.pyplot(figura_separacao)

    st.info('Para ver o planejamento completo de outra noite, escolha "Planejar uma noite" na barra lateral e informe a data.')

# ---------------------------------------------------------------------------
# Planejamento da noite (usado nos dois modos, para noite_alvo)
# ---------------------------------------------------------------------------
st.divider()
st.header(f'Planejamento da noite de {noite_alvo:%d/%m} para {noite_alvo + timedelta(days=1):%d/%m}')
st.caption(f'Local: {nome_local} (latitude {latitude:.3f}, longitude {longitude:.3f}). Horários no fuso de Brasília.')

ref0 = datetime(noite_alvo.year, noite_alvo.month, noite_alvo.day, 12, 0) + fuso
ref1 = ref0 + timedelta(days=1)
idx_noite = [i for i, h in enumerate(horarios) if ref0 <= h < ref1]

if len(idx_noite) < 10:
    st.warning('A janela de cálculo não cobre essa noite.')
    st.stop()

sl = np.array(idx_noite)  # indices da noite na grade de tempo

# Sol: por do sol, fim do crepusculo astronomico (ceu escuro) e nascer do sol
i_por = None
i_nascer = None
for i in idx_noite:
    if i_por is None and alt_sol[i] < -0.833:
        i_por = i
    elif i_por is not None and i_nascer is None and alt_sol[i] > -0.833:
        i_nascer = i
idx_escuro = [i for i in idx_noite if alt_sol[i] < -12]

txt_por_sol = (horarios[i_por] - fuso).strftime('%H:%M') if i_por is not None else 'sem pôr do sol'
txt_nascer_sol = (horarios[i_nascer] - fuso).strftime('%H:%M') if i_nascer is not None else 'sem nascer do sol'
if len(idx_escuro) > 0:
    txt_escuro = (horarios[idx_escuro[0]] - fuso).strftime('%H:%M') + ' às ' + (horarios[idx_escuro[-1]] - fuso).strftime('%H:%M')
else:
    txt_escuro = 'sem céu totalmente escuro'

# Lua: fase na hora de referencia (21h locais), nascer, poente e janela sem Lua
alvo_21h = ref0 + timedelta(hours=9)
diferencas_21h = [abs((horarios[i] - alvo_21h).total_seconds()) for i in idx_noite]
idx_21h = idx_noite[int(np.argmin(diferencas_21h))]
fracao_lua_noite = float(frac_lua_serie[idx_21h])
angulo_fase_noite = float(fase_lua_serie[idx_21h])

nascer_lua = None
poente_lua = None
for k in range(1, len(idx_noite)):
    a0 = alt_lua[idx_noite[k - 1]]
    a1 = alt_lua[idx_noite[k]]
    if nascer_lua is None and a0 < -0.5 and a1 >= -0.5:
        nascer_lua = horarios[idx_noite[k]]
    if poente_lua is None and a0 >= -0.5 and a1 < -0.5:
        poente_lua = horarios[idx_noite[k]]

txt_lua_nasce = 'A Lua nasce às ' + (nascer_lua - fuso).strftime('%H:%M') if nascer_lua is not None else 'A Lua não nasce nesta janela'
txt_lua_poe = 'se põe às ' + (poente_lua - fuso).strftime('%H:%M') if poente_lua is not None else 'não se põe nesta janela'
idx_sem_lua = [i for i in idx_escuro if alt_lua[i] < -0.5]
if len(idx_escuro) > 0 and len(idx_sem_lua) == len(idx_escuro):
    txt_sem_lua = 'Todo o céu escuro fica sem Lua.'
elif len(idx_sem_lua) > 0:
    txt_sem_lua = 'Céu escuro sem Lua das ' + (horarios[idx_sem_lua[0]] - fuso).strftime('%H:%M') + ' às ' + (horarios[idx_sem_lua[-1]] - fuso).strftime('%H:%M') + '.'
else:
    txt_sem_lua = 'A Lua fica acima do horizonte durante todo o céu escuro.'

crescente = angulo_fase_noite < 180
fase_nome = 'crescente' if crescente else 'minguante'

coluna_resumo, coluna_icone = st.columns([3, 1])
with coluna_resumo:
    m1, m2, m3 = st.columns(3)
    m1.metric('Pôr do sol', txt_por_sol)
    m2.metric('Céu escuro', txt_escuro)
    m3.metric('Nascer do sol', txt_nascer_sol)
    st.write(f'Lua {fracao_lua_noite * 100:.0f}% iluminada às 21h, {fase_nome}. {txt_lua_nasce} e {txt_lua_poe}. {txt_sem_lua}')
with coluna_icone:
    # Icone da fase da Lua gerado por matplotlib: disco escuro de fundo mais
    # um recorte iluminado cujo formato segue a fracao iluminada real.
    theta_lua = np.linspace(-np.pi / 2, np.pi / 2, 200)
    y_lua = np.sin(theta_lua)
    x_limbo = np.cos(theta_lua)
    x_terminador = (1 - 2 * fracao_lua_noite) * np.cos(theta_lua)
    if not crescente:
        x_limbo = -x_limbo
        x_terminador = -x_terminador
    xs_lua = np.concatenate([x_limbo, x_terminador[::-1]])
    ys_lua = np.concatenate([y_lua, y_lua[::-1]])
    figura_lua, eixo_lua = plt.subplots(figsize=(2.0, 2.0))
    eixo_lua.add_patch(plt.Circle((0, 0), 1, color='#1b1b3a'))
    eixo_lua.fill(xs_lua, ys_lua, color='#f4f1c9')
    eixo_lua.set_xlim(-1.15, 1.15)
    eixo_lua.set_ylim(-1.15, 1.15)
    eixo_lua.set_aspect('equal')
    eixo_lua.axis('off')
    st.pyplot(figura_lua)

# Aproximacoes da noite
eventos_noite = [e for e in eventos if e['data_noite'] == noite_alvo]
if len(eventos_noite) > 0:
    st.subheader('Aproximações desta noite')
    linhas_eventos_noite = []
    for evento in eventos_noite:
        linhas_eventos_noite.append({
            'Par': evento['par'],
            'Horário local': (evento['horario'] - fuso).strftime('%d/%m %H:%M'),
            'Separação (graus)': round(evento['separacao'], 1),
            'Altitude mínima': round(min(evento['alt_a'], evento['alt_b']), 1),
            'Lua iluminada': round(evento['fracao_lua'] * 100, 0) if evento['fracao_lua'] is not None else None,
            'Magnitude do alvo': round(evento['magnitude_do_alvo'], 1) if evento['magnitude_do_alvo'] is not None else None,
        })
    st.dataframe(pd.DataFrame(linhas_eventos_noite), width='stretch', hide_index=True)

# A Lua quase cheia ou quase nova rende menos como alvo
info['Lua']['interesse'] = 4 if 0.08 < fracao_lua_noite < 0.92 else 2

# ---------------------------------------------------------------------------
# Alvos da noite: alcance, janela de visibilidade e interferencia da Lua
# ---------------------------------------------------------------------------
dados_obj = {}
linhas_alvos = []
fora_do_alcance = []
sessao_planetaria = []
sessao_ceu_profundo = []
sessao_binoculo = []
alvos_faceis = []
alvos_intermediarios = []
alvos_desafio = []

for item in objetos:
    if item['no_roteiro']:
        continue
    chave = item['chave']
    alt_obj = posicoes[chave]['alt']
    az_obj = posicoes[chave]['az']

    limite_sol_obj = -6 if chave in brilhantes else -12
    altura_min_obj = min(altura_roteiro, 8) if chave in ('Mercurio', 'Venus') else altura_roteiro

    mascara_sol = alt_sol[sl] < limite_sol_obj
    alt_mascarada = np.where(mascara_sol, alt_obj[sl], -90.0)
    p_pico = int(np.argmax(alt_mascarada))
    alt_pico = float(alt_mascarada[p_pico])
    if alt_pico < altitude_minima_visivel:
        continue  # nao aparece no ceu escuro desta noite

    # alcance do equipamento (objetos extensos perdem 2 magnitudes)
    magnitude_obj = item['magnitude']
    if magnitude_obj is None:
        nivel = 'Fácil'
    else:
        limite_efetivo = limite_magnitude_atual - (2.0 if item['extenso'] else 0.0)
        margem = limite_efetivo - magnitude_obj
        if margem >= 3:
            nivel = 'Fácil'
        elif margem >= 1:
            nivel = 'Moderado'
        elif margem >= 0:
            nivel = 'Desafio'
        else:
            nivel = 'Fora do alcance'
    if nivel == 'Fora do alcance':
        fora_do_alcance.append(item['rotulo'])
        continue

    # distancia da Lua e interferencia (so para nebulosas e galaxias)
    if chave != 'Lua':
        sep_lua = posicoes[chave]['apparent'].separation_from(posicoes['Lua']['apparent']).degrees
    else:
        sep_lua = np.zeros(len(horarios))
    if item['extenso']:
        interferencia = (alt_lua > 0) & (frac_lua_serie > 0.25) & (sep_lua < 50)
    else:
        interferencia = np.zeros(len(horarios), dtype=bool)

    ok = (alt_obj[sl] >= altura_min_obj) & mascara_sol
    ok_roteiro = ok & ~interferencia[sl]

    # quantos passos seguidos o alvo continua utilizavel a partir de cada instante
    restante = np.zeros(len(sl), dtype=int)
    for p in range(len(sl) - 1, -1, -1):
        if ok_roteiro[p]:
            restante[p] = 1 + (restante[p + 1] if p + 1 < len(sl) else 0)

    pos_ok = np.where(ok)[0]
    if len(pos_ok) > 0:
        txt_janela = (horarios[sl[pos_ok[0]]] - fuso).strftime('%H:%M') + ' às ' + (horarios[sl[pos_ok[-1]]] - fuso).strftime('%H:%M')
    else:
        txt_janela = f'não passa de {altura_min_obj:.0f}°'

    if item['extenso'] and ok.any():
        fracao_interferida = float((ok & interferencia[sl]).sum()) / float(ok.sum())
        if fracao_interferida >= 0.99:
            txt_lua_atrapalha = 'Sim'
        elif fracao_interferida > 0:
            txt_lua_atrapalha = 'Em parte'
        else:
            txt_lua_atrapalha = 'Não'
    else:
        txt_lua_atrapalha = '-'

    az_pico = float(az_obj[sl[p_pico]])
    direcao_pico = pontos_cardeais[int(((az_pico + 22.5) % 360) // 45)]

    dados_obj[chave] = {
        'item': item, 'nivel': nivel, 'alt': alt_obj, 'az': az_obj,
        'ok_roteiro': ok_roteiro, 'restante': restante,
    }
    linhas_alvos.append({
        '_pico': p_pico,
        'Objeto': item['rotulo'],
        'Tipo': item['subtipo'],
        'Magnitude': round(magnitude_obj, 1) if magnitude_obj is not None else None,
        'Dificuldade': nivel,
        'Altura máxima': f'{alt_pico:.0f}° ({direcao_pico})',
        'Melhor horário': (horarios[sl[p_pico]] - fuso).strftime('%H:%M'),
        f'Acima de {altura_roteiro}°': txt_janela,
        'Lua atrapalha': txt_lua_atrapalha,
    })

    if item['categoria'] in ('planeta', 'lua'):
        sessao_planetaria.append(item['rotulo'])
    if item['categoria'] == 'profundo':
        sessao_ceu_profundo.append(item['rotulo'])
    if magnitude_obj is not None and magnitude_obj <= 4.5 and item['categoria'] in ('aglomerado', 'profundo'):
        sessao_binoculo.append(item['rotulo'])
    if nivel == 'Fácil':
        alvos_faceis.append(item['rotulo'])
    elif nivel == 'Moderado':
        alvos_intermediarios.append(item['rotulo'])
    else:
        alvos_desafio.append(item['rotulo'])

# ---------------------------------------------------------------------------
# Roteiro: a cada intervalo escolhe o melhor alvo disponivel
# ---------------------------------------------------------------------------
# Regras: um alvo so entra se ficar utilizavel durante todo o intervalo; alvos
# que sairiam do ceu logo depois tem prioridade (urgentes); fora isso vale o
# interesse do alvo mais um bonus por altura (alturas medias sao melhores, e
# acima de 78 graus o Dobson fica incomodo de apontar).
passo_slot = max(1, int(round(tempo_por_objeto / passo_minutos)))
duracao_slot = passo_slot * passo_minutos
posicoes_slot = [p for p in range(len(sl)) if alt_sol[sl[p]] < -6][::passo_slot]

usados = set()
roteiro = []
for p in posicoes_slot:
    disponiveis = [
        chave for chave, d in dados_obj.items()
        if chave not in usados and d['restante'][p] >= passo_slot
    ]
    if len(disponiveis) == 0:
        continue
    urgentes = [c for c in disponiveis if dados_obj[c]['restante'][p] < 2 * passo_slot]
    pool = urgentes if len(urgentes) > 0 else disponiveis

    melhor_chave = None
    melhor_valor = -1e9
    for c in pool:
        altura_c = float(dados_obj[c]['alt'][sl[p]])
        bonus = min(altura_c, 65) / 65 * 1.5
        if altura_c > 78:
            bonus -= 0.7
        valor = dados_obj[c]['item']['interesse'] + bonus
        if valor > melhor_valor:
            melhor_valor = valor
            melhor_chave = c

    usados.add(melhor_chave)
    p_meio = min(p + passo_slot // 2, len(sl) - 1)
    az_meio = float(dados_obj[melhor_chave]['az'][sl[p_meio]])
    alt_meio = float(dados_obj[melhor_chave]['alt'][sl[p_meio]])
    inicio_slot = horarios[sl[p]] - fuso
    fim_slot = inicio_slot + timedelta(minutes=duracao_slot)
    roteiro.append({
        'chave': melhor_chave,
        'item': dados_obj[melhor_chave]['item'],
        'nivel': dados_obj[melhor_chave]['nivel'],
        'horario': inicio_slot.strftime('%H:%M') + ' às ' + fim_slot.strftime('%H:%M'),
        'onde': pontos_cardeais[int(((az_meio + 22.5) % 360) // 45)] + f', {alt_meio:.0f}° de altura',
        'az': az_meio, 'alt': alt_meio,
        'interesse': dados_obj[melhor_chave]['item']['interesse'],
    })

st.subheader('Roteiro da noite')
if len(roteiro) == 0:
    st.write('Não foi possível montar um roteiro para essa noite com os parâmetros atuais. Tente diminuir a altura mínima do roteiro ou escolher outro equipamento.')
else:
    st.caption(f'Cerca de {tempo_por_objeto} minutos por objeto, só com alvos acima de {altura_roteiro}° de altura. Os alvos que se põem primeiro vêm antes.')
    linhas_roteiro = []
    for numero, passo_roteiro in enumerate(roteiro, start=1):
        linhas_roteiro.append({
            '#': numero,
            'Horário': passo_roteiro['horario'],
            'Objeto': passo_roteiro['item']['rotulo'],
            'Tipo': passo_roteiro['item']['subtipo'],
            'Onde olhar': passo_roteiro['onde'],
            'Dificuldade': passo_roteiro['nivel'],
            'Dica': passo_roteiro['item']['dica'],
        })
    st.table(pd.DataFrame(linhas_roteiro).set_index('#'))

    coluna_mapa, coluna_altura = st.columns(2)

    with coluna_mapa:
        # Mapa do ceu: zenite no centro, horizonte na borda, norte em cima.
        figura_mapa = plt.figure(figsize=(6, 6))
        eixo_mapa = figura_mapa.add_subplot(111, polar=True)
        eixo_mapa.set_theta_zero_location('N')
        eixo_mapa.set_theta_direction(-1)
        eixo_mapa.set_rlim(0, 90)
        eixo_mapa.set_rticks([30, 60, 90])
        eixo_mapa.set_yticklabels(['60°', '30°', 'horizonte'])
        eixo_mapa.set_xticks(np.radians(np.arange(0, 360, 45)))
        eixo_mapa.set_xticklabels(siglas_cardeais)
        for numero, passo_roteiro in enumerate(roteiro, start=1):
            azimute_rad = np.radians(passo_roteiro['az'])
            raio = 90 - passo_roteiro['alt']
            eixo_mapa.scatter(azimute_rad, raio, s=80)
            eixo_mapa.annotate(str(numero) + '. ' + passo_roteiro['item']['rotulo'], (azimute_rad, raio),
                               textcoords='offset points', xytext=(6, 6), fontsize=8)
        st.pyplot(figura_mapa)
        st.caption('Posição de cada alvo no horário do roteiro. O centro é o zênite (acima da cabeça) e a borda é o horizonte. Norte em cima, leste à direita.')

    with coluna_altura:
        # Altura dos alvos de maior interesse ao longo da noite
        x_horas = np.array([(horarios[i] - ref0).total_seconds() / 3600 for i in idx_noite])
        figura_altura, eixo_altura = plt.subplots(figsize=(6, 6))
        eixo_altura.fill_between(x_horas, 0, 90, where=alt_sol[sl] > -12, color='gray', alpha=0.2, label='Céu claro')
        principais = sorted(roteiro, key=itemgetter('interesse'), reverse=True)[:8]
        for passo_roteiro in principais:
            eixo_altura.plot(x_horas, dados_obj[passo_roteiro['chave']]['alt'][sl], label=passo_roteiro['item']['rotulo'])
        if 'Lua' not in [pr['chave'] for pr in principais]:
            eixo_altura.plot(x_horas, alt_lua[sl], color='gold', linestyle='--', label='Lua')
        eixo_altura.axhline(altura_roteiro, color='red', linestyle=':', label=f'Mínimo do roteiro ({altura_roteiro}°)')
        eixo_altura.set_ylim(0, 90)
        eixo_altura.set_xlim(0, 24)
        eixo_altura.set_xticks(range(0, 25, 2))
        eixo_altura.set_xticklabels([f'{(12 + h) % 24:02d}h' for h in range(0, 25, 2)])
        eixo_altura.set_xlabel('Horário local')
        eixo_altura.set_ylabel('Altura (graus)')
        eixo_altura.grid(True, alpha=0.3)
        eixo_altura.legend(fontsize=7, loc='upper left')
        st.pyplot(figura_altura)
        st.caption('Altura dos principais alvos ao longo da noite. As faixas cinzas marcam o dia e o crepúsculo.')

# ---------------------------------------------------------------------------
# Todos os alvos visiveis e sessoes
# ---------------------------------------------------------------------------
st.divider()
st.subheader('Alvos visíveis nesta noite')
if len(linhas_alvos) > 0:
    tabela_alvos = pd.DataFrame(linhas_alvos).sort_values('_pico').drop(columns='_pico')
    st.dataframe(tabela_alvos, width='stretch', hide_index=True)
else:
    st.write('Nenhum alvo do catálogo fica visível no céu escuro dessa noite com os parâmetros atuais.')
if len(fora_do_alcance) > 0:
    with st.expander(f'{len(fora_do_alcance)} alvo(s) fora do alcance do equipamento selecionado'):
        st.write(', '.join(fora_do_alcance))

st.subheader('Sessões de observação')
coluna_a, coluna_b, coluna_c = st.columns(3)
with coluna_a:
    st.write('**Sessão Planetária**')
    for rotulo_obj in sessao_planetaria:
        st.write('- ' + rotulo_obj)
with coluna_b:
    st.write('**Céu Profundo**')
    for rotulo_obj in sessao_ceu_profundo:
        st.write('- ' + rotulo_obj)
with coluna_c:
    st.write('**Binóculo**')
    for rotulo_obj in sessao_binoculo:
        st.write('- ' + rotulo_obj)

coluna_d, coluna_e, coluna_f = st.columns(3)
with coluna_d:
    st.write('**Iniciantes**')
    for rotulo_obj in alvos_faceis:
        st.write('- ' + rotulo_obj)
with coluna_e:
    st.write('**Intermediários**')
    for rotulo_obj in alvos_intermediarios:
        st.write('- ' + rotulo_obj)
with coluna_f:
    st.write('**Desafio**')
    for rotulo_obj in alvos_desafio:
        st.write('- ' + rotulo_obj)

st.divider()
st.caption('Desenvolvido por Vinicio Almeida')