# Projeto_Bloco_EtapaTP2 - Instituto Infnet
**Aluno: Nelson C. de Araujo**  
**Projeto da Agenda 2030 - ODS 13: Ação Contra a Mudança Global do Clima**

---

## 1. Definição do Problema de Negócio & Objetivos do TP2

**Problema:** Muitas organizações e gestores não dispõem de ferramentas dinâmicas e acessíveis para acompanhar suas emissões de gases de efeito estufa e monitorar as principais discussões climáticas globais.

**Objetivo Geral:** Evoluir a solução desenvolvida no TP1, transformando o protótipo inicial em um painel interativo, de alta performance e resiliente, capaz de integrar dados de séries temporais de CO₂, matérias de veículos oficiais via Web Scraping e serviços de upload/download de dados de emissões.

**Metas para o Sucesso no TP2:**
- Interface de usuário interativa e intuitiva construída em Streamlit com navegação por abas.
- Módulo de extração independente via Web Scraping usando `BeautifulSoup` para monitoramento de notícias climáticas.
- Processamento e geração de **Nuvem de Palavras (WordCloud)** a partir do compilado textual raspado.
- Alta performance da aplicação utilizando decoradores de cache (`@st.cache_data`) e gerenciamento de estado (`st.session_state`).
- Funcionalidade completa de **Upload** de arquivos CSV personalizados e **Download** de relatórios filtrados.

---

## 2. Metodologia e Ciclo de Vida do Projeto (TDSP / CRISP-DM)

O projeto segue a estrutura do **Team Data Science Process (TDSP)**:

1. **Business Understanding (`docs/BusinessUnderstanding/`):** Alinhamento dos objetivos com as metas do ODS 13 e mapeamento dos requisitos de usabilidade.
2. **Data Understanding (`docs/DataUnderstanding/`):** Identificação das fontes de emissões (NOAA GML) e de dados não estruturados de notícias (Agência Brasil e ONU News).
3. **Data Preparation (`docs/DataPreparation/`):** Desenvolvimento de scripts independentes para Web Scraping (`src/scrape_news.py`) e limpeza/tratamento de stopwords (`src/process_data.py`).
4. **Modeling & Analytics (`docs/Modeling/`):** Agregação de métricas estatísticas e geração visual de nuvem de palavras.
5. **Deployment (`docs/Deployment/`):** Publicação e otimização da aplicação web interativa em Streamlit (`code/app.py`).
6. **Customer Acceptance (`docs/Acceptance/`):** Validação dos serviços de upload/download de arquivos CSV e facilidade de navegação com os stakeholders.

---

## 3. Estrutura Atualizada do Repositório

```
Projeto_Bloco_EtapaTP2/
|-- data/                       # Armazenamento de dados
|   |-- raw/                    # Dados brutos (noticias_ods13.csv e conteudo_ods13.txt)
|   |-- processed/              # Dados limpos (noticias_ods13_limpo.csv e texto_nuvem_palavras.txt)
|-- docs/                       # Documentação organizada pelas fases do TDSP
|   |-- BusinessUnderstanding/
|   |-- DataUnderstanding/
|   |-- DataPreparation/
|   |-- Modeling/
|   |-- Deployment/
|   |-- Acceptance/
| |-- models/                     # Modelos e artefatos serializados
|-- src/                        # Scripts independentes do pipeline de dados
|   |-- scrape_news.py          # Script de Web Scraping (BeautifulSoup)
|   |-- process_data.py         # Script de limpeza de texto e stopwords
|-- code/                       # Aplicação principal Streamlit
|   |-- app.py                  # Dashboard interativo com cache, sessão, upload/download
|-- artifacts/                  # Artefatos da documentação do projeto
|   |-- project_charter.md
|   |-- data_summary_report.md
|-- requirements.txt            # Dependências Python (streamlit, pandas, bs4, wordcloud, etc.)
|-- README.md                   # Visão geral do repositório
```

---

## 4. Principais Avanços Técnicos no TP2

- **Navegação & Interatividade:** Estruturação por abas ("Indicadores de Emissão" e "Panorama de Notícias & Temas em Alta").
- **Filtros Personalizados na Sidebar:** Filtro de período por mês (`multiselect`) e campo de pesquisa por palavra-chave para notícias com salvamento no `st.session_state`.
- **Serviço de Dados Próprios:** Leitura de arquivos CSV locais do usuário com renderização automática da tabela e do gráfico de linhas abaixo da tabela.
- **Resiliência:** Mecanismo de fallback para a raspagem de dados caso haja falha de conexão com os sites oficiais.