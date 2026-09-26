# Relatório de Sumário de Dados - Projeto_Bloco_EtapaTP2
**Instituto Infnet | Aluno: Nelson C. de Araujo**

Este documento descreve todas as fontes de dados (estruturadas e não estruturadas), o fluxo de pré-processamento e os artefatos de dados mantidos no projeto para o monitoramento do **ODS 13 (Ação Contra a Mudança Global do Clima)**.

---

## 1. Fontes de Dados de Emissões de CO₂ (Estruturados)

### 1.1. NOAA Climate Data - Global Monitoring Laboratory (GML)
- **Tipo:** Série temporal de concentração de CO₂ atmosférico (Curva de Keeling e Média Global).
- **Formato:** CSV / Estruturado.
- **Licença:** Domínio Público / NOAA Open Data.
- **Uso na Aplicação:** Leitura de médias mensais em ppm (partes por milhão) e tendências dessazonalizadas para visualização tabular e em gráficos de linha.

### 1.2. Conjunto de Dados Próprios do Usuário (Upload CSV)
- **Tipo:** Arquivos CSV carregados dinamicamente via interface web (`st.file_uploader`).
- **Formato:** CSV contendo ao menos as colunas `Data de Registro` e `Nível de CO2 (ppm)`.
- **Uso na Aplicação:** Permite que empresas e pesquisadores visualizem instantaneamente suas próprias medições de emissões em tabela e gráfico.

---

## 2. Fontes de Dados de Notícias & Conteúdo Climático (Não Estruturados)

### 2.1. Web Scraping via BeautifulSoup (`src/scrape_news.py`)
- **Fontes Coletadas:** Agência Brasil (Editoria de Meio Ambiente) e ONU News (Tópico de Mudanças Climáticas).
- **Dados Extraídos:** Título da matéria, resumo/parágrafo, link oficial e nome do veículo.
- **Mecanismo de Resiliência:** Caso haja indisponibilidade temporária das páginas raspadas, o script ativa um conjunto de conteúdos institucionais das Nações Unidas e do IPCC para garantir o funcionamento contínuo do sistema.

---

## 3. Pipeline e Arquivos Gerados (`data/`)

O fluxo de dados é segregado em duas etapas dentro do padrão TDSP:

### 3.1. Dados Brutos (`data/raw/`)
- `noticias_ods13.csv`: Arquivo estruturado com os dados brutos obtidos do scraping.
- `conteudo_ods13.txt`: Compilado de texto bruto contendo a junção de títulos e parágrafos.

### 3.2. Dados Processados (`data/processed/`)
- `noticias_ods13_limpo.csv`: Dataset limpo e formatado para a exibição na tabela interativa da aplicação.
- `texto_nuvem_palavras.txt`: Arquivo de texto tratado através do script `src/process_data.py`, com remoção de *stopwords* em português, pontuações e caracteres especiais, utilizado diretamente para a geração visual da **Nuvem de Palavras (WordCloud)**.
