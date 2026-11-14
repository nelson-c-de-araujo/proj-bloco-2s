# Relatório de Sumário de Dados - Projeto_Bloco_Etapa4
**Instituto Infnet | Aluno: Nelson C. de Araujo**

Este documento descreve as fontes de dados (estruturadas e não estruturadas), o fluxo de pré-processamento, as transformações e os arquivos mantidos no projeto para o monitoramento do **ODS 13 (Ação Contra a Mudança Global do Clima)**.

---

## 1. Fontes de Dados de Emissões e Concentração (Estruturados)

### 1.1. SEEG - Plataforma de Emissões por Estado (Ativa)
- **Origem:** Plataforma SEEG (`plataforma.seeg.eco.br`), com tabela dinâmica clusterizada por Unidade Federativa.
- **Coleta:** Script [`src/scrape_seeg_brasil.py`](../src/scrape_seeg_brasil.py), utilizando Selenium e Google Chrome em modo *headless* com sincronização explícita via `WebDriverWait` e `expected_conditions`.
- **Período Histórico:** 1990 a 2024 (anual).
- **Unidade de Medida:** Toneladas de CO₂ equivalente (t CO₂e).
- **Dimensões e Estrutura:** 27 Unidades Federativas (26 estados + Distrito Federal), 1 linha residual de emissões não regionalizadas ("Não Alocado") e 1 linha consolidada nacional ("Total").
- **Acesso e Consumo:** Consumido pelo painel Streamlit e por clientes externos via API RESTful (`GET /emissoes` e `POST /emissoes/sincronizar`).

### 1.2. Série Histórica de Concentração Atmosférica de CO₂ - NOAA Mauna Loa (Integrada)
- **Origem Oficial:** National Oceanic and Atmospheric Administration (NOAA) - Global Monitoring Laboratory (GML), Observatório de Mauna Loa, Havaí.
- **Coleta e Formato:** Arquivo tabular com medições mensais de concentração média em partes por milhão (ppm) e curva de tendência ajustada (dessazonalizada).
- **Período:** 2020 a 2024 (mensal).
- **Acesso e Consumo:** Disponibilizado pela API no endpoint `GET /co2` e consumido na página de Indicadores Globais do Streamlit.

### 1.3. Conjunto de Dados Próprios do Usuário (Upload CSV)
- **Tipo:** Arquivos CSV customizados carregados via `st.file_uploader`.
- **Flexibilidade:** Detecção automática de séries temporais com plotagem reativa.

---

## 2. Fontes de Notícias & Conteúdo Climático (Não Estruturados)

### 2.1. Web Scraping de Notícias (`src/scrape_news.py`)
- **Portais Monitorados:** Agência Brasil (editoria de Meio Ambiente / Mudanças Climáticas) e ONU News (tópico Mudança Climática).
- **Atributos Extraídos:** Data de publicação (`data`), veículo/fonte, título, resumo detalhado, link permanente e categoria temática.
- **Aprimoramento de Resumo e Data (Etapa 4):** Implementação de extração cronológica via tags `<time>`, metadados estruturados e padrões de URL, aliada à busca aprofundada em múltiplos níveis de ancestrais e leitura das meta tags (`meta[name="description"]` e `og:description`), garantindo resumos ricos e temporalidade precisa.
- **Acesso e Consumo:** Disponível na API via `GET /noticias`, `POST /noticias` (cadastro manual com data) e `POST /noticias/sincronizar` (gatilho de scraping).

---

## 3. Pipeline e Organização dos Arquivos (`data/`)

### 3.1. Dados Brutos (`data/raw/`)
| Arquivo | Origem | Descrição do Conteúdo |
|---|---|---|
| `noticias_ods13.csv` | Web Scraping / API `POST` | Data, título, resumo detalhado, link, veículo e categoria temática |
| `conteudo_ods13.txt` | Web Scraping / API | Texto corrido concatenado para análise semântica e lematização |
| `seeg_brasil_estados.csv` | Selenium + WebDriverWait | Matriz histórica de emissões estaduais (1990–2024) com pontuação brasileira |
| `co2_mensal_noaa.csv` | NOAA Mauna Loa GML | Série histórica real de concentrações atmosféricas mensais (ppm) |

### 3.2. Dados Processados (`data/processed/`)
| Arquivo | Processamento Aplicado | Uso Principal |
|---|---|---|
| `noticias_ods13_limpo.csv` | Normalização cronológica, limpeza textual de stopwords, pontuação e caracteres | Tabela filtrável por termo e data no painel |
| `texto_nuvem_palavras.txt` | Normalização, remoção de stopwords em PT e termos irrelevantes | Geração da Nuvem de Palavras (WordCloud) |
| `seeg_brasil_estados_limpo.csv` | Remoção de pontuação de milhar, conversão para float e imputação de nulos | Gráficos temporais, rankings estaduais e download |
| `co2_mensal_noaa_limpo.csv` | Tipagem numérica estrita de ppm e tendência dessazonalizada | Gráficos temporais na página de Indicadores Globais |

---

## 4. Métricas de Qualidade dos Dados (Auditoria Etapa 4)

| Indicador | Situação Etapa 3 | Situação Etapa 4 (Atual) |
|---|---|---|
| Unidades Federativas SEEG | 28 (incluía "Não Alocado") | **27 UFs estritas** (com nota explicativa para "Não Alocado") |
| Resumos Padrão Genéricos | 7 de 10 (70%) | **0%** (100% dos registros contam com resumos informativos reais) |
| Indicador de CO₂ | Demonstração sintética | **Série real oficial da NOAA (Mauna Loa)** |
| Protocolo de Acesso aos Dados | Leitura direta de CSV | **API RESTful HTTP (`requests.get` / `requests.post`)** |
| Espera no Web Scraping | `time.sleep(12)` estático | **`WebDriverWait` inteligente baseado em eventos DOM** |
