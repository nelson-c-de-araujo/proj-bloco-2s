# Projeto_Bloco_EtapaTP3 - Instituto Infnet
**Aluno: Nelson C. de Araujo**  
**Projeto da Agenda 2030 - ODS 13: Ação Contra a Mudança Global do Clima**

---

## 1. Definição do Problema de Negócio

**Problema:** Gestores públicos, empresas e pesquisadores têm dificuldade para acompanhar as emissões de gases de efeito estufa do Brasil em nível estadual e para entender o que está sendo discutido sobre clima. Os dados oficiais existem, mas estão em plataformas separadas, em formatos pouco práticos e sem integração com as notícias do tema.

**Revisão em relação ao TP2:** O problema continua válido. Mudou o escopo da solução. No TP2, o foco era um painel com séries de CO₂ e notícias. No TP3, o painel passou a usar a base oficial de emissões por estado do SEEG, e a solução ganhou uma API para acesso programático. Os dados de CO₂ atmosférico ainda não são reais (ver seção 5).

---

## 2. Objetivos

**Objetivo geral:** Oferecer um painel interativo e uma API que reúnam emissões oficiais por estado (SEEG), notícias sobre ação climática e uma base preparada para tarefas com LLM.

**Metas do TP3:**
- Painel Streamlit com navegação multipage: Visão Geral, Indicadores Globais de CO₂, Panorama de Notícias & NLP, SEEG - Emissões Brasil e Gestão de Arquivos & Dados.
- Coleta automatizada das emissões estaduais do SEEG com Selenium (página dinâmica), de 1990 a 2024.
- API FastAPI com quatro rotas (`GET /`, `GET /noticias`, `POST /noticias`, `GET /emissoes`), documentada no Swagger.
- Documentação de preparação para LLM em `docs/Modeling/preparacao_llm.md`.

**Metas mantidas do TP2:**
- Coleta de notícias por *web scraping* com BeautifulSoup e nuvem de palavras a partir do texto coletado.
- Upload de CSV próprio e download de relatórios.
- Cache (`@st.cache_data`) e estado de sessão (`st.session_state`).

**Metas que ainda não foram atingidas:**
- Séries reais de CO₂ atmosférico (NOAA). O gráfico usa valores de demonstração.
- Notícias com resumo completo. Hoje, 7 de 10 matérias usam um resumo padrão.

---

## 3. Metodologia e Ciclo de Vida do Projeto (TDSP / CRISP-DM)

O projeto segue o **Team Data Science Process (TDSP)**, com apoio das etapas do CRISP-DM:

1. **Business Understanding (`docs/BusinessUnderstanding/`):** definição do problema, objetivos e metas (este documento).
2. **Data Understanding (`docs/DataUnderstanding/`):** identificação das fontes de emissões (SEEG) e de notícias (Agência Brasil e ONU News). Ver [`data_summary_report.md`](data_summary_report.md).
3. **Data Preparation (`docs/DataPreparation/`):** scripts de coleta e limpeza em `src/` (`scrape_seeg_brasil.py`, `scrape_news.py`, `process_data.py`).
4. **Modeling & Analytics (`docs/Modeling/`):** agregações, nuvem de palavras e preparação para LLM ([`preparacao_llm.md`](../docs/Modeling/preparacao_llm.md)).
5. **Deployment (`docs/Deployment/`):** aplicação Streamlit (`code/app.py`) e API FastAPI (`src/api.py`).
6. **Customer Acceptance (`docs/Acceptance/`):** validação com stakeholders. Ainda não realizada.

---

## 4. Estrutura do Repositório

```
Projeto_Bloco_EtapaTP3/
|-- data/
|   |-- raw/                        # Dados brutos (noticias, conteúdo, SEEG)
|   |-- processed/                  # Dados limpos (notícias, nuvem de palavras, SEEG)
|-- docs/                           # Documentação por fase do TDSP
|-- models/                         # Modelos e artefatos serializados
|-- src/                            # Pipeline de dados e API
|   |-- scrape_seeg_brasil.py       # Coleta do SEEG com Selenium
|   |-- scrape_news.py              # Coleta de notícias com BeautifulSoup
|   |-- process_data.py             # Limpeza de texto, stopwords e conversão numérica
|   |-- api.py                      # API FastAPI
|-- code/
|   |-- app.py                      # Painel Streamlit multipage
|-- artifacts/                      # Charter e relatório de dados
|-- requirements.txt
|-- README.md
```

---

## 5. Limitações Conhecidas

- **Indicador de CO₂:** a página "Indicadores Globais de CO₂" usa uma série de demonstração de 2024, fixa no código. Não há integração com a NOAA. A seção de fontes do relatório de dados descreve a integração como planejada.
- **Resumos das notícias:** o scraping não consegue ler o parágrafo de 7 das 10 matérias, e o resumo padrão é gravado no lugar.
- **Métrica "Estados Monitorados":** a página do SEEG conta 28 linhas. Isso inclui "Não Alocado", que não é uma unidade federativa. O correto seria 27.
- **Segurança da API:** não há autenticação. O `POST /noticias` pode ser usado por qualquer pessoa com acesso à rede.
- **Ambiente de execução:** o scraping do SEEG exige Google Chrome instalado.

---

## 6. Próximos Passos

1. Corrigir a contagem de estados e tratar "Não Alocado" separadamente.
2. Substituir a série de demonstração de CO₂ por dados reais da NOAA, ou remover a página.
3. Extrair o corpo das notícias, em vez do resumo padrão.
4. Adicionar autenticação ao `POST /noticias`.
5. Iniciar a etapa de LLM, começando pela geração de texto a partir dos dados do SEEG.
6. Validar a solução com stakeholders e registrar em `docs/Acceptance/`.
