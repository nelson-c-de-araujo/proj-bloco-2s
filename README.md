# Projeto_Bloco_TP5_Final — Monitor de Emissões, Governança ESG & Ação Climática (ODS 13)
**Instituto Infnet | Ciência de Dados e Inteligência Artificial**  
**Aluno:** Nelson C. de Araujo  
**Frameworks Metodológicos:** Team Data Science Process (TDSP) e CRISP-DM  

---

## 🚀 Sobre a Solução Final (TP5)

Este repositório consolida a entrega final (**TP5**) do Projeto de Bloco. A solução demonstra o **ciclo completo da Ciência de Dados Aplicada** — desde a coleta automatizada e saneamento de dados até a modelagem avançada com Inteligência Artificial e a implementação de um **Agente Inteligente de Tomada de Decisão** voltado à governança socioambiental e sustentabilidade corporativa (**ODS 13 — Ação Contra a Mudança Global do Clima**).

---

## 🌟 Principais Destaques e Inovações da Solução

1. **Agente Inteligente para Tomada de Decisão ESG com LLMs (`src/decision_agent.py`)**:
   - **Data Grounding Analítico Estrito:** Todas as métricas matemáticas (taxas de crescimento, deltas quinquenais, rankings das 27 UFs e ano de pico) são calculadas previamente em Pandas, blindando a IA contra alucinações numéricas;
   - **Arquitetura Multi-Motor de IA:**
     - ⚡ **Google Gemini (API oficial Google AI Studio):** Integração via REST API com **auto-descoberta dinâmica de modelos textuais ativos**, com teto ampliado para **2.048 tokens**, gerando pareceres densos e sem cortes em menos de 2 segundos;
     - 🧠 **Motor Analítico Heurístico Especialista ESG:** Resposta analítica instantânea em **50 milissegundos**, servindo como contingência de alta disponibilidade;
     - 🤖 **Modelo Local Hugging Face:** Execução offline para cenários de privacidade estrita.
   - **Tratamento Mandatório da Demanda do Decisor:** Campo livre para perguntas e focos prioritários, gerando obrigatoriamente a Seção 5 no parecer final com orientações práticas.
   - Suporte a 3 perfis de decisão:
     - 🏛️ *Gestão Pública & Regulação*;
     - 🏢 *Governança Corporativa & ESG*;
     - 💼 *Investimento de Impacto & Riscos Climáticos*.

2. **Dashboard Analítico e Fluido (Streamlit Multipage em [`code/app.py`](code/app.py))**:
   - **Estrutura Organizada para Apresentação Acadêmica:**
     - 📊 **Monitoramento e Dados:**
       1. 🏠 *Visão Geral da Solução* (Página inicial com roteiro da apresentação);
       2. 📈 *Indicadores Globais de CO₂* (Séries oficiais NOAA Mauna Loa);
       3. 🇧🇷 *SEEG - Emissões por Estado* (Matriz histórica de 35 anos das 27 UFs);
       4. 📰 *Panorama de Notícias & NLP* (Acervo socioambiental e nuvem de tópicos);
       5. 📁 *Gestão de Arquivos & Dados* (Upload e download de dados);
     - 🎯 **Inteligência & Decisão ESG:**
       1. 🎯 *Agente Decisório ESG (ODS 13)* (A cereja do bolo da aplicação).
   - Cards de KPIs reativos com deltas percentuais em tempo real;
   - Gráficos dinâmicos de linha e barra comparando estados e contextualizando com a curva global da NOAA;
   - Download de relatórios executivos em Markdown (`.md`) e bases em CSV.

3. **Integração Desacoplada via API RESTful (FastAPI em [`src/api.py`](src/api.py))**:
   - Backend desacoplado servindo aos dashboards e a clientes externos;
   - Endpoints dedicados para tomada de decisão (`POST /agente/decisao` e `GET /agente/metricas`);
   - Documentação interativa Swagger UI em `/docs` com modelos Pydantic e controle de status HTTP.

4. **Pipelines de Coleta Automatizada com Dados Reais**:
   - **SEEG Brasil:** Scraping dinâmico via Selenium em modo headless com esperas explícitas inteligentes (`WebDriverWait`), cobrindo as 27 UFs (1990–2024);
   - **NOAA Mauna Loa:** Série histórica oficial de concentrações atmosféricas mensais de CO₂ (ppm) e tendência ajustada;
   - **Portais de Notícias:** Scraping via BeautifulSoup com busca estrutural profunda de resumos e metadados cronológicos.

5. **Documentação TDSP Completa e Auditável**:
   - Todos os artefatos metodológicos consolidados: [Project Charter](artifacts/project_charter.md), [Data Summary Report](artifacts/data_summary_report.md) e [Apresentação e Argumentação da Solução Final](docs/Acceptance/apresentacao_solucao_final.md).

---

## 📂 Estrutura do Repositório (Padrão TDSP)

```
Projeto_Bloco_TP5_Final/
|-- data/
|   |-- raw/                        # Dados brutos coletados (SEEG, NOAA, notícias)
|   |-- processed/                  # Dados limpos, normalizados e tipados
|-- docs/                           # Documentação pelas fases do ciclo TDSP
|   |-- BusinessUnderstanding/      # Entendimento do problema, personas e ODS 13
|   |-- DataUnderstanding/          # Mapeamento e auditoria das fontes
|   |-- DataPreparation/            # Pipeline de extração, limpeza e normalização
|   |-- Modeling/                   # Módulos de IA, Data Grounding e Agente Decisório
|   |-- Deployment/                 # Arquitetura de microsserviços (FastAPI + Streamlit)
|   |-- Acceptance/                 # Apresentação executiva, estudos de caso.
|-- src/                            # Backend, microsserviços e algoritmos
|   |-- api.py                      # API RESTful FastAPI (GET e POST)
|   |-- decision_agent.py           # Agente Inteligente para Tomada de Decisão ESG (Multi-IA)
|   |-- llm_engine.py               # Motor de inferência local Hugging Face
|   |-- scrape_seeg_brasil.py       # Extração dinâmica SEEG via Selenium + WebDriverWait
|   |-- scrape_news.py              # Extração de notícias socioambientais via BeautifulSoup
|   |-- process_data.py             # Pré-processamento, normalização numérica e limpeza textual
|-- code/
|   |-- app.py                      # Painel interativo Streamlit multipage
|-- artifacts/
|   |-- project_charter.md          # Charter completo do projeto
|   |-- data_summary_report.md      # Relatório de fontes de dados integradas
|-- requirements.txt                # Dependências do projeto
|-- README.md                       # Documentação principal consolidada
```

---

## 🛠️ Como Executar a Solução

### 1. Instalação das Dependências
Em um ambiente virtual Python (3.10 ou superior):
```bash
pip install -r requirements.txt
```

### 2. Iniciar a API Backend (FastAPI)
A partir da raiz do projeto:
```bash
uvicorn src.api:app --reload --port 8000
```
> Documentação interativa (Swagger UI): **`http://127.0.0.1:8000/docs`**

#### Tabela de Principais Endpoints da API:
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Status e confirmação de prontidão da API. |
| `POST` | `/agente/decisao` | **Gera parecer executivo de tomada de decisão com IA (ODS 13/ESG)** para uma UF ou Brasil total. |
| `GET` | `/agente/metricas` | Consulta KPIs estatísticos calculados de um estado para apoio à decisão. |
| `GET` | `/emissoes` | Consulta histórica de emissões brutas por estado (1990–2024). |
| `POST` | `/emissoes/sincronizar` | Dispara extração dinâmica do SEEG via Selenium em modo headless. |
| `GET` | `/co2` | Consulta série histórica real de CO₂ atmosférico da NOAA (Mauna Loa). |
| `GET` | `/noticias` | Consulta matérias cadastradas, com suporte a filtros e limites. |
| `POST` | `/noticias/sincronizar` | Dispara o web scraping e reprocessamento de notícias. |
| `POST` | `/processar_texto` | Executa inferência com LLM para resumo, sentimento ou insights. |
| `GET` | `/llm/status` | Retorna o status de prontidão do modelo local. |

### 3. Iniciar o Painel Front-end (Streamlit)
Em outro terminal:
```bash
streamlit run code/app.py
```
Para apontar para uma API em outro host ou porta:
```powershell
$env:API_URL="http://seu-servidor:8000"; streamlit run code/app.py
```
O painel estará acessível em **`http://localhost:8501`**.
