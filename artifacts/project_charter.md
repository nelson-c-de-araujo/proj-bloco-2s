# Projeto_Bloco_Etapa4 - Instituto Infnet
**Aluno: Nelson C. de Araujo**  
**Projeto da Agenda 2030 - ODS 13: Ação Contra a Mudança Global do Clima**

---

## 1. Definição do Problema de Negócio

**Problema:** Gestores públicos, empresas e pesquisadores têm dificuldade para acompanhar as emissões de gases de efeito estufa do Brasil em nível estadual e para entender o que está sendo discutido sobre clima. Os dados oficiais existem, mas estão em plataformas separadas, em formatos pouco práticos e sem integração com as notícias do tema.

**Revisão em relação ao TP3:** Na Etapa 4 (penúltima etapa do projeto), a solução atingiu o estágio de integração desacoplada completa:
- O painel Streamlit consome a API FastAPI via chamadas HTTP (`requests.get` e `requests.post`) com configuração dinâmica por variável de ambiente (`API_URL`).
- Os dados sintéticos de CO₂ atmosférico foram integralmente substituídos por séries históricas reais da NOAA (Observatório de Mauna Loa).
- A automação em Selenium foi aprimorada com `WebDriverWait`, eliminando delays cegos (`time.sleep`).
- A captura de notícias passou a extrair resumos reais via inspeção estrutural e meta descriptions.
- A contagem de unidades federativas foi retificada para 27 UFs, tratando "Não Alocado" com a devida nota metodológica.

---

## 2. Objetivos e Entregas da Etapa 4

**Objetivo geral:** Disponibilizar uma arquitetura moderna e desacoplada composta por uma API RESTful de serviços e um painel interativo analítico, integrando dados oficiais do SEEG Brasil, medições reais de CO₂ da NOAA e acervo dinâmico de notícias socioambientais com processamento de linguagem natural.

**Metas da Etapa 4 Concluídas:**
- **Integração HTTP Client-Server:** O `code/app.py` consome os endpoints da API (`/noticias`, `/emissoes`, `/co2`) via `requests.get`, dispara rotinas via `requests.post` e permite cadastrar notícias com payload JSON validado via Pydantic.
- **Parametrização por Variável de Ambiente:** Implementação de `API_URL` (com valor padrão `http://127.0.0.1:8000`) para suportar deploys locais e em nuvem/containers.
- **Robustez no Web Scraping com Selenium:** Substituição de `time.sleep(12)` por esperas explícitas `WebDriverWait` e `expected_conditions`, sincronizando a captura exatamente no término da renderização do React/D3 na Plataforma SEEG.
- **Extração Real de Resumos:** Aprimoramento da extração de notícias em `src/scrape_news.py`, eliminando resumos padrões genéricos.
- **Série Real de Concentração de CO₂:** Substituição de dados mockados por medições reais oficiais (ppm e tendência) do Observatório de Mauna Loa da NOAA.
- **Retificação Metodológica de Unidades Federativas:** Métrica estrita de 27 Estados/DF monitorados, com isolamento e esclarecimento sobre "Não Alocado".

---

## 3. Metodologia e Ciclo de Vida do Projeto (TDSP / CRISP-DM)

O projeto segue rigorosamente o framework **Team Data Science Process (TDSP)**:

1. **Business Understanding (`docs/BusinessUnderstanding/`):** Alinhamento contínuo das metas ao ODS 13 e aos requisitos da disciplina.
2. **Data Understanding (`docs/DataUnderstanding/`):** Mapeamento detalhado das fontes oficiais (SEEG Brasil, NOAA Mauna Loa, Agência Brasil, ONU News). Ver [`data_summary_report.md`](data_summary_report.md).
3. **Data Preparation (`docs/DataPreparation/`):** Scripts em `src/` com limpeza de stopwords, conversão de formatos numéricos brasileiros e estruturação para modelos analíticos.
4. **Modeling & Analytics (`docs/Modeling/`):** Nuvem de palavras com pesos de frequência, séries temporais e documentação de preparação para tarefas com LLMs ([`preparacao_llm.md`](../docs/Modeling/preparacao_llm.md)).
5. **Deployment (`docs/Deployment/`):** Execução paralela do servidor FastAPI (porta 8000) e do painel Streamlit (porta 8501).
6. **Customer Acceptance (`docs/Acceptance/`):** Validações com base no feedback avaliativo das entregas parciais e critérios de completude.

---

## 4. Estrutura Atualizada do Repositório

```
Projeto_Bloco_Etapa4/
|-- data/
|   |-- raw/                        # noticias_ods13.csv, conteudo_ods13.txt, seeg_brasil_estados.csv, co2_mensal_noaa.csv
|   |-- processed/                  # noticias_ods13_limpo.csv, texto_nuvem_palavras.txt, seeg_brasil_estados_limpo.csv, co2_mensal_noaa_limpo.csv
|-- docs/                           # Documentação por fase TDSP
|-- models/                         # Modelos e artefatos analíticos
|-- src/                            # Backend, API e pipelines
|   |-- api.py                      # API RESTful FastAPI completa (GET / POST)
|   |-- scrape_seeg_brasil.py       # Coleta dinâmica SEEG com Selenium e WebDriverWait
|   |-- scrape_news.py              # Coleta de notícias com busca estrutural de resumo
|   |-- process_data.py             # Pré-processamento, normalização numérica e limpeza textual
|-- code/
|   |-- app.py                      # Painel Streamlit multipage consumindo a API via HTTP
|-- artifacts/                      # project_charter.md e data_summary_report.md
|-- requirements.txt
|-- README.md
```

---

## 5. Limitações Residuais e Próximos Passos (Etapa Final / TP5)

- **Autenticação de Endpoints:** A API opera atualmente sem camadas de autenticação (OAuth2/API Key) nos endpoints de mutação (`POST`), recomendando-se proteção por token antes de publicação aberta em produção.
- **Aperfeiçoamento dos Prompts do LLM:** Refinar os templates ChatML para sumarização de tabelas numéricas do SEEG e respostas analíticas de séries temporais.
- **Homologação Final com Usuários:** Concluir a rodada formal de validação de aceitação com stakeholders em `docs/Acceptance/`.
