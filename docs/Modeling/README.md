# TDSP — Modeling: IA, Agente Decisório e Engenharia de Prompts (TP5 Final)

Esta fase documenta a modelagem em Ciência de Dados, o módulo analítico de *Grounding* estatístico e a integração de **Modelos de Linguagem de Grande Porte (LLMs)** para a geração de inteligência estratégica no contexto do **ODS 13 (Ação Climática)**.

---

## 1. Arquitetura do Agente Inteligente de Tomada de Decisão (`src/decision_agent.py`)

O Agente Inteligente ESG foi projetado sob o princípio de **Data Grounding Analítico + Prompt Engineering com Multi-IA**:

```
[ Usuário / Decisor ] ──> Seleciona UF (ex: São Paulo), Perfil e Pergunta Opcional
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │       Data Grounding Engine (Pandas)         │
         │  - Variação histórica 1990-2024 (%)          │
         │  - Delta recente 2020-2024 (%)               │
         │  - Ranking das 27 UFs e % nacional           │
         │  - Ano e volume de pico histórico           │
         │  - Nível de risco e trajetória climática     │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │       Engenharia de Prompt (ChatML)          │
         │  - Persona do Decisor (Role-based)           │
         │  - Injeção das métricas calculadas           │
         │  - Contexto global NOAA e notícias recentes  │
         │  - 5 Seções executivas obrigatórias          │
         │  - Tratamento mandatório do foco do decisor  │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │           Motor de Inferência Multi-IA       │
         │  Opção 1: Google Gemini (AI Studio API)      │
         │           (Auto-Descoberta de Modelos)       │
         │  Opção 2: Motor Heurístico ESG (50ms)        │
         │  Opção 3: Modelo Qwen Local Hugging Face     │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         [ Parecer Executivo Estruturado com Plano de Ação ]
```

---

## 2. Motores de Inteligência Artificial Integrados

1. **Google Gemini (Google AI Studio via REST API):**
   - Suporte nativo à família Gemini Flash com **auto-descoberta dinâmica de modelos textuais** via endpoint `/v1beta/models`, evitando quebras por atualizações de catálogo;
   - Geração rápida (< 2s) com teto ampliado para **2.048 tokens**, eliminando truncamentos;
   - Compreensão profunda de regulação socioambiental, taxonomia BACEN/CVM e ODS 13.

2. **Motor Analítico Heurístico Especialista ESG:**
   - Sistema determinístico baseado em lógica de domínio que calcula a árvore de decisão sobre as métricas do SEEG e NOAA em **50 milissegundos**;
   - Serve como garantia de alta disponibilidade e resiliência contra falhas de conexão ou limites de cota.

3. **Modelo Local Hugging Face (`Qwen/Qwen2.5-0.5B-Instruct`):**
   - Execução 100% offline em hardware local (CPU/GPU) via PyTorch/Transformers.

---

## 3. Estrutura Padronizada do Parecer Decisório

1. **Diagnóstico Situacional & Trajetória Histórica:** Evolução das emissões de 1990 a 2024 e posição relativa no ranking nacional;
2. **Matriz de Riscos Climáticos & Governança ESG:** Riscos físicos, regulatórios (SBCE) e de transição de acordo com o perfil;
3. **Alinhamento com o ODS 13 (Agenda 2030):** Conformidade com o Acordo de Paris e metas de descarbonização;
4. **Plano de Ação Estratégico & Recomendações:** Ações de Curto (0-12m), Médio (1-3 anos) e Longo Prazo (3-5 anos);
5. **Diretrizes Estratégicas para o Foco do Decisor:** Resposta direta e obrigatória ao questionamento específico informado pelo usuário no campo livre.
