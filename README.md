# Projeto_Bloco_Etapa4 - Monitor de Emissões & Ação Climática (ODS 13)

Este repositório contém a quarta etapa de desenvolvimento (`Projeto_Bloco_Etapa4`) da plataforma integrada de monitoramento socioambiental e análise climática, desenvolvida sob os frameworks metodológicos **TDSP (Team Data Science Process)** e **CRISP-DM**, alinhada ao **ODS 13 (Ação Contra a Mudança Global do Clima)**.

---

## 🚀 Principais Entregas e Melhorias da Etapa 4

1. **Integração Completa via API RESTful (FastAPI + Streamlit via HTTP)**:
   - O painel em [`code/app.py`](code/app.py) consome o backend desacoplado via requisições HTTP (`requests.get` e `requests.post`), utilizando a variável de ambiente `API_URL` (padrão: `http://127.0.0.1:8000`).
   - Rotas consumidas no painel:
     - `GET /emissoes`: consome as séries históricas do SEEG Brasil.
     - `GET /noticias`: consome as matérias jornalísticas e seus resumos.
     - `GET /co2`: consome as concentrações reais de CO₂ atmosférico da NOAA.
     - `POST /noticias/sincronizar` e `POST /emissoes/sincronizar`: acionam a atualização de dados no backend sob demanda.
     - `POST /noticias`: permite cadastro direto de novas notícias através de formulário interativo no painel.
   - Resiliência integrada: mecanismo de fallback local automático caso a API esteja temporariamente offline.

2. **Web Scraping Dinâmico com Selenium e `WebDriverWait`**:
   - O módulo [`src/scrape_seeg_brasil.py`](src/scrape_seeg_brasil.py) substituiu o delay estático (`time.sleep`) por espera explícita inteligente (`WebDriverWait` com `expected_conditions`), aguardando dinamicamente a renderização completa do DOM/React na Single Page Application da Plataforma SEEG antes da extração da tabela `sticky-table`.

3. **Extração Robusta de Resumos de Notícias**:
   - Aprimoramento no scraper [`src/scrape_news.py`](src/scrape_news.py) com busca aprofundada na árvore do HTML e fallback para as meta tags (`meta[name="description"]` / `og:description`), eliminando o texto padrão genérico e garantindo resumos ricos e fiéis ao conteúdo original.

4. **Correção Metodológica na Contagem de Estados (27 UFs)**:
   - A contagem de "Estados Monitorados" no painel SEEG Brasil reflete com rigor as **27 Unidades Federativas** (26 estados e o Distrito Federal), separando a categoria residual *"Não Alocado"* (que abrange emissões não regionalizáveis, como offshore e aviação) com nota explicativa dedicada.

5. **Série Histórica Real de CO₂ (NOAA Mauna Loa)**:
   - Substituição dos dados de demonstração pela série histórica oficial de medições mensais e curvas de tendência dessazonalizada do **Observatório de Mauna Loa (NOAA Global Monitoring Laboratory)**.

---

## 📂 Estrutura do Repositório (Padrão TDSP)

```
Projeto_Bloco_Etapa4/
|-- data/
|   |-- raw/                        # Dados brutos (notícias, SEEG, série NOAA CO₂)
|   |-- processed/                  # Dados limpos e normalizados para consumo
|-- docs/                           # Documentação pelas fases do ciclo TDSP
|   |-- BusinessUnderstanding/      # Entendimento do problema e objetivos
|   |-- DataUnderstanding/          # Mapeamento e dicionário das fontes
|   |-- DataPreparation/            # Pipeline de extração, limpeza e normalização
|   |-- Modeling/                   # NLP, agregações e preparação para LLM
|   |-- Deployment/                 # Arquitetura de deploy (Streamlit + FastAPI)
|   |-- Acceptance/                 # Validação com stakeholders e aceitação
|-- src/                            # Backend, pipelines e API
|   |-- api.py                      # API RESTful FastAPI (GET e POST)
|   |-- scrape_seeg_brasil.py       # Coleta dinâmica SEEG via Selenium + WebDriverWait
|   |-- scrape_news.py              # Coleta de notícias via BeautifulSoup + Meta description
|   |-- process_data.py             # Pré-processamento, limpeza textual e conversões numéricas
|-- code/
|   |-- app.py                      # Painel analítico Streamlit multipage (HTTP client)
|-- artifacts/                      # Project Charter e Data Summary Report
|-- requirements.txt                # Dependências do projeto
|-- README.md                       # Documentação principal
```

---

## 🛠️ Como Executar a Solução

### 1. Instalação das Dependências
Em um ambiente virtual Python (3.10+):
```bash
pip install -r requirements.txt
```

### 2. Iniciar a API Backend (FastAPI)
A partir da raiz do projeto, inicie o servidor da API:
```bash
uvicorn src.api:app --reload --port 8000
```
> Documentação interativa (Swagger UI): **`http://127.0.0.1:8000/docs`**

#### Tabela de Endpoints da API:
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Confirmação de status da API. |
| `GET` | `/noticias` | Consulta matérias cadastradas, com suporte a filtro `termo` e `limite`. |
| `POST` | `/noticias` | Cadastro manual de notícia (payload JSON com `fonte`, `titulo`, `link`, `resumo`). |
| `POST` | `/noticias/sincronizar` | Dispara o web scraping e reprocessamento de notícias. |
| `GET` | `/emissoes` | Consulta histórica de emissões brutas por estado (1990–2024). |
| `POST` | `/emissoes` | Atualização/cadastro de medições estaduais. |
| `POST` | `/emissoes/sincronizar` | Dispara extração dinâmica do SEEG via Selenium. |
| `GET` | `/co2` | Consulta série histórica real de CO₂ atmosférico da NOAA (Mauna Loa). |

### 3. Iniciar o Painel Front-end (Streamlit)
Em outro terminal (com a API em execução ou configurando `API_URL`):
```bash
streamlit run code/app.py
```
Para apontar para uma API em outro host ou porta:
```bash
# Exemplo no Linux/Mac:
export API_URL="http://seu-servidor:8000" && streamlit run code/app.py

# Exemplo no Windows (PowerShell):
$env:API_URL="http://seu-servidor:8000"; streamlit run code/app.py
```
O painel estará acessível em **`http://localhost:8501`**.
