# Extrator de Metadados para Revisão Sistemática (ENW para Excel)

Este projeto foi desenvolvido para automatizar a coleta de DOIs, Título, Autor, Ano de Publicação e link, a partir de arquivos EndNote (.enw), auxiliando pesquisadores em Revisões Sistemáticas de Literatura (RSL).

## 🛡️ Rigor Científico e Responsabilidade
**Atenção:** Este script utiliza a API da CrossRef para buscar DOIs baseando-se no título do estudo. Para garantir a integridade dos dados acadêmicos:
* O script possui um **limite de confiança (Threshold)** ajustável.
* Campos de DOI e Título da API só são preenchidos se a similaridade entre o título original e o encontrado for superior ao limite definido (Padrão: 85%).
* **É responsabilidade do pesquisador revisar os resultados**, especialmente os campos deixados em branco pelo script.

## 🚀 Como Usar
1. Dentro do Google Acadêmico, salve todos os resultados de pesquisa > vá em Minha Biblioteca e exporte no formato **EndNote**.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Ajuste a variável `TAXA_SIMILARIDADE`, no código, se necessário.
4. Preencha a variável  `ARQUIVO_ENTRADA` com o nome do arquivo fonte (ex: citations.enw).
4. Execute o script: `extrator_rsl.py`.

## 🛠️ Tecnologias
* Python 3.x
* Pandas (Manipulação de dados)
* Habanero (Interface com API CrossRef)
* SequenceMatcher (Algoritmo de similaridade de strings)

## 👤 Autor
**Elizeu Lucio** - Estudante de Ciência da Computação (UNEMAT-ROO).
