# TDSP - Deployment

Esta pasta descreve a arquitetura de implantação da solução, estruturada de forma desacoplada entre uma **API de Serviços RESTful (FastAPI)** e uma **Interface Analítica Web (Streamlit)**.

---

## 1. Arquitetura da Solução

```
[ Usuário / Navegador ]
          │
          ▼ (Porta 8501)
┌─────────────────────────────────┐
│     Painel Streamlit            │
│       (code/app.py)             │
│                                 │
│  - Navegação Multipage          │
│  - Visualizações e Gráficos     │
│  - Consumo via requests HTTP    │
└────────────────┬────────────────┘
                 │
                 │ HTTP GET / POST (com variável API_URL)
                 ▼
┌─────────────────────────────────┐
│      API Backend FastAPI        │
│         (src/api.py)            │
│                                 │
│  - Documentação Swagger /docs   │
│  - Validação via Pydantic       │
│  - Gatilhos de Pipelines        │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    Pipeline de Dados (src/)     │
│  - scrape_seeg_brasil.py        │
│  - scrape_news.py               │
│  - process_data.py              │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│        Camada de Dados          │
│     data/raw & data/processed   │
└─────────────────────────────────┘
```

---

## 2. API Backend (FastAPI)

- **Arquivo principal:** [`src/api.py`](../../src/api.py)
- **Execução:**
  ```bash
  uvicorn src.api:app --reload --port 8000
  ```
- **Documentação interativa:** `http://127.0.0.1:8000/docs`

### Catálogo de Rotas Disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Retorna o status de integridade da API. |
| GET | `/noticias` | Consulta notícias cadastradas, com suporte a filtro opcional por `termo` e `limite`. |
| POST | `/noticias` | Cadastra uma nova notícia enviada pelo cliente (com validação Pydantic e prevenção de duplicatas). |
| POST | `/noticias/sincronizar` | Dispara o web scraping ao vivo nos portais de notícias e o pré-processamento de NLP. |
| GET | `/emissoes` | Consulta os dados históricos de emissões do SEEG Brasil (1990–2024), com filtro opcional por `estado`. |
| POST | `/emissoes` | Cadastra ou atualiza registros de emissão estadual. |
| POST | `/emissoes/sincronizar` | Dispara a extração dinâmica na Plataforma SEEG via Selenium com `WebDriverWait`. |
| GET | `/co2` | Consulta medições reais de CO₂ atmosférico do Observatório de Mauna Loa da NOAA. |
| POST | `/processar_texto` | Executa inferência com LLM local (`Qwen2.5-0.5B-Instruct`), retornando resposta estruturada (Response Model) com resumo, tom climático ou insights. |
| GET | `/llm/status` | Verifica a prontidão do engine de inferência e do modelo Hugging Face na máquina local. |

### Tratamento Robusto de Erros (HTTP Exceptions)

A rota `POST /processar_texto` conta com tratamento rigoroso de exceções:
- **`422 Unprocessable Entity`**: Texto de entrada inválido ou inferior a 15 caracteres.
- **`400 Bad Request`**: Tipo de análise não suportado (aceitos: `resumo`, `sentimento`, `insights`).
- **`503 Service Unavailable`**: Modelo de IA local indisponível (ex.: ausência de bibliotecas `torch`/`transformers` ou falha de alocação de memória no host).
- **`500 Internal Server Error`**: Erro inesperado durante o processo de geração/inferência.

---

## 3. Aplicação Front-end (Streamlit)

- **Arquivo principal:** [`code/app.py`](../../code/app.py)
- **Execução:**
  ```bash
  streamlit run code/app.py
  ```
- **Configuração de Ambiente (`API_URL`):**
  O painel lê a variável de ambiente `API_URL` para realizar as chamadas HTTP. Caso não informada, assume por padrão `http://127.0.0.1:8000`.
  - Exemplo para ambiente local:
    ```bash
    streamlit run code/app.py
    ```
  - Exemplo para ambiente em nuvem ou container:
    ```bash
    API_URL="https://minha-api-clima.com" streamlit run code/app.py
    ```
- **Mecanismo de Resiliência:** Caso a API esteja em processo de reinicialização ou inacessível, as rotinas de carregamento executam um fallback elegante direto para a camada de dados em disco, assegurando alta disponibilidade ao usuário final.

---

## 4. Dependências e Requisitos de Ambiente

As dependências estão listadas em [`requirements.txt`](../../requirements.txt).
Requisitos de infraestrutura:
- Python 3.10 ou superior.
- Google Chrome instalado no sistema para a execução do Selenium em modo headless.
