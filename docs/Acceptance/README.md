# TDSP — Customer Acceptance (Aceitação e Validação Final)

Esta pasta reúne os artefatos de homologação, validação com stakeholders e a argumentação executiva final da solução perante as rubricas avaliativas do **Projeto de Bloco (TP5)**.

---

## 1. Documento de Apresentação e Argumentação Final
* **Documento Mestre:** [`apresentacao_solucao_final.md`](apresentacao_solucao_final.md)
  * Apresentação da solução e justificativa de resolução do problema de negócio socioambiental;
  * Demonstração de cada etapa do ciclo completo de Ciência de Dados (Coleta ➔ Limpeza ➔ Análise ➔ IA ➔ Apresentação);
  * Estudos de caso práticos (Pará, São Paulo e Total Brasil);
  * Alinhamento detalhado com as metas do ODS 13 e práticas ESG;
  * Roteiro para apresentação oral (Pitch de 5 minutos).

---

## 2. Matriz de Atendimento das Rubricas de Avaliação (TP5)

| Rubrica de Avaliação | Evidência Técnica no Projeto | Status |
|---|---|---|
| **1. Integração de funcionalidade com LLM** | Agente Inteligente para Tomada de Decisão ESG implementado em `src/decision_agent.py` e integrado ao dashboard Streamlit e à API FastAPI. | **Demonstrado** |
| **2. Uso eficaz de dados coletados (APIs/Scraping)** | O Agente cruza dados do SEEG Brasil (Selenium), NOAA (Mauna Loa) e Notícias (BeautifulSoup), calculando evidências reais para o parecer. | **Demonstrado** |
| **3. Ciclo completo de Ciência de Dados** | Coleta automatizada ➔ Limpeza e normalização ➔ Modelagem estatística com Pandas ➔ Inferência com IA local ➔ Interface visual e exportação executiva. | **Demonstrado** |
| **4. Justificativa e resolução do problema ESG/ODS** | Diagnóstico situacional, matriz de riscos climáticos e plano de ação estruturado em curto, médio e longo prazo para gestores e empresas. | **Demonstrado** |
| **5. Uso eficiente e alinhado de LLMs** | Modelo local open-source (`Qwen2.5-0.5B`) executado sem custos de nuvem, blindado contra alucinações através de *Data Grounding*. | **Demonstrado** |
| **6. Visualizações claras e organizadas** | Painel Streamlit multipage com cards métricos, gráficos temporais dinâmicos, comparativos entre estados e visualizações limpas. | **Demonstrado** |
| **7. Artefatos TDSP completos e atualizados** | `project_charter.md`, `data_summary_report.md` e documentações por fase TDSP totalmente consolidados na raiz e em `docs/`. | **Demonstrado** |
| **8. Simplicidade e fluidez no uso** | Geração de parecer executivo com apenas 1 clique a partir da seleção da UF, com download do relatório em Markdown. | **Demonstrado** |
