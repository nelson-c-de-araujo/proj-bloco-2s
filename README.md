# Projeto_Bloco_EtapaTP3 - Monitor de Emissões & Ação Climática (ODS 13)

Este repositório contém a terceira etapa de desenvolvimento (`Projeto_Bloco_EtapaTP3`) da aplicação de monitoramento e análise de emissões e panorama climático, desenvolvida sob os frameworks **TDSP (Team Data Science Process)** e **CRISP-DM**, alinhada ao **ODS 13 (Ação Contra a Mudança Global do Clima)**.

## Novidades da Etapa (TP3)

1. **Arquitetura Multipage no Streamlit**:
   - Menu de navegação centralizado com divisão em páginas especializadas:
     - 🏠 **Visão Geral**: Contextualização do projeto, objetivos e indicadores consolidados.
     - 📈 **Indicadores Globais de CO₂**: Gráficos temporais de concentração (ppm) e médias.
     - 📰 **Panorama de Notícias & NLP**: Web scraping dinâmico e Nuvem de Palavras.
     - 🇧🇷 **SEEG - Emissões Brasil**: Página nacional com dados históricos (1990–2024) clusterizados por todos os Estados brasileiros extraídos da Plataforma SEEG via **Selenium**.
     - 📁 **Gestão de Arquivos & Dados**: Módulo de upload de CSVs customizados e download de relatórios.
2. **Web Scraping Dinâmico via Selenium (SEEG Brasil)**:
   - Módulo automatizado (`src/scrape_seeg_brasil.py`) que utiliza o Google Chrome em modo *headless* para acessar a Single Page Application da Plataforma SEEG com filtros dinâmicos na URL, interagindo com o contêiner `sticky-table` e extraindo a matriz histórica (1990–2024) de emissões de todos os 27 estados e total nacional.

## Estrutura do Repositório (Padrão TDSP)

- `data/`:
  - `data/raw/`: Dados brutos (`noticias_ods13.csv`, `conteudo_ods13.txt`, `seeg_brasil_estados.csv`).
  - `data/processed/`: Dados tratados (`noticias_ods13_limpo.csv`, `texto_nuvem_palavras.txt`, `seeg_brasil_estados_limpo.csv`).
- `docs/`: Documentação estruturada pelas fases do ciclo de vida TDSP:
  - `BusinessUnderstanding/`: Entendimento do problema de negócio e objetivos.
  - `DataUnderstanding/`: Exploração e mapeamento das fontes de dados (SEEG Brasil e notícias climáticas).
  - `DataPreparation/`: Documentação de limpeza, stopwords, normalização numérica e formatação de séries estaduais.
  - `Modeling/`: Análise visual (WordCloud) e agregações temporais/estaduais.
  - `Deployment/`: Orientações de implantação da aplicação Streamlit multipage.
  - `Acceptance/`: Critérios de validação com stakeholders.
- `src/`: Scripts do pipeline de dados:
  - `scrape_seeg_brasil.py`: Raspagem dinâmica com Selenium da tabela de emissões por Estado na Plataforma SEEG.
  - `scrape_news.py`: Raspagem de notícias climáticas via BeautifulSoup.
  - `process_data.py`: Tratamento de textos, stopwords, conversão numérica e consolidação de datasets.
- `models/`: Artefatos e modelos serializados.
- `code/`: Aplicação principal ([`app.py`](code/app.py)) com interface interativa multipage, filtros reativos e persistência de sessão.
- `artifacts/`: Artefatos da documentação ([`project_charter.md`](artifacts/project_charter.md) e [`data_summary_report.md`](artifacts/data_summary_report.md)).

## Como Executar a Aplicação

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o pipeline de extração e tratamento de dados:
   ```bash
   python src/scrape_seeg_brasil.py
   python src/scrape_news.py
   python src/process_data.py
   ```

3. Inicie a aplicação Streamlit:
   ```bash
   streamlit run code/app.py
   ```

4. (Opcional) Inicie a API FastAPI a partir da raiz do projeto:
   ```bash
   uvicorn src.api:app --reload
   ```
   Acesse `http://127.0.0.1:8000/docs` para ver a documentação interativa.

   | Método | Rota | Função |
   |--------|------|--------|
   | GET | `/` | Verifica se a API está no ar. |
   | GET | `/noticias?termo=calor&limite=20` | Consulta notícias, com filtro opcional por título ou fonte. |
   | POST | `/noticias` | Envia uma nova notícia (JSON com `fonte`, `titulo` e `link`). Títulos repetidos retornam erro 409. |
   | GET | `/emissoes?estado=Rio de Janeiro` | Consulta as emissões de 1990 a 2024 de um estado, ou de todos se o parâmetro for omitido. |




