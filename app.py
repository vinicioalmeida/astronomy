# Observatorio Primeira Luz - painel Streamlit
# Mostra os eventos astronomicos da semana para o ceu de Natal/RN: o indice de
# qualidade de cada evento, a melhor noite da semana com a fase da Lua e um
# mapa do ceu gerados por matplotlib, as sessoes de observacao classificadas
# por tipo e dificuldade, e um roteiro para a melhor noite.
#
# Para rodar localmente: streamlit run observatorio_almeida.py
# Para publicar: mesmo processo do site academico, subindo este arquivo e o
# requirements.txt para o repositorio conectado ao Streamlit Cloud.

import os
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta
from skyfield.api import Loader, wgs84, Star
from skyfield import almanac

st.set_page_config(page_title='Observatório Primeira Luz', layout='wide')

# Pasta de dados: usa a pasta onde este arquivo esta salvo, para funcionar
# tanto rodando localmente quanto publicado no Streamlit Cloud.
pasta_dados = os.path.dirname(os.path.abspath(__file__))

st.sidebar.header('Parâmetros')
dias_para_frente = st.sidebar.slider('Dias à frente', 3, 14, 7)
separacao_maxima = st.sidebar.slider('Separação máxima considerada (graus)', 5, 30, 15)
altitude_minima_visivel = st.sidebar.slider('Altitude mínima para considerar visível (graus)', 0, 20, 5)

# Limite de magnitude aproximado de cada equipamento. Sao valores tipicos de
# referencia (ceu com alguma poluicao luminosa, como o de Natal) - a noite
# real pode variar, principalmente para objetos extensos como nebulosas e
# galaxias, que parecem mais fracos do que a magnitude catalogada sugere.
alcance_equipamento = {
    'Olho nu': 6.0,
    'Binóculo': 9.5,
    'Dobson 150mm': 12.5,
}
equipamento_atual = st.sidebar.selectbox('Equipamento disponível', list(alcance_equipamento.keys()), index=1)
limite_magnitude_atual = alcance_equipamento[equipamento_atual]

with st.spinner('Carregando efemérides e calculando posições...'):
    carrega = Loader(pasta_dados)
    ts = carrega.timescale()
    eph = carrega('de421.bsp')
    terra = eph['earth']

    latitude = -5.795
    longitude = -35.209
    natal = wgs84.latlon(latitude, longitude)
    observador = terra + natal

    inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=dias_para_frente)
    rotulo_periodo = 'da semana' if dias_para_frente == 7 else 'dos próximos ' + str(dias_para_frente) + ' dias'
    passo_minutos = 10
    n_passos = int((fim - inicio).total_seconds() / 60 / passo_minutos)
    horarios = [inicio + timedelta(minutes=i * passo_minutos) for i in range(n_passos)]
    t = ts.utc(
        [h.year for h in horarios], [h.month for h in horarios], [h.day for h in horarios],
        [h.hour for h in horarios], [h.minute for h in horarios]
    )

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

    magnitude_aproximada = {
        'Mercurio': 0.5, 'Venus': -4.0, 'Marte': 0.5, 'Jupiter': -2.2, 'Saturno': 0.6,
        'Urano': 5.8, 'Netuno': 7.8,
        'Aldebaran': 0.85, 'Antares': 1.09, 'Regulus': 1.35, 'Spica': 0.97, 'Pollux': 1.14,
        'Albireo': 3.1, 'Pleiades': 1.6, 'Hyades': 0.5,
        'M8': 6.0, 'M22': 5.1, 'M13': 5.8, 'M31': 3.4,
    }

    posicoes = {}
    for nome, categoria, corpo in catalogo:
        astrometrico = observador.at(t).observe(corpo).apparent()
        alt, az, _ = astrometrico.altaz()
        posicoes[nome] = {'categoria': categoria, 'alt': alt.degrees, 'az': az.degrees, 'apparent': astrometrico}

    alt_sol = posicoes['Sol']['alt']
    brilhantes = {'Lua', 'Venus', 'Jupiter', 'Mercurio'}
    fixos = {'estrela', 'aglomerado', 'profundo'}
    nomes_para_comparar = [nome for nome, categoria, corpo in catalogo if categoria != 'sol']

    eventos = []
    for nome_a, nome_b in itertools.combinations(nomes_para_comparar, 2):
        if posicoes[nome_a]['categoria'] in fixos and posicoes[nome_b]['categoria'] in fixos:
            continue

        separacao = posicoes[nome_a]['apparent'].separation_from(posicoes[nome_b]['apparent']).degrees

        par_tem_corpo_brilhante = (nome_a in brilhantes) or (nome_b in brilhantes)
        limite_crepusculo = -1 if par_tem_corpo_brilhante else -12

        visivel = (
            (posicoes[nome_a]['alt'] > altitude_minima_visivel) &
            (posicoes[nome_b]['alt'] > altitude_minima_visivel) &
            (alt_sol < limite_crepusculo)
        )

        if not visivel.any():
            continue

        separacao_visivel = np.where(visivel, separacao, 999)
        indice_minimo = int(np.argmin(separacao_visivel))
        separacao_minima = separacao_visivel[indice_minimo]

        if separacao_minima >= separacao_maxima:
            continue

        alt_a = posicoes[nome_a]['alt'][indice_minimo]
        alt_b = posicoes[nome_b]['alt'][indice_minimo]
        altitude_media = (alt_a + alt_b) / 2
        altitude_minima_evento = min(alt_a, alt_b)

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

        dentro_do_alcance = magnitude_do_alvo is None or magnitude_do_alvo <= limite_magnitude_atual

        tempo_acima_30 = np.sum(
            visivel & (posicoes[nome_a]['alt'] > 30) & (posicoes[nome_b]['alt'] > 30)
        ) * passo_minutos / 60

        altitude_norm = min(altitude_media / 90, 1)
        ausencia_lua = 1 - fracao_lua if fracao_lua is not None else 1
        magnitude_norm = min(max((8 - magnitude_do_alvo) / 12, 0), 1) if magnitude_do_alvo is not None else 0.5
        tempo_norm = min(tempo_acima_30 / 5, 1)
        horizonte_norm = min(max(altitude_minima_evento / 45, 0), 1)

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
            'dentro_do_alcance': dentro_do_alcance,
            'magnitude_do_alvo': magnitude_do_alvo,
            'score': score,
        })

    eventos.sort(key=lambda e: e['score'], reverse=True)

st.title('Observatório Primeira Luz')
st.caption('Eventos astronômicos em Natal/RN, ' + inicio.strftime('%d/%m/%Y') + ' a ' + fim.strftime('%d/%m/%Y'))
st.caption('Equipamento selecionado: ' + equipamento_atual + ' (alcance até magnitude ~' + str(limite_magnitude_atual) + ')')

if len(eventos) == 0:
    st.warning('Nenhum evento encontrado com os parâmetros atuais. Tente aumentar a separação máxima na barra lateral.')
else:
    melhor_evento = eventos[0]
    horario_local_melhor = melhor_evento['horario'] - timedelta(hours=3)
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

    st.header('Melhor noite ' + rotulo_periodo + ': ' + noite_data.strftime('%d/%m') + ' para ' + (noite_data + timedelta(days=1)).strftime('%d/%m'))

    # Momento de referencia da noite (21h locais) para calcular a fase da Lua
    # exibida no painel, independente de a Lua participar do evento principal.
    inicio_noite_painel = datetime(noite_data.year, noite_data.month, noite_data.day, 21, 0) + timedelta(hours=3)
    diferencas = [abs((h - inicio_noite_painel).total_seconds()) for h in horarios]
    indice_noite_painel = int(np.argmin(diferencas))
    fracao_lua_noite = almanac.fraction_illuminated(eph, 'moon', t[indice_noite_painel])
    angulo_fase_noite = almanac.moon_phase(eph, t[indice_noite_painel]).degrees

    coluna_score, coluna_fase, coluna_objetos = st.columns([1, 1, 1])

    with coluna_score:
        st.metric('Índice de qualidade', '{:.1f}'.format(melhor_evento['score']))
        st.write('Classificação: ' + '*' * classificacao + '.' * (5 - classificacao) + ' (' + str(classificacao) + '/5)')
        st.write('Evento principal: ' + melhor_evento['par'])
        st.write('Separação: {:.1f} graus'.format(melhor_evento['separacao']))

    with coluna_fase:
        # Icone de fase da Lua gerado por matplotlib: disco escuro de fundo
        # (lua nova) mais um recorte iluminado cujo formato segue a fracao
        # iluminada real. Convencao simplificada: crescente ilumina o lado
        # direito, minguante ilumina o lado esquerdo (aproximado).
        crescente = angulo_fase_noite < 180
        theta_lua = np.linspace(-np.pi / 2, np.pi / 2, 200)
        y_lua = np.sin(theta_lua)
        x_limbo = np.cos(theta_lua)
        x_terminador = (1 - 2 * fracao_lua_noite) * np.cos(theta_lua)
        if not crescente:
            x_limbo = -x_limbo
            x_terminador = -x_terminador
        xs_lua = np.concatenate([x_limbo, x_terminador[::-1]])
        ys_lua = np.concatenate([y_lua, y_lua[::-1]])

        figura_lua, eixo_lua = plt.subplots(figsize=(2.6, 2.6))
        circulo_fundo = plt.Circle((0, 0), 1, color='#1b1b3a')
        eixo_lua.add_patch(circulo_fundo)
        eixo_lua.fill(xs_lua, ys_lua, color='#f4f1c9')
        eixo_lua.set_xlim(-1.15, 1.15)
        eixo_lua.set_ylim(-1.15, 1.15)
        eixo_lua.set_aspect('equal')
        eixo_lua.axis('off')
        st.pyplot(figura_lua)
        fase_nome = 'crescente' if crescente else 'minguante'
        st.write('Lua {:.0f}% iluminada, {}'.format(fracao_lua_noite * 100, fase_nome))

    with coluna_objetos:
        st.write('Objetos dessa noite:')
        for nome_obj in objetos_da_noite:
            st.write('- ' + nome_obj)

    st.divider()
    st.subheader('Todos os eventos ' + rotulo_periodo)
    linhas_tabela = []
    for evento in eventos:
        linhas_tabela.append({
            'Par': evento['par'],
            'Horário local': (evento['horario'] - timedelta(hours=3)).strftime('%d/%m %H:%M'),
            'Separação (graus)': round(evento['separacao'], 1),
            'Índice de qualidade': round(evento['score'], 1),
            'Altitude mínima': round(min(evento['alt_a'], evento['alt_b']), 1),
            'Lua iluminada': round(evento['fracao_lua'] * 100, 0) if evento['fracao_lua'] is not None else None,
            'Ao alcance do equipamento': evento['dentro_do_alcance'],
        })
    tabela_eventos = pd.DataFrame(linhas_tabela)
    st.dataframe(tabela_eventos, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader('Separação angular ao longo ' + rotulo_periodo + ' - top 5 eventos')
    top_eventos = eventos[:5]
    figura_separacao, eixo_separacao = plt.subplots(figsize=(10, 5))
    for evento in top_eventos:
        nome_a, nome_b = evento['par'].split(' - ')
        separacao_completa = posicoes[nome_a]['apparent'].separation_from(posicoes[nome_b]['apparent']).degrees
        horas_desde_inicio = [(h - inicio).total_seconds() / 3600 for h in horarios]
        eixo_separacao.plot(horas_desde_inicio, separacao_completa, label=evento['par'])
    eixo_separacao.set_xlabel('Horas desde ' + inicio.strftime('%d/%m 00h UTC'))
    eixo_separacao.set_ylabel('Separação angular (graus)')
    eixo_separacao.legend()
    eixo_separacao.grid(True, alpha=0.3)
    st.pyplot(figura_separacao)

    st.divider()
    st.subheader('Sessões de observação')
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

    coluna_a, coluna_b, coluna_c = st.columns(3)
    with coluna_a:
        st.write('**Sessão Planetária**')
        for nome_obj in sessao_planetaria:
            st.write('- ' + nome_obj)
    with coluna_b:
        st.write('**Céu Profundo**')
        for nome_obj in sessao_ceu_profundo:
            st.write('- ' + nome_obj)
    with coluna_c:
        st.write('**Binóculo**')
        for nome_obj in sessao_binoculo:
            st.write('- ' + nome_obj)

    coluna_d, coluna_e = st.columns(2)
    with coluna_d:
        st.write('**Iniciantes**')
        for nome_obj in iniciantes:
            st.write('- ' + nome_obj)
    with coluna_e:
        st.write('**Desafio**')
        for nome_obj in desafio:
            st.write('- ' + nome_obj)

    st.divider()
    st.subheader('Roteiro para a noite de ' + noite_data.strftime('%d/%m') + ' para ' + (noite_data + timedelta(days=1)).strftime('%d/%m'))

    inicio_noite = datetime(noite_data.year, noite_data.month, noite_data.day, 18, 0) + timedelta(hours=3)
    fim_noite = inicio_noite + timedelta(hours=12)
    indices_noite = [i for i, h in enumerate(horarios) if inicio_noite <= h < fim_noite and alt_sol[i] < -12]
    indices_slots = indices_noite[::3]

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
        roteiro.append({'Horário': hora_local, 'Objeto': escolhido, 'indice_tempo': indice})
        if len(roteiro) >= 8:
            break

    if len(roteiro) > 0:
        tabela_roteiro = pd.DataFrame(roteiro)[['Horário', 'Objeto']]
        st.table(tabela_roteiro)

        # Mapa do ceu gerado por matplotlib para o roteiro: cada objeto e
        # plotado na sua posicao de altitude/azimute no horario sugerido.
        # Norte para cima, azimute crescendo no sentido horario, zenite no
        # centro (raio = 90 - altitude).
        figura_mapa = plt.figure(figsize=(6, 6))
        eixo_mapa = figura_mapa.add_subplot(111, polar=True)
        eixo_mapa.set_theta_zero_location('N')
        eixo_mapa.set_theta_direction(-1)
        eixo_mapa.set_rlim(0, 90)
        eixo_mapa.set_rticks([30, 60, 90])
        eixo_mapa.set_yticklabels(['60 graus', '30 graus', 'horizonte'])
        for item in roteiro:
            indice_item = item['indice_tempo']
            nome_obj = item['Objeto']
            azimute_rad = np.radians(posicoes[nome_obj]['az'][indice_item])
            raio = 90 - posicoes[nome_obj]['alt'][indice_item]
            eixo_mapa.scatter(azimute_rad, raio, s=80)
            eixo_mapa.annotate(nome_obj, (azimute_rad, raio), textcoords='offset points', xytext=(6, 6))
        st.pyplot(figura_mapa)
    else:
        st.write('Não foi possível montar um roteiro para essa noite com os parâmetros atuais.')

st.divider()
st.caption('Desenvolvido por Vinicio Almeida')