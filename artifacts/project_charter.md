# Project Charter — Projeto de Bloco (TP5 / Versão Final Consolidada)
**Instituto Infnet | Ciência de Dados e Inteligência Artificial**  
**Aluno:** Nelson C. de Araujo  
**Projeto da Agenda 2030:** ODS 13 — Ação Contra a Mudança Global do Clima & Práticas ESG  
**Frameworks Metodológicos:** Team Data Science Process (TDSP) e CRISP-DM  

---

## 1. Definição do Problema de Negócio e Justificativa

### 1.1. Contexto do Problema
Gestores públicos municipais e estaduais, comitês executivos de sustentabilidade corporativa (ESG) e gestores de fundos de investimento enfrentam sérias dificuldades para desenhar planos de mitigação climática fundamentados em evidências sólidas:
* **Dispersão e Assimetria de Dados:** Os dados oficiais de emissões de Gases de Efeito Estufa (GEE) no Brasil estão dispersos em portais técnicos de difícil navegação ou em relatórios anuais estáticos;
* **Desconexão entre Escala Local e Global:** As metas macroclimáticas internacionais (como o monitoramento de partes por milhão de CO₂ atmosférico da NOAA e o Acordo de Paris) raramente dialogam com as especificidades regionais de cada Unidade Federativa brasileira;
* **Abismo entre Métricas e Decisão Prática:** Gráficos e números brutos não respondem diretamente às perguntas críticas de governança: *"Qual é o risco regulatório para a economia do meu estado?", "Como direcionar incentivos fiscais?", "Quais ações imediatas de curto prazo devem ser priorizadas para conter o desmatamento ou descarbonizar o transporte?"*.

### 1.2. A Solução de Ciência de Dados
A solução desenvolvida integra todo o ciclo da Ciência de Dados Aplicada para transformar dados brutos em **inteligência acionável e tomada de decisão estratégica**, combinando:
1. **Engenharia e Coleta Automatizada:** Web Scraping dinâmico com Selenium e `WebDriverWait` (SEEG Brasil: 27 UFs de 1990 a 2024), parsing com BeautifulSoup (Agência Brasil e ONU News) e séries oficiais da NOAA (Observatório de Mauna Loa);
2. **Pré-Processamento & Backend de Microsserviços:** Módulo `src/process_data.py` e API RESTful desacoplada em FastAPI (`src/api.py`) com validação estrita via Pydantic;
3. **Agente Inteligente de Tomada de Decisão ESG (`src/decision_agent.py`):**
   - **Data Grounding Analítico Estrito:** Todas as métricas matemáticas (taxas de crescimento, deltas quinquenais, rankings das 27 UFs e ano de pico) são calculadas em Pandas antes da geração textual, blindando o sistema contra alucinações numéricas;
   - **Arquitetura Híbrida de IA Multi-Motor:** Suporte nativo ao **Google Gemini (API oficial Google AI Studio)** com auto-descoberta dinâmica de modelos textuais, motor analítico heurístico especialista ESG (instantâneo em 50ms) e modelo open-source local via Hugging Face;
   - **Suporte a Demandas Customizadas do Decisor:** Campo livre para inserção de dúvidas estratégicas, gerando obrigatoriamente a Seção 5 no parecer executivo com orientações práticas;
   - **Teto Amplo de Tokens:** Capacidade de geração ampliada para até 2.048 tokens, assegurando pareceres completos sem truncamento;
4. **Interface Analítica Fluida e Intuitiva (Streamlit Multipage em `code/app.py`):** Navegação estruturada em dois pilares fundamentais: **Monitoramento e Dados** e **Inteligência & Decisão ESG**.

---

## 2. Objetivos e Entregas Consolidadas da Solução Final (TP5)

### 2.1. Objetivos do Projeto
* **Objetivo Geral:** Disponibilizar uma plataforma de inteligência de dados climáticos e governança socioambiental que una séries históricas consolidadas (SEEG e NOAA) a capacidades avançadas de Inteligência Artificial para orientar políticas públicas e decisões corporativas ESG no Brasil.
* **Objetivos Específicos:**
  * Automatizar a extração e atualização de dados de emissões para as 27 Unidades Federativas do Brasil (1990–2024);
  * Implementar e validar um **Agente Inteligente de Tomada de Decisão** alimentado por LLM e motor analítico de regras (*Closed-Domain Grounding*);
  * Prover um painel web intuitivo e fluido com visualizações comparativas e geração de relatórios executivos em tempo real;
  * Cumprir integralmente o ciclo metodológico do TDSP e os critérios de avaliação acadêmica.

### 2.2. Entregas Técnicas Consolidadas (Ciclo Completo)
| Fase TDSP | Entregas Técnicas Realizadas |
|---|---|
| **Business Understanding** | Project Charter atualizado com métricas de negócio, definição de personas (Gestão Pública, Governança Corporativa, Investimento de Impacto) e alinhamento com as metas do ODS 13. |
| **Data Understanding** | Mapeamento e auditoria das bases estruturadas (SEEG Brasil: 27 UFs + NOAA Mauna Loa) e não estruturadas (notícias socioambientais), consolidado no [Data Summary Report](data_summary_report.md). |
| **Data Preparation** | Módulo [`src/process_data.py`](../src/process_data.py) com tipagem numérica brasileira, tratamento de categorias residuais ("Não Alocado"), normalização cronológica e limpeza semântica de *stopwords* em português. |
| **Modeling & Analytics** | Módulo [`src/decision_agent.py`](../src/decision_agent.py) integrando motor multi-IA: Google Gemini (com auto-descoberta de modelos textuais), motor analítico especialista de alta disponibilidade e modelo Hugging Face, com ChatML e Data Grounding via Pandas. |
| **Deployment** | Backend desacoplado em FastAPI ([`src/api.py`](../src/api.py)) operando rotas `GET` e `POST` com validação Pydantic e Swagger, integrado ao painel Streamlit multipage ([`code/app.py`](../code/app.py)) com resiliência e fallback local elegante. |
| **Customer Acceptance** | Validação prática de casos de uso (Pará, São Paulo, Total Nacional), pareceres estratégicos exportáveis em Markdown [`docs/Acceptance/apresentacao_solucao_final.md`](../docs/Acceptance/apresentacao_solucao_final.md). |

---

## 3. O Papel da IA e da Engenharia de Prompts na Resolução do Problema

### 3.1. Por que Modelos de Linguagem para Decisão Climática?
O grande desafio dos relatórios tradicionais de sustentabilidade é a rigidez: tabelas e gráficos mostram *o que aconteceu*, mas não explicam *o que fazer em seguida*. O uso de LLMs atua como uma ponte cognitiva entre os números brutos e a estratégia.

### 3.2. Arquitetura de Data Grounding (Prevenção de Alucinações)
Para garantir rigor científico no projeto:
1. **O LLM não realiza cálculos aritméticos:** Todas as taxas de crescimento, deltas quinquenais, rankings estaduais e proporções percentuais são calculadas estritamente em Python/Pandas pelo módulo `src/decision_agent.py`.
2. **Injeção de Evidências Confinadas:** As métricas calculadas e os fatos jornalísticos recentes são injetados no prompt estruturado como *evidências restritas*.
3. **Engenharia de Prompt Especializada (ChatML):** O modelo opera sob personas bem definidas (*Role-Based Prompting*), estruturando o parecer em 5 blocos analíticos padronizados:
   - *1. Diagnóstico Situacional & Trajetória Histórica;*
   - *2. Matriz de Riscos Climáticos & Governança ESG;*
   - *3. Alinhamento com o ODS 13 (Agenda 2030);*
   - *4. Plano de Ação Estratégico (Curto, Médio e Longo Prazo);*
   - *5. Diretrizes Estratégicas para o Foco do Decisor (Resposta obrigatória ao termo/pergunta informada).*

### 3.3. Soberania, Flexibilidade e Desempenho Multi-Motor
A solução final suporta três modalidades de execução:
* **Google Gemini (Google AI Studio):** Máxima profundidade analítica, raciocínio avançado, suporte a até 2.048 tokens de saída sem truncamento e velocidade de resposta inferior a 2 segundos;
* **Motor Analítico Heurístico Especialista ESG:** Resposta determinística instantânea em 50 milissegundos, com alta densidade conceitual, servindo como garantia absoluta de disponibilidade contra falhas de rede ou cotas de API;
* **Modelo Local Hugging Face:** Execução 100% offline em hardware local para cenários de privacidade estrita.

---

## 4. Estrutura Final do Repositório (Padrão TDSP)

```
Projeto_Bloco_TP5_Final/
|-- data/
|   |-- raw/                        # Dados brutos coletados (SEEG, NOAA, notícias)
|   |-- processed/                  # Dados limpos, normalizados e tipados
|-- docs/                           # Documentação pelas fases do ciclo TDSP
|   |-- BusinessUnderstanding/      # Problema, personas e ODS 13
|   |-- DataUnderstanding/          # Dicionário e sumarização das bases
|   |-- DataPreparation/            # Pipeline de engenharia e limpeza de dados
|   |-- Modeling/                   # Módulos de IA, Data Grounding e Agente Decisório
|   |-- Deployment/                 # Arquitetura de microsserviços (FastAPI + Streamlit)
|   |-- Acceptance/                 # Apresentação executiva, estudos de caso.
|-- src/                            # Backend, microsserviços e algoritmos
|   |-- api.py                      # API RESTful FastAPI (GET e POST com Swagger)
|   |-- decision_agent.py           # Agente Inteligente para Tomada de Decisão ESG (Multi-IA)
|   |-- llm_engine.py               # Motor de inferência local Hugging Face
|   |-- scrape_seeg_brasil.py       # Extração dinâmica SEEG via Selenium + WebDriverWait
|   |-- scrape_news.py              # Extração de notícias socioambientais via BeautifulSoup
|   |-- process_data.py             # Limpeza textual, conversões numéricas e ordenação
|-- code/
|   |-- app.py                      # Painel interativo Streamlit multipage
|-- artifacts/
|   |-- project_charter.md          # Charter completo do projeto (este documento)
|   |-- data_summary_report.md      # Relatório técnico das fontes de dados integradas
|-- requirements.txt                # Dependências do projeto
|-- README.md                       # Guia mestre da solução consolidada
```

---

## 5. Critérios de Sucesso e Impacto Acadêmico/Profissional

* **Simplicidade e Usabilidade:** Usuários técnicos ou executivos conseguem gerar um diagnóstico completo de qualquer estado brasileiro em segundos com interface fluida e intuitiva;
* **Fidelidade e Rigor Metodológico:** 100% dos dados apresentados refletem fontes oficiais com rastreabilidade comprovada;
* **Conformidade com as Rubricas:** Demonstração inequívoca de todas as etapas da Ciência de Dados Aplicada, posicionando a inteligência artificial como catalisadora de governança sustentável e cumprimento da Agenda 2030 no Brasil.
