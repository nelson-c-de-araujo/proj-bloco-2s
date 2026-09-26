# Projeto_Bloco_EtapaTP2 - Monitor de Emissões & Ação Climática (ODS 13)

Este repositório contém a segunda etapa de desenvolvimento (`Projeto_Bloco_EtapaTP2`) da aplicação de monitoramento e análise de emissões de CO₂ e panorama de notícias climáticas para apoiar decisões alinhadas ao **ODS 13 (Ação Contra a Mudança Global do Clima)**.

## Estrutura do Repositório (Padrão TDSP)

A estrutura segue rigorosamente o padrão do **Team Data Science Process (TDSP)**:

- `data/`:
  - `data/raw/`: Dados brutos obtidos via scraping (`noticias_ods13.csv` e `conteudo_ods13.txt`).
  - `data/processed/`: Dados tratados para a aplicação (`noticias_ods13_limpo.csv` e `texto_nuvem_palavras.txt`).
- `docs/`: Documentação estruturada pelas fases do ciclo de vida TDSP:
  - `BusinessUnderstanding/`: Entendimento do problema de negócio e objetivos.
  - `DataUnderstanding/`: Exploração e mapeamento das fontes de dados.
  - `DataPreparation/`: Documentação de limpeza e stopwords.
  - `Modeling/`: Análise visual (WordCloud) e agregações.
  - `Deployment/`: Orientações de implantação da aplicação Streamlit.
  - `Acceptance/`: Critérios de validação com stakeholders.
- `src/`: Scripts independentes do pipeline de dados:
  - `scrape_news.py`: Raspagem de notícias climáticas via BeautifulSoup.
  - `process_data.py`: Tratamento de textos e remoção de stopwords em português.
- `models/`: Artefatos e pickles de modelos serializados.
- `code/`: Aplicação principal ([`app.py`](code/app.py)) com interface interativa, cache, sessão e serviços de upload/download de CSV.
- `artifacts/`: Artefatos principais da documentação ([`project_charter.md`](artifacts/project_charter.md) e [`data_summary_report.md`](artifacts/data_summary_report.md)).

## Como Executar a Aplicação

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o pipeline de dados (opcional, para atualizar notícias):
   ```bash
   python src/scrape_news.py
   python src/process_data.py
   ```

3. Inicie a aplicação Streamlit:
   ```bash
   streamlit run code/app.py
   ```
