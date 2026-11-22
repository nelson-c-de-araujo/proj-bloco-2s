# TDSP — Data Preparation (Preparação dos Dados)

Esta fase reúne os scripts e pipelines de Extração, Transformação e Carga (ETL), saneamento de dados e engenharia de características para modelos analíticos e de linguagem natural.

---

## 1. Pipelines de Engenharia (`src/`)
* **[`src/scrape_seeg_brasil.py`](../../src/scrape_seeg_brasil.py):** Web scraping dinâmico em Selenium headless com esperas explícitas inteligentes (`WebDriverWait`) sobre a tabela React do SEEG Brasil.
* **[`src/scrape_news.py`](../../src/scrape_news.py):** Web scraping de notícias climáticas com BeautifulSoup, busca hierárquica no DOM e meta description tags.
* **[`src/process_data.py`](../../src/process_data.py):** Limpeza e normalização numérica (formato brasileiro para float padrão), tratamento de dados omissos, ordenação cronológica e pré-processamento de NLP (remoção de *stopwords* e pontuações).

## 2. Camadas de Dados
* **Dados Brutos:** `data/raw/` (preservação da integridade das coletas originais).
* **Dados Processados:** `data/processed/` (dados prontos e higienizados para consumo analítico e APIs).
