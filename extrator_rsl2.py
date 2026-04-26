import pandas as pd
import requests
import time
import os
import glob
from difflib import SequenceMatcher

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================
TAXA_SIMILARIDADE = 0.85
PASTA_ARQUIVOS = './arq_enw' # Crie uma pasta e coloque os .enw dentro
ARQUIVO_SAIDA = 'resultado_rsl_total.xlsx'
# ==========================================================

def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def reconstruir_resumo(inverted_index):
    if not inverted_index: return ""
    word_index = [(word, pos) for word, positions in inverted_index.items() for pos in positions]
    word_index.sort(key=lambda x: x[1])
    return " ".join([x[0] for x in word_index])

def buscar_openalex(titulo_original):
    if not titulo_original: return "", 0, "", ""
    url = f"https://api.openalex.org/works?filter=title.search:{titulo_original}&limit=1"
    try:
        response = requests.get(url).json()
        if 'results' in response and response['results']:
            item = response['results'][0]
            doi = item.get('doi', "").replace("https://doi.org/", "")
            titulo_api = item.get('title', "")
            resumo = reconstruir_resumo(item.get('abstract_inverted_index', {}))
            score = similaridade(titulo_original, titulo_api)
            if score >= TAXA_SIMILARIDADE:
                return doi, round(score * 100, 2), titulo_api, resumo
    except: pass
    return "", 0, "", ""

def processar_multiplos_arquivos():
    # Busca todos os arquivos .enw na pasta selecionada
    arquivos = glob.glob(os.path.join(PASTA_ARQUIVOS, "*.enw"))
    
    if not arquivos:
        print(f"Nenhum arquivo .enw encontrado na pasta '{PASTA_ARQUIVOS}'.")
        return

    print(f"Encontrados {len(arquivos)} arquivos para processar.")
    lista_final = []
    total_estudos = 0

    for arquivo in arquivos:
        print(f"\n--- Lendo arquivo: {os.path.basename(arquivo)} ---")
        
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()
        
        referencias = [r.strip() for r in conteudo.split('%0') if r.strip()]
        
        for ref in referencias:
            extraido = {'ANO': '', 'TITULO': '', 'AUTORES': [], 'URL_ENW': ''}
            linhas = ref.strip().split('\n')
            
            for linha in linhas:
                tag = linha[:2]
                valor = linha[3:].strip()
                if tag == '%T': extraido['TITULO'] = valor
                elif tag == '%D': extraido['ANO'] = valor
                elif tag == '%A': extraido['AUTORES'].append(valor)
                elif tag == '%U': extraido['URL_ENW'] = valor
            
            total_estudos += 1
            print(f"Processando estudo {total_estudos}...")
            
            doi, score, tit_api, resumo = buscar_openalex(extraido['TITULO'])
            
            lista_final.append({
                'ARQUIVO_ORIGEM': os.path.basename(arquivo),
                'TAXA SIMILARIDADE (%)': score,
                'DOI': doi,
                'RESUMO': resumo,
                'AUTORES': "; ".join(extraido['AUTORES']),
                'TÍTULO ORIGINAL': extraido['TITULO'],
                'ANO': extraido['ANO'],
                'LINK ACESSO': f"https://doi.org/{doi}" if doi else extraido['URL_ENW']
            })
            time.sleep(0.1) # Breve pausa para API

    # Gerar planilha única com tudo
    df = pd.DataFrame(lista_final)
    df.to_excel(ARQUIVO_SAIDA, index=False)
    print(f"\nFIM! Processados {total_estudos} estudos de {len(arquivos)} arquivos.")
    print(f"Planilha consolidada salva em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    processar_multiplos_arquivos()