"""
Análise e Visualização de Exoplanetas - Dados NASA
Projeto para análise de planetas potencialmente habitáveis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

class ExoplanetAnalyzer:
    def __init__(self):
        """Inicializa o analisador de exoplanetas"""
        self.data = None
        self.habitable_zone_data = None
        
    def fetch_nasa_data(self):
        """Busca dados reais do NASA Exoplanet Archive"""
        print("🚀 Buscando dados do NASA Exoplanet Archive...")
        
        # URL da API da NASA para exoplanetas confirmados
        url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
        
        # Query ADQL para buscar dados relevantes
        query = """
        SELECT 
            pl_name, 
            pl_orbper, 
            pl_rade, 
            pl_masse, 
            st_dist, 
            st_teff, 
            st_rad, 
            st_mass,
            disc_year,
            pl_eqt,
            pl_orbsmax,
            sy_snum,
            sy_pnum
        FROM ps 
        WHERE 
            pl_rade IS NOT NULL 
            AND pl_masse IS NOT NULL 
            AND st_dist IS NOT NULL 
            AND st_dist < 100
            AND pl_rade < 5
            AND pl_masse < 20
        ORDER BY st_dist ASC
        """
        
        params = {
            'request': 'doQuery',
            'lang': 'adql',
            'query': query,
            'format': 'csv'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Carrega os dados em DataFrame
            self.data = pd.read_csv(StringIO(response.text))
            print(f"✅ {len(self.data)} exoplanetas carregados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados: {e}")
            print("📊 Usando dados de exemplo...")
            self._create_sample_data()
            return False
    
    def _create_sample_data(self):
        """Cria dados de exemplo baseados em exoplanetas reais conhecidos"""
        sample_data = {
            'pl_name': [
                'Proxima Cen b', 'TRAPPIST-1 e', 'TRAPPIST-1 f', 'TRAPPIST-1 g',
                'TOI-715 b', 'K2-18 b', 'LHS 1140 b', 'Kepler-442 b',
                'Wolf 1061 c', 'Gliese 667C c', 'HD 40307 g', 'Kepler-186 f',
                'Kepler-452 b', 'TOI-849 b', 'GJ 357 d'
            ],
            'pl_rade': [1.1, 0.91, 1.04, 1.13, 1.55, 2.61, 1.43, 1.34, 1.6, 1.5, 1.9, 1.11, 1.63, 3.4, 1.7],
            'pl_masse': [1.27, 0.62, 0.68, 1.34, 3.02, 8.63, 6.6, 2.36, 4.3, 3.8, 7.1, 1.44, 5.0, 39.1, 6.1],
            'st_dist': [4.24, 39.5, 39.5, 39.5, 137, 124, 41, 1120, 13.8, 23.6, 42, 561, 1800, 150, 31],
            'st_teff': [3042, 2566, 2566, 2566, 3650, 2631, 3216, 4402, 3342, 3700, 4977, 3755, 5757, 4500, 3500],
            'disc_year': [2016, 2017, 2017, 2017, 2024, 2015, 2017, 2015, 2015, 2011, 2012, 2014, 2015, 2020, 2019],
            'pl_eqt': [234, 251, 219, 198, 300, 279, 230, 233, 223, 277, 320, 188, 265, 1800, 202],
            'pl_orbsmax': [0.0485, 0.0282, 0.0371, 0.0451, 0.083, 0.143, 0.0946, 0.409, 0.084, 0.125, 0.6, 0.432, 1.05, 0.0156, 0.204],
            'sy_pnum': [1, 7, 7, 7, 2, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3]
        }
        
        self.data = pd.DataFrame(sample_data)
        print(f"📊 {len(self.data)} exoplanetas de exemplo carregados!")
    
    def calculate_habitability_score(self):
        """Calcula um score de habitabilidade baseado em múltiplos fatores"""
        if self.data is None:
            print("❌ Dados não carregados!")
            return
        
        # Cria uma cópia para trabalhar
        df = self.data.copy()
        
        # Score baseado em raio (planetas terrestres: 0.5-1.5 R⊕)
        radius_score = np.where(
            (df['pl_rade'] >= 0.5) & (df['pl_rade'] <= 1.5), 1.0,
            np.where(
                (df['pl_rade'] >= 0.3) & (df['pl_rade'] <= 2.0), 0.7,
                np.where(df['pl_rade'] <= 3.0, 0.4, 0.1)
            )
        )
        
        # Score baseado em massa (planetas terrestres: 0.1-5 M⊕)
        mass_score = np.where(
            (df['pl_masse'] >= 0.1) & (df['pl_masse'] <= 5), 1.0,
            np.where(
                (df['pl_masse'] >= 0.05) & (df['pl_masse'] <= 10), 0.7,
                np.where(df['pl_masse'] <= 15, 0.4, 0.1)
            )
        )
        
        # Score baseado em temperatura (zona habitável: 175-320 K)
        temp_score = np.where(
            (df['pl_eqt'] >= 175) & (df['pl_eqt'] <= 320), 1.0,
            np.where(
                (df['pl_eqt'] >= 150) & (df['pl_eqt'] <= 400), 0.7,
                np.where(
                    (df['pl_eqt'] >= 100) & (df['pl_eqt'] <= 500), 0.4, 0.1
                )
            )
        )
        
        # Score baseado na distância (planetas próximos são mais estudáveis)
        distance_score = np.where(
            df['st_dist'] <= 20, 1.0,
            np.where(
                df['st_dist'] <= 50, 0.8,
                np.where(df['st_dist'] <= 100, 0.6, 0.3)
            )
        )
        
        # Calcula score final (média ponderada)
        df['habitability_score'] = (
            radius_score * 0.3 + 
            mass_score * 0.3 + 
            temp_score * 0.25 + 
            distance_score * 0.15
        )
        
        # Classifica os planetas
        df['classification'] = pd.cut(
            df['habitability_score'],
            bins=[0, 0.3, 0.6, 0.8, 1.0],
            labels=['Baixo', 'Moderado', 'Alto', 'Muito Alto'],
            include_lowest=True
        )
        
        self.data = df
        print("✅ Score de habitabilidade calculado!")
    
    def create_3d_visualization(self):
        """Cria visualização 3D interativa"""
        if self.data is None:
            print("❌ Dados não carregados!")
            return
        
        # Filtra dados para melhor visualização
        df_viz = self.data[
            (self.data['st_dist'] <= 200) & 
            (self.data['pl_rade'] <= 4) &
            (self.data['pl_masse'] <= 15)
        ].copy()
        
        # Cria o gráfico 3D
        fig = px.scatter_3d(
            df_viz,
            x='st_dist',
            y='pl_rade',
            z='pl_masse',
            color='habitability_score',
            size='pl_eqt',
            hover_name='pl_name',
            hover_data={
                'st_dist': ':.1f',
                'pl_rade': ':.2f',
                'pl_masse': ':.2f',
                'pl_eqt': ':.0f',
                'disc_year': True,
                'habitability_score': ':.2f'
            },
            color_continuous_scale='Viridis',
            title='🌍 Exoplanetas Potencialmente Habitáveis - Visualização 3D',
            labels={
                'st_dist': 'Distância (anos-luz)',
                'pl_rade': 'Raio (Terras)',
                'pl_masse': 'Massa (Terras)',
                'habitability_score': 'Score Habitabilidade'
            }
        )
        
        # Customiza o layout
        fig.update_layout(
            scene=dict(
                xaxis_title='Distância (anos-luz)',
                yaxis_title='Raio (Terras)',
                zaxis_title='Massa (Terras)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            width=900,
            height=700,
            title_x=0.5
        )
        
        fig.show()
        return fig
    
    def create_dashboard(self):
        """Cria um dashboard completo com múltiplas visualizações"""
        if self.data is None:
            print("❌ Dados não carregados!")
            return
        
        # Cria subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Distribuição por Distância',
                'Raio vs Massa',
                'Descobertas por Ano',
                'Score de Habitabilidade'
            ),
            specs=[
                [{"type": "histogram"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "box"}]
            ]
        )
        
        # 1. Histograma de distâncias
        fig.add_trace(
            go.Histogram(
                x=self.data['st_dist'],
                nbinsx=20,
                name='Distância',
                marker_color='skyblue'
            ),
            row=1, col=1
        )
        
        # 2. Scatter Raio vs Massa
        fig.add_trace(
            go.Scatter(
                x=self.data['pl_rade'],
                y=self.data['pl_masse'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.data['habitability_score'],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=self.data['pl_name'],
                name='Exoplanetas'
            ),
            row=1, col=2
        )
        
        # 3. Descobertas por ano
        discoveries_by_year = self.data['disc_year'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(
                x=discoveries_by_year.index,
                y=discoveries_by_year.values,
                name='Descobertas',
                marker_color='lightcoral'
            ),
            row=2, col=1
        )
        
        # 4. Box plot do score de habitabilidade por classificação
        fig.add_trace(
            go.Box(
                y=self.data['habitability_score'],
                x=self.data['classification'],
                name='Score',
                marker_color='lightgreen'
            ),
            row=2, col=2
        )
        
        # Atualiza layout
        fig.update_layout(
            height=800,
            title_text="🌌 Dashboard de Análise de Exoplanetas",
            title_x=0.5,
            showlegend=False
        )
        
        # Atualiza eixos
        fig.update_xaxes(title_text="Distância (anos-luz)", row=1, col=1)
        fig.update_xaxes(title_text="Raio (Terras)", row=1, col=2)
        fig.update_xaxes(title_text="Ano", row=2, col=1)
        fig.update_xaxes(title_text="Classificação", row=2, col=2)
        
        fig.update_yaxes(title_text="Frequência", row=1, col=1)
        fig.update_yaxes(title_text="Massa (Terras)", row=1, col=2)
        fig.update_yaxes(title_text="Número de Descobertas", row=2, col=1)
        fig.update_yaxes(title_text="Score de Habitabilidade", row=2, col=2)
        
        fig.show()
        return fig
    
    def generate_report(self):
        """Gera relatório estatístico detalhado"""
        if self.data is None:
            print("❌ Dados não carregados!")
            return
        
        print("=" * 60)
        print("🌍 RELATÓRIO DE ANÁLISE DE EXOPLANETAS")
        print("=" * 60)
        
        # Estatísticas gerais
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"• Total de exoplanetas analisados: {len(self.data)}")
        print(f"• Distância média: {self.data['st_dist'].mean():.1f} anos-luz")
        print(f"• Raio médio: {self.data['pl_rade'].mean():.2f} Terras")
        print(f"• Massa média: {self.data['pl_masse'].mean():.2f} Terras")
        
        # Top 10 mais próximos
        print(f"\n🚀 TOP 10 EXOPLANETAS MAIS PRÓXIMOS:")
        closest = self.data.nsmallest(10, 'st_dist')[['pl_name', 'st_dist', 'habitability_score']]
        for idx, row in closest.iterrows():
            print(f"• {row['pl_name']}: {row['st_dist']:.1f} anos-luz (Score: {row['habitability_score']:.2f})")
        
        # Top 10 score de habitabilidade
        print(f"\n🌱 TOP 10 MAIOR SCORE DE HABITABILIDADE:")
        habitable = self.data.nlargest(10, 'habitability_score')[['pl_name', 'habitability_score', 'st_dist']]
        for idx, row in habitable.iterrows():
            print(f"• {row['pl_name']}: Score {row['habitability_score']:.2f} ({row['st_dist']:.1f} anos-luz)")
        
        # Distribuição por classificação
        print(f"\n📈 DISTRIBUIÇÃO POR HABITABILIDADE:")
        classification_counts = self.data['classification'].value_counts()
        for category, count in classification_counts.items():
            percentage = (count / len(self.data)) * 100
            print(f"• {category}: {count} planetas ({percentage:.1f}%)")
        
        # Recomendações para observação de Natal/RN
        print(f"\n🔭 RECOMENDAÇÕES PARA OBSERVAÇÃO (NATAL/RN):")
        print("Baseado na proximidade e score de habitabilidade:")
        
        # Filtra planetas promissores e próximos
        promising = self.data[
            (self.data['st_dist'] <= 50) & 
            (self.data['habitability_score'] >= 0.5)
        ].sort_values(['habitability_score', 'st_dist'], ascending=[False, True])
        
        if len(promising) > 0:
            for idx, row in promising.head(5).iterrows():
                print(f"• {row['pl_name']}: {row['st_dist']:.1f} anos-luz, Score: {row['habitability_score']:.2f}")
        else:
            print("• Nenhum planeta próximo com alto score de habitabilidade encontrado")
        
        print("=" * 60)
    
    def save_data(self, filename='exoplanets_analysis.csv'):
        """Salva os dados analisados em CSV"""
        if self.data is None:
            print("❌ Dados não carregados!")
            return
        
        self.data.to_csv(filename, index=False)
        print(f"💾 Dados salvos em: {filename}")

def main():
    """Função principal - executa análise completa"""
    print("🌌 Iniciando Análise de Exoplanetas - NASA Data")
    print("=" * 50)
    
    # Inicializa o analisador
    analyzer = ExoplanetAnalyzer()
    
    # Busca dados da NASA
    analyzer.fetch_nasa_data()
    
    # Calcula score de habitabilidade
    analyzer.calculate_habitability_score()
    
    # Cria visualizações
    print("\n📊 Gerando visualizações...")
    analyzer.create_3d_visualization()
    analyzer.create_dashboard()
    
    # Gera relatório
    analyzer.generate_report()
    
    # Salva dados
    analyzer.save_data()
    
    print("\n✅ Análise completa finalizada!")
    print("🔬 Use as visualizações interativas para explorar os dados")

if __name__ == "__main__":
    main()