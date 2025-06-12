import math
from datetime import datetime

def calcular_peso(massa_kg, gravidade):
    """Calcula o peso (força gravitacional) dado massa e gravidade"""
    return massa_kg * gravidade

def calcular_velocidade_escape(gravidade, raio_m):
    """Calcula a velocidade de escape de um corpo celeste"""
    return math.sqrt(2 * gravidade * raio_m)

def tempo_queda_livre(altura_m, gravidade):
    """Calcula o tempo para um objeto cair de uma altura específica"""
    return math.sqrt(2 * altura_m / gravidade)

def main():
    print("=" * 70)
    print("🌌 CALCULADORA INTERPLANETÁRIA DE PESO E FÍSICA 🌌")
    print("=" * 70)
    
    # Massa do usuário (em kg)
    while True:
        try:
            massa = float(input("\n📏 Digite sua massa em kg: "))
            if massa <= 0:
                print("⚠️  Por favor, digite uma massa positiva!")
                continue
            break
        except ValueError:
            print("⚠️  Por favor, digite um número válido!")
    
    # Dados completos dos corpos celestes
    corpos_celestes = {
        "☿️ Mercúrio": {
            "gravidade": 3.7,
            "raio_km": 2439.7,
            "massa_kg": 3.301e23,
            "temp_media": 167,
            "distancia_sol": 57.9,
            "curiosidade": "Um dia em Mercúrio dura 176 dias terrestres!"
        },
        "♀️ Vênus": {
            "gravidade": 8.87,
            "raio_km": 6051.8,
            "massa_kg": 4.867e24,
            "temp_media": 464,
            "distancia_sol": 108.2,
            "curiosidade": "Vênus gira no sentido contrário aos outros planetas!"
        },
        "🌍 Terra": {
            "gravidade": 9.807,
            "raio_km": 6371,
            "massa_kg": 5.972e24,
            "temp_media": 15,
            "distancia_sol": 149.6,
            "curiosidade": "O único planeta conhecido com vida!"
        },
        "🌙 Lua": {
            "gravidade": 1.62,
            "raio_km": 1737.4,
            "massa_kg": 7.342e22,
            "temp_media": -20,
            "distancia_sol": 149.6,
            "curiosidade": "A Lua se afasta da Terra 3,8 cm por ano!"
        },
        "♂️ Marte": {
            "gravidade": 3.721,
            "raio_km": 3389.5,
            "massa_kg": 6.39e23,
            "temp_media": -65,
            "distancia_sol": 227.9,
            "curiosidade": "Marte tem as maiores tempestades de poeira do Sistema Solar!"
        },
        "♃ Júpiter": {
            "gravidade": 24.79,
            "raio_km": 69911,
            "massa_kg": 1.898e27,
            "temp_media": -110,
            "distancia_sol": 778.5,
            "curiosidade": "Júpiter tem mais de 80 luas conhecidas!"
        },
        "♄ Saturno": {
            "gravidade": 10.44,
            "raio_km": 58232,
            "massa_kg": 5.683e26,
            "temp_media": -140,
            "distancia_sol": 1432,
            "curiosidade": "Saturno é menos denso que a água - flutuaria!"
        },
        "♅ Urano": {
            "gravidade": 8.69,
            "raio_km": 25362,
            "massa_kg": 8.681e25,
            "temp_media": -195,
            "distancia_sol": 2867,
            "curiosidade": "Urano 'rola' de lado - seu eixo está inclinado 98°!"
        },
        "♆ Netuno": {
            "gravidade": 11.15,
            "raio_km": 24622,
            "massa_kg": 1.024e26,
            "temp_media": -200,
            "distancia_sol": 4515,
            "curiosidade": "Os ventos em Netuno chegam a 2.100 km/h!"
        },
        "🪐 Plutão": {
            "gravidade": 0.62,
            "raio_km": 1188.3,
            "massa_kg": 1.309e22,
            "temp_media": -230,
            "distancia_sol": 5906,
            "curiosidade": "Plutão ainda não completou uma órbita desde sua descoberta!"
        }
    }
    
    # Peso na Terra para referência
    peso_terra = calcular_peso(massa, corpos_celestes["🌍 Terra"]["gravidade"])
    
    print(f"\n🌍 Seu peso na Terra: {peso_terra:.2f} N ({peso_terra/9.807:.1f} kg)")
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO COMPLETO - SEU PESO EM DIFERENTES MUNDOS")
    print("=" * 70)
    
    for nome, dados in corpos_celestes.items():
        peso = calcular_peso(massa, dados["gravidade"])
        relacao = peso / peso_terra
        vel_escape = calcular_velocidade_escape(dados["gravidade"], dados["raio_km"] * 1000)
        tempo_queda = tempo_queda_livre(10, dados["gravidade"])  # tempo para cair 10m
        
        print(f"\n{nome}")
        print("-" * 50)
        print(f"⚖️  Seu peso: {peso:.2f} N ({relacao:.2f}× o peso da Terra)")
        print(f"🌡️  Temperatura média: {dados['temp_media']}°C")
        print(f"📏 Raio: {dados['raio_km']:,} km")
        print(f"🚀 Velocidade de escape: {vel_escape/1000:.2f} km/s")
        print(f"⏱️  Tempo para cair 10m: {tempo_queda:.2f} segundos")
        print(f"☀️  Distância do Sol: {dados['distancia_sol']:,} milhões de km")
        print(f"💡 Curiosidade: {dados['curiosidade']}")
    
    # Análises interessantes
    print("\n" + "=" * 70)
    print("🔍 ANÁLISES INTERESSANTES")
    print("=" * 70)
    
    # Onde você seria mais leve/pesado
    pesos = {nome: calcular_peso(massa, dados["gravidade"]) for nome, dados in corpos_celestes.items()}
    mais_leve = min(pesos, key=pesos.get)
    mais_pesado = max(pesos, key=pesos.get)
    
    print(f"\n🪶 Você seria mais LEVE em: {mais_leve}")
    print(f"   Pesaria apenas {pesos[mais_leve]:.2f} N ({pesos[mais_leve]/peso_terra:.1%} do seu peso na Terra)")
    
    print(f"\n🏋️ Você seria mais PESADO em: {mais_pesado}")
    print(f"   Pesaria {pesos[mais_pesado]:.2f} N ({pesos[mais_pesado]/peso_terra:.1f}× seu peso na Terra)")
    
    # Simulação de salto
    altura_salto_terra = 0.5  # assumindo um salto de 50cm na Terra
    print(f"\n🦘 SIMULAÇÃO DE SALTO (assumindo que você salta {altura_salto_terra}m na Terra):")
    print("-" * 50)
    
    for nome, dados in corpos_celestes.items():
        relacao_grav = dados["gravidade"] / corpos_celestes["🌍 Terra"]["gravidade"]
        altura_salto = altura_salto_terra / relacao_grav
        print(f"{nome}: {altura_salto:.2f} m de altura")
    
    # Estatísticas finais
    print(f"\n📈 ESTATÍSTICAS:")
    print("-" * 30)
    print(f"🌡️  Lugar mais quente: ♀️ Vênus ({corpos_celestes['♀️ Vênus']['temp_media']}°C)")
    print(f"🧊 Lugar mais frio: 🪐 Plutão ({corpos_celestes['🪐 Plutão']['temp_media']}°C)")
    print(f"🔴 Maior gravidade: ♃ Júpiter ({corpos_celestes['♃ Júpiter']['gravidade']} m/s²)")
    print(f"🟢 Menor gravidade: 🪐 Plutão ({corpos_celestes['🪐 Plutão']['gravidade']} m/s²)")
    
    print(f"\n⏰ Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print("\n🌌 Obrigado por explorar o Sistema Solar conosco! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()