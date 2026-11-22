# TDSP — Data Understanding (Entendimento dos Dados)

Esta fase documenta o mapeamento, a ingestão, a estrutura e a auditoria de qualidade de todas as fontes de dados utilizadas no projeto.

---

## 1. Fontes Estruturadas
* **SEEG Brasil:** Emissões brutas em t CO₂e por Unidade Federativa (1990–2024), cobrindo 27 UFs e a linha residual "Não Alocado".
* **NOAA Mauna Loa:** Série temporal oficial de medições mensais de concentração atmosférica de dióxido de carbono em partes por milhão (ppm).

## 2. Fontes Não Estruturadas
* **Portais Jornalísticos (Agência Brasil e ONU News):** Matérias socioambientais coletadas via web scraping, com datas padronizadas, resumos estruturais e metadados temáticos.

## 3. Artefato Principal Vinculado
* **Relatório de Sumário de Dados (Data Summary Report):** [`artifacts/data_summary_report.md`](../../artifacts/data_summary_report.md)
