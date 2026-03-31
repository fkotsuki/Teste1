import requests
import pandas as pd
import json
import os 
import time

## WebScraping AVAMEC FTV|IN BRASIL Competências Digitais ##
## Autor: Felipe K. Otsuki
## Data: 22/10/2025

# URL base da API
base_url = "https://avamec.mec.gov.br/ava-mec-ws/sistema"

# 1. LISTA DE TODOS OS ESTADOS DO BRASIL (com códigos e nomes/siglas do IBGE)
estados_brasil = [
    {'id': 12, 'nome': 'Acre', 'sigla': 'AC'}, {'id': 27, 'nome': 'Alagoas', 'sigla': 'AL'},
    {'id': 16, 'nome': 'Amapá', 'sigla': 'AP'}, {'id': 13, 'nome': 'Amazonas', 'sigla': 'AM'},
    {'id': 29, 'nome': 'Bahia', 'sigla': 'BA'}, {'id': 23, 'nome': 'Ceará', 'sigla': 'CE'},
    {'id': 53, 'nome': 'Distrito Federal', 'sigla': 'DF'}, {'id': 32, 'nome': 'Espírito Santo', 'sigla': 'ES'},
    {'id': 52, 'nome': 'Goiás', 'sigla': 'GO'}, {'id': 21, 'nome': 'Maranhão', 'sigla': 'MA'},
    {'id': 51, 'nome': 'Mato Grosso', 'sigla': 'MT'}, {'id': 50, 'nome': 'Mato Grosso do Sul', 'sigla': 'MS'},
    {'id': 31, 'nome': 'Minas Gerais', 'sigla': 'MG'}, {'id': 15, 'nome': 'Pará', 'sigla': 'PA'},
    {'id': 25, 'nome': 'Paraíba', 'sigla': 'PB'}, {'id': 41, 'nome': 'Paraná', 'sigla': 'PR'},
    {'id': 26, 'nome': 'Pernambuco', 'sigla': 'PE'}, {'id': 22, 'nome': 'Piauí', 'sigla': 'PI'},
    {'id': 33, 'nome': 'Rio de Janeiro', 'sigla': 'RJ'}, {'id': 24, 'nome': 'Rio Grande do Norte', 'sigla': 'RN'},
    {'id': 43, 'nome': 'Rio Grande do Sul', 'sigla': 'RS'}, {'id': 11, 'nome': 'Rondônia', 'sigla': 'RO'},
    {'id': 14, 'nome': 'Roraima', 'sigla': 'RR'}, {'id': 42, 'nome': 'Santa Catarina', 'sigla': 'SC'},
    {'id': 35, 'nome': 'São Paulo', 'sigla': 'SP'}, {'id': 28, 'nome': 'Sergipe', 'sigla': 'SE'},
    {'id': 17, 'nome': 'Tocantins', 'sigla': 'TO'}
]

# Lista para armazenar os resultados por município/estado
resultados_geograficos = []

# Cabeçalhos para a requisição POST (necessários para simular um navegador)
headers = {
    "Content-Type": "application/json;charset=UTF-8"
}

# Payload padrão para requisições nacionais consolidadas
payload_nacional = {
    "anos": [2025],
    "participantes": [],
    "esferasAdministrativas": [],
    "estado": None, # Indica 'null' (Brasil todo)
    "municipio": None # Indica 'null' (Brasil todo)
}

# ==============================================================================
# 2. FUNÇÕES PARA COLETAR DADOS NACIONAIS CONSOLIDADOS (GÊNERO e ESFERA)
# ==============================================================================

def obter_dados_por_genero():
    """Busca os dados de Participantes por Gênero para o Brasil todo."""
    
    print("Iniciando coleta de dados por GÊNERO...")
    url_genero = f"{base_url}/ferramenta/autodiagnostico/resolucao/relatorio/dados-participantes-por-genero/obtem"
    
    try:
        response = requests.post(url_genero, json=payload_nacional, headers=headers)
        response.raise_for_status() 
        dados_genero = response.json()
        
        # Estrutura esperada: lista de dicionários com chaves como 'genero', 
        # 'professoresEducacaoBasica', 'demaisParticipantes'
        df_genero = pd.DataFrame(dados_genero)
        df_genero.rename(columns={
            'genero': 'Gênero',
            'professoresEducacaoBasica': 'Professores de Educação Básica',
            'demaisParticipantes': 'Demais Participantes'
        }, inplace=True)
        
        print("Dados de GÊNERO coletados com sucesso.")
        return df_genero
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados por Gênero: {e}")
        return pd.DataFrame()

def obter_dados_por_esfera_administrativa():
    """Busca os dados de Respostas por Esfera Administrativa para o Brasil todo."""
    
    print("Iniciando coleta de dados por ESFERA ADMINISTRATIVA...")
    # URL específica para Esfera Administrativa
    url_esfera = f"{base_url}/ferramenta/autodiagnostico/resolucao/relatorio/respostas-por-esfera-administrativa/obtem"
    
    try:
        response = requests.post(url_esfera, json=payload_nacional, headers=headers)
        response.raise_for_status() 
        dados_esfera = response.json()
        
        # Estrutura esperada: lista de dicionários com chaves como 'esferaAdministrativa', 
        # 'professoresEducacaoBasica', 'demaisParticipantes'
        df_esfera = pd.DataFrame(dados_esfera)
        df_esfera.rename(columns={
            'esferaAdministrativa': 'Esfera Administrativa',
            'professoresEducacaoBasica': 'Professores de Educação Básica',
            'demaisParticipantes': 'Demais Participantes'
        }, inplace=True)
        
        print("Dados de ESFERA ADMINISTRATIVA coletados com sucesso.")
        return df_esfera
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados por Esfera Administrativa: {e}")
        return pd.DataFrame()

# ==============================================================================
# 3. FUNÇÃO PARA COLETAR DADOS GEOGRÁFICOS (MUNICÍPIO/ESTADO)
#    (Seu código original, reembalado em uma função)
# ==============================================================================

def obter_dados_geograficos(estados_brasil):
    """Coleta dados gerais por Estado e Município."""
    
    resultados_geograficos = []
    
    for estado_atual in estados_brasil:
        id_estado = estado_atual['id']
        nome_estado = estado_atual['nome']
        sigla_estado = estado_atual['sigla']

        print(f"Iniciando coleta de dados para o estado: {nome_estado}...")
        
        # 3.1 Obtém a lista de municípios (Requisição GET)
        municipios_url = f"{base_url}/estado/{id_estado}/municipio/lista"
        try:
            response_municipios = requests.get(municipios_url)
            response_municipios.raise_for_status()
            municipios = response_municipios.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter a lista de municípios para {nome_estado}: {e}")
            continue

        # 3.2 Itera sobre cada município
        for municipio in municipios:
            # Corpo da requisição POST específico para o município
            body = {
                "anos": [2025],
                "participantes": [],
                "esferasAdministrativas": [],
                "estado": {"id": id_estado, "nome": nome_estado, "sigla": sigla_estado},
                "municipio": {"id": municipio['id'], "nome": municipio['nome']}
            }
            
            # URL para obter os dados gerais
            dados_gerais_url = f"{base_url}/ferramenta/autodiagnostico/resolucao/relatorio/dados-gerais/obtem"
            
            try:
                response_dados = requests.post(dados_gerais_url, json=body, headers=headers)
                response_dados.raise_for_status()
                dados = response_dados.json()
                
                # Extrai e organiza os dados da resposta
                resultado = {
                    "Estado": nome_estado,
                    "Sigla": sigla_estado,
                    "Municipio": municipio['nome'],
                    "Respostas enviadas para o autodiagnóstico": dados.get('qtdRespostas', 0),
                    "Professores da rede estadual": dados.get('estadual', 0),
                    "Professores da rede municipal": dados.get('municipal', 0),
                    "Professores das demais redes": dados.get('demaisRedes', 0),
                    "Outros participantes": dados.get('outros', 0)
                }
                resultados_geograficos.append(resultado)
                # time.sleep(0.1) # Pequeno atraso (opcional)

            except requests.exceptions.RequestException as e:
                print(f"Erro ao obter dados para o município: {municipio['nome']} em {nome_estado}. Erro: {e}")

        print(f"Dados do estado de {nome_estado} coletados com sucesso.")

    return pd.DataFrame(resultados_geograficos)


# ==============================================================================
# 4. EXECUÇÃO PRINCIPAL
# ==============================================================================

# Coleta dos dados
df_genero = obter_dados_por_genero()
df_esfera = obter_dados_por_esfera_administrativa()
df_geografico = obter_dados_geograficos(estados_brasil)

# Lista de DataFrames e nomes de arquivos
dataframes_para_salvar = [
    (df_geografico, "autodiagnostico_geografico_municipios.xlsx"),
    (df_genero, "autodiagnostico_nacional_genero.xlsx"),
    (df_esfera, "autodiagnostico_nacional_esfera_adm.xlsx")
]

# Define o diretório de destino e garante que ele exista
DIRETORIO_DESTINO = r"C:\Nova pasta" 

try:
    # Cria o diretório (e subdiretórios, se houver) se ele não existir.
    # 'exist_ok=True' evita erro se a pasta já existir.
    os.makedirs(DIRETORIO_DESTINO, exist_ok=True)
    print(f"Diretório de destino garantido: {DIRETORIO_DESTINO}")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível criar/acessar o diretório {DIRETORIO_DESTINO}. Verifique suas permissões. Erro: {e}")
    # Se o diretório não puder ser criado, o programa pode prosseguir, 
    # mas o salvamento falhará, o que será capturado no loop abaixo.

# Salva cada DataFrame em um arquivo Excel separado
print("\n--- Processo de Salvamento ---")
for df, nome_arquivo in dataframes_para_salvar:
    if not df.empty:
        # Cria o caminho completo
        caminho_completo = os.path.join(DIRETORIO_DESTINO, nome_arquivo)
        
        try:
            # Salva o DataFrame no caminho completo
            df.to_excel(caminho_completo, index=False)
            print(f"Dados salvos com sucesso no arquivo: {os.path.abspath(caminho_completo)}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo {nome_arquivo} no diretório {DIRETORIO_DESTINO}: {e}")
    else:
        print(f"Aviso: O DataFrame para '{nome_arquivo}' está vazio e não foi salvo.")

print("\n--- FIM ---")