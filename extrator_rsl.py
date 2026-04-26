import pandas as pd
from habanero import Crossref
import time
from difflib import SequenceMatcher
import glob
import os

# ==========================================================
# CONFIGURAÇÕES DO PESQUISADOR (Editável)
# ==========================================================
TAXA_SIMILARIDADE = 0.85  #Ex: 0.85 (85%) | 1.0 (100%)
pasta = "C:/Users/elize/Documents/Repositórios/Extrator_de_Metadados_para_Revisao_Sistematica_da_Literatura"
ARQUIVO_ENTRADA = glob.glob(os.path.join(pasta ,'*.enw'))
ARQUIVO_SAIDA = 'resultado_rsl.xlsx'
# ==========================================================

cr = Crossref()

def similaridade(a, b):
    #Calcula a similaridade entre os títulos (0.0 a 1.0).
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def formatar_nome(nome_sujo):
    #Converte 'Sobrenome, Nome' para 'Nome Sobrenome'.
    nome = nome_sujo.strip()
    if ',' in nome:
        partes = nome.split(',')
        return f"{partes[1].strip()} {partes[0].strip()}"
    return nome

def buscar_metadados_com_trava(titulo_original):
    #Busca o DOI e valida contra o limite de confiança do pesquisador.
    if not titulo_original:
        return "", 0, ""
    try:
        res = cr.works(query=titulo_original, limit=1)
        if res['message']['items']:
            item = res['message']['items'][0]
            doi_encontrado = item.get('DOI', "")
            titulo_api = item.get('title', [''])[0]
            
            score = similaridade(titulo_original, titulo_api)
            
            # Só preenche se atingir o limite
            if score >= TAXA_SIMILARIDADE:
                return doi_encontrado, round(score * 100, 2), titulo_api
            else:
                # Se não atingir, retorna o score para transparência, mas campos de dados vazios
                return "", round(score * 100, 2), ""
    except Exception:
        pass
    return "", 0, ""

def executar_pipeline_rsl(arquivo_in, arquivo_out):
    try:
        with open(arquivo_in, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_in}' não foi encontrado.")
        return

    referencias = conteudo.split('%0')
    lista_final = []

    print(f"Pipeline iniciado | Rigor de Confiança: {TAXA_SIMILARIDADE*100}%")

    for i, ref in enumerate(referencias):
        if not ref.strip(): continue
        
        # Dicionário temporário para extração do arquivo ENW
        extraido = {'ANO': '', 'TITULO': '', 'AUTORES': [], 'URL_ENW': ''}
        linhas = ref.strip().split('\n')
        
        for linha in linhas:
            if linha.startswith('%T'): extraido['TITULO'] = linha[3:].strip()
            elif linha.startswith('%D'): extraido['ANO'] = linha[3:].strip()
            elif linha.startswith('%A'): extraido['AUTORES'].append(formatar_nome(linha[3:]))
            elif linha.startswith('%U'): extraido['URL_ENW'] = linha[3:].strip()
        
        autores_formatados = "; ".join(extraido['AUTORES'])
        
        # Consulta API com a trava lógica solicitada
        doi, score, titulo_validado = buscar_metadados_com_trava(extraido['TITULO'])
        
        # Se houver DOI validado, gera link DOI. Se não, usa o URL do ENW (se houver).
        link_final = f"https://doi.org/{doi}" if doi else extraido['URL_ENW']
        
        lista_final.append({
            'TAXA DE SIMILARIDADE (%)': score,
            'DOI': doi,
            'TÍTULO ENCONTRADO (API)': titulo_validado,
            'AUTORES': autores_formatados,
            'TÍTULO ORIGINAL': extraido['TITULO'],
            'ANO': extraido['ANO'],
            'LINK ACESSO': link_final
        })
        
        status = "✅ OK" if doi else "❌ ABAIXO DO LIMITE"
        print(f"[{i+1}/380] {status} | Similaridade: {score}% | {extraido['TITULO'][:40]}...")
        
        time.sleep(0.4) # Proteção contra bloqueio de IP

    # Gerar planilha final
    df = pd.DataFrame(lista_final)
    df.to_excel(arquivo_out, index=False)
    print(f"\nProcessamento concluído. Planilha salva como: {arquivo_out}")

# Rodar o código
# Rodar o código
if __name__ == "__main__":
    arquivos_enw = glob.glob('*.enw')
    
    if not arquivos_enw:
        print("Nenhum arquivo .enw encontrado no diretório.")
    else:
        for arquivo in arquivos_enw:
            print(f"\n--- Iniciando processamento do arquivo: {arquivo} ---")
            # Define um nome de saída baseado no nome do arquivo original
            nome_saida = arquivo.replace('.enw', '_resultado.xlsx')
            executar_pipeline_rsl(arquivo, nome_saida)