# Logbook pessoal de observacoes - cria uma entrada do dia na estrutura
# observacoes/AAAA/MM/AAAA-MM-DD.md, no mesmo repositorio Git deste script.
# Roda separado do Primeira Luz de proposito: esse aqui e so seu.

import os
from datetime import datetime

pasta_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'observacoes')

entrada_data = input('Data da observacao (AAAA-MM-DD, Enter para hoje): ').strip()
if entrada_data == '':
    data = datetime.now().date()
else:
    data = datetime.strptime(entrada_data, '%Y-%m-%d').date()

pasta_do_mes = os.path.join(pasta_base, str(data.year), '{:02d}'.format(data.month))
os.makedirs(pasta_do_mes, exist_ok=True)
caminho_arquivo = os.path.join(pasta_do_mes, data.strftime('%Y-%m-%d') + '.md')

if os.path.exists(caminho_arquivo):
    print('Ja existe uma entrada para essa data: ' + caminho_arquivo)
    print('Edite o arquivo direto se quiser complementar - o script nao sobrescreve entradas existentes.')
else:
    local = input('Local: ').strip()
    equipamento = input('Equipamento: ').strip()
    seeing = input('Seeing (1 a 5): ').strip()
    transparencia = input('Transparencia (1 a 5): ').strip()
    objetos_texto = input('Objetos observados (separados por virgula): ').strip()
    objetos = [nome.strip() for nome in objetos_texto.split(',') if nome.strip() != '']

    print('Observacoes (uma linha por observacao, linha em branco para terminar):')
    linhas_observacoes = []
    while True:
        linha = input('  ')
        if linha == '':
            break
        linhas_observacoes.append(linha)

    conteudo = '# ' + data.strftime('%Y-%m-%d') + '\n\n'
    conteudo += '## Local\n' + local + '\n\n'
    conteudo += '## Equipamento\n' + equipamento + '\n\n'
    conteudo += '## Seeing\n' + seeing + '/5\n\n'
    conteudo += '## Transparencia\n' + transparencia + '/5\n\n'
    conteudo += '## Objetos\n'
    for nome_objeto in objetos:
        conteudo += '- [x] ' + nome_objeto + '\n'
    conteudo += '\n## Observacoes\n'
    for linha in linhas_observacoes:
        conteudo += linha + '\n'

    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(conteudo)

    print('Entrada criada em: ' + caminho_arquivo)
