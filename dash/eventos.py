import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from icalendar import Calendar
import pytz

st.set_page_config(page_title="Eventos Astronômicos", layout="wide")

st.title("🔭 Eventos Astronômicos Visíveis")

st.markdown("""
Este dashboard mostra eventos astronômicos visíveis nos próximos dias, com base em sua localização.
""")

# Localização aproximada (Goianinha-RN como padrão)
col1, col2 = st.columns(2)
with col1:
    latitude = st.number_input("Latitude", value=-6.2847, format="%.4f", help="Latitude da sua localização")
with col2:
    longitude = st.number_input("Longitude", value=-35.1997, format="%.4f", help="Longitude da sua localização")

dias = st.slider("Dias à frente", min_value=1, max_value=30, value=7)

@st.cache_data(ttl=3600)  # Cache por 1 hora
def buscar_eventos_astronomicos(lat, lon, dias):
    """Busca eventos astronômicos do In-The-Sky.org"""
    
    # URL corrigida com parâmetros adequados
    ical_url = f"https://in-the-sky.org/ical.php?c=BR&l={lat},{lon}&n={dias}&type=0"
    
    try:
        # Headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(ical_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Verifica se o conteúdo é um calendário válido
        if not response.content or b'BEGIN:VCALENDAR' not in response.content:
            return None, "Dados de calendário inválidos recebidos"
        
        cal = Calendar.from_ical(response.content)
        
        eventos = []
        timezone_br = pytz.timezone('America/Fortaleza')  # Timezone do RN
        
        for component in cal.walk():
            if component.name == "VEVENT":
                try:
                    # Extrai data/hora
                    dtstart = component.get("dtstart")
                    if dtstart:
                        start_dt = dtstart.dt
                        
                        # Converte para datetime se for apenas data
                        if isinstance(start_dt, datetime):
                            # Se já tem timezone, converte para BR
                            if start_dt.tzinfo:
                                start_dt = start_dt.astimezone(timezone_br)
                            else:
                                # Se não tem timezone, assume UTC e converte
                                start_dt = pytz.UTC.localize(start_dt).astimezone(timezone_br)
                            data_formatada = start_dt.strftime("%d/%m/%Y %H:%M")
                            data_sort = start_dt
                        else:
                            # Se for apenas data (sem hora)
                            data_formatada = start_dt.strftime("%d/%m/%Y")
                            data_sort = datetime.combine(start_dt, datetime.min.time())
                    else:
                        continue
                    
                    # Extrai título do evento
                    summary = component.get("summary")
                    if summary:
                        titulo = str(summary).strip()
                    else:
                        continue
                    
                    # Extrai descrição se disponível
                    description = component.get("description")
                    descricao = str(description).strip() if description else ""
                    
                    eventos.append({
                        "Data": data_formatada,
                        "Evento": titulo,
                        "Descrição": descricao,
                        "Data_Sort": data_sort
                    })
                    
                except Exception as e:
                    continue  # Pula eventos com problemas
        
        return eventos, None
        
    except requests.exceptions.Timeout:
        return None, "Timeout ao acessar o serviço"
    except requests.exceptions.RequestException as e:
        return None, f"Erro na requisição: {str(e)}"
    except Exception as e:
        return None, f"Erro ao processar dados: {str(e)}"

def criar_eventos_exemplo():
    """Cria eventos astronômicos de exemplo baseados na data atual"""
    hoje = datetime.now()
    eventos_exemplo = []
    
    # Eventos astronômicos comuns
    eventos_base = [
        "Lua Cheia",
        "Lua Nova", 
        "Conjunção de Júpiter e Saturno",
        "Máximo da chuva de meteoros Perseidas",
        "Oposição de Marte",
        "Eclipse lunar parcial",
        "Passagem da Estação Espacial Internacional"
    ]
    
    for i, evento in enumerate(eventos_base[:min(len(eventos_base), dias)]):
        data_evento = hoje + timedelta(days=i+1)
        eventos_exemplo.append({
            "Data": data_evento.strftime("%d/%m/%Y %H:%M"),
            "Evento": evento,
            "Descrição": f"Evento astronômico visível de {evento.lower()}",
            "Data_Sort": data_evento
        })
    
    return eventos_exemplo

# Interface principal
if st.button("🔍 Buscar Eventos", type="primary"):
    with st.spinner("Buscando eventos astronômicos..."):
        
        # Mostra informações da busca
        st.info(f"📍 Buscando eventos para coordenadas: {latitude}, {longitude}")
        
        eventos, erro = buscar_eventos_astronomicos(latitude, longitude, dias)
        
        if erro:
            st.error(f"❌ Erro ao buscar eventos: {erro}")
            st.warning("Mostrando eventos de exemplo:")
            eventos = criar_eventos_exemplo()
        
        if eventos:
            # Cria DataFrame e ordena por data
            df = pd.DataFrame(eventos)
            df = df.sort_values("Data_Sort").reset_index(drop=True)
            df = df.drop("Data_Sort", axis=1)  # Remove coluna auxiliar
            
            st.success(f"✅ {len(eventos)} eventos encontrados para os próximos {dias} dias:")
            
            # Mostra tabela de eventos
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "Data": st.column_config.TextColumn("📅 Data", width="medium"),
                    "Evento": st.column_config.TextColumn("🌟 Evento", width="large"), 
                    "Descrição": st.column_config.TextColumn("📝 Descrição", width="large")
                }
            )
            
            # Gráfico de eventos por dia (se houver dados suficientes)
            if len(df) > 1:
                st.subheader("📊 Distribuição de Eventos")
                df_graph = df.copy()
                df_graph['Dia'] = pd.to_datetime(df_graph['Data'], format='%d/%m/%Y %H:%M', errors='coerce').dt.date
                eventos_por_dia = df_graph['Dia'].value_counts().sort_index()
                st.bar_chart(eventos_por_dia)
            
        else:
            st.warning("⚠️ Nenhum evento encontrado para os parâmetros especificados.")

# Informações adicionais
with st.expander("ℹ️ Informações sobre o Dashboard"):
    st.markdown("""
    **Como usar:**
    1. Ajuste sua latitude e longitude (ou use a localização padrão)
    2. Selecione quantos dias à frente você quer ver
    3. Clique em "Buscar Eventos"
    
    **Fontes de dados:**
    - In-The-Sky.org (serviço de eventos astronômicos)
    - Eventos incluem: fases da lua, conjunções planetárias, chuvas de meteoros, eclipses, etc.
    
    **Localização padrão:** Goianinha, Rio Grande do Norte, Brasil
    
    **Nota:** Em caso de problemas com a API externa, são mostrados eventos de exemplo.
    """)

# Link para download do arquivo ICS
ical_url = f"https://in-the-sky.org/ical.php?c=BR&l={latitude},{longitude}&n={dias}&type=0"
st.markdown(f"[📥 Baixar arquivo .ics com eventos]({ical_url})")

# Rodapé
st.markdown("---")
st.markdown("🔭 **Dashboard de Eventos Astronômicos** | Desenvolvido com Streamlit")