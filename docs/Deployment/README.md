# TDSP — Deployment (Implantação e Arquitetura)

Esta fase descreve a arquitetura de implantação da solução, estruturada de forma desacoplada entre uma **API de Serviços RESTful (FastAPI)** e uma **Interface Analítica Web (Streamlit)**.

---

## 1. Arquitetura da Solução

```
[ Usuário / Navegador ]
          │
          ▼ (Porta 8501)
┌──────────────────────────────────────────────┐
│            Painel Streamlit                  │
│              (code/app.py)                   │
│                                              │
│  📊 Monitoramento e Dados:                   │
│     - 🏠 Visão Geral da Solução (Home)       │
│     - 📈 Indicadores Globais de CO₂          │
│     - 🇧🇷 SEEG - Emissões por Estado          │
│     - 📰 Panorama de Notícias & NLP          │
│     - 📁 Gestão de Arquivos & Dados          │
│                                              │
│  🎯 Inteligência & Decisão ESG:              │
│     - 🎯 Agente Decisório ESG (ODS 13)       │
│       (Google Gemini / Motor Especialista)   │
└──────────────────────┬───────────────────────┘
                       │
                       │ HTTP GET / POST (com variável API_URL)
                       ▼
┌──────────────────────────────────────────────┐
│            API Backend FastAPI               │
│               (src/api.py)                   │
│                                              │
│  - Documentação Swagger /docs                │
│  - Validação de Payloads via Pydantic        │
│  - Endpoints do Agente (/agente/decisao)     │
│  - Gatilhos de Pipelines e Sincronização     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│        Motor do Agente & Decisão             │
│        - src/decision_agent.py               │
│        (Data Grounding + Multi-IA)           │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│          Pipeline de Engenharia              │
│  - scrape_seeg_brasil.py (Selenium)          │
│  - scrape_news.py (BeautifulSoup)            │
│  - process_data.py (Limpeza e Tipagem)       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             Camada de Dados                  │
│       data/raw & data/processed              │
└──────────────────────────────────────────────┘
```

---

## 2. API Backend (FastAPI)

* **Arquivo principal:** [`src/api.py`](../../src/api.py)
* **Execução:**
  ```bash
  uvicorn src.api:app --reload --port 8000
  ```
* **Documentação interativa (Swagger UI):** `http://127.0.0.1:8000/docs`

### Catálogo de Rotas Disponíveis (TP5 Final)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Confirma o status de integridade e versão da API. |
| `POST` | `/agente/decisao` | **Gera parecer executivo de tomada de decisão com IA (ODS 13/ESG)** para uma UF ou Brasil total. Suporta Google Gemini, motor heurístico e modelo local. |
| `GET` | `/agente/metricas` | Consulta métricas e evidências de Ciência de Dados pré-calculadas para um estado. |
| `GET` | `/emissoes` | Consulta os dados históricos de emissões do SEEG Brasil (1990–2024), com filtro por estado. |
| `POST` | `/emissoes` | Cadastra ou atualiza registros de emissão estadual. |
| `POST` | `/emissoes/sincronizar` | Dispara extração dinâmica do SEEG via Selenium em modo headless com `WebDriverWait`. |
| `GET` | `/co2` | Consulta medições reais de CO₂ atmosférico do Observatório de Mauna Loa da NOAA. |
| `GET` | `/noticias` | Consulta notícias cadastradas, com suporte a filtro por termo e limite. |
| `POST` | `/noticias` | Cadastra uma nova notícia enviada pelo cliente com validação Pydantic. |
| `POST` | `/noticias/sincronizar` | Dispara o web scraping ao vivo nos portais de notícias e o pré-processamento de NLP. |
| `POST` | `/processar_texto` | Executa inferência textual com LLM para resumo, sentimento ou insights. |
| `GET` | `/llm/status` | Verifica a prontidão do engine de inferência e do modelo local. |

---

## 3. Aplicação Front-end (Streamlit)

* **Arquivo principal:** [`code/app.py`](../../code/app.py)
* **Execução:**
  ```bash
  streamlit run code/app.py
  ```
* **Configuração de Ambiente (`API_URL`):**
  Lê a variável de ambiente `API_URL` para realizar chamadas HTTP. Caso não configurada, assume por padrão `http://127.0.0.1:8000`.
* **Alta Disponibilidade e Resiliência:** Caso o servidor FastAPI esteja temporariamente offline ou ocorra latência excessiva, a interface aciona automaticamente um fallback local elegante direto para a camada de dados em disco e motor heurístico, assegurando que o usuário nunca encontre falhas de tela.
