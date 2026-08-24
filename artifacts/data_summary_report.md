# Fontes de dados

## 1. NOAA Climate Data - Global Monitoring Laboratory (GML)
- **Tipo:** Série temporal de concentração de CO₂ atmosférico (Curva de Keeling e Média Global)
- **Formato:** CSV / Estruturado
- **Licença:** Domínio Público / NOAA Open Data
- **Uso:** Base histórica de referência para monitoramento climático, comparação e modelagem de séries temporais
- **Endpoints públicos oficiais:**
  - *Mauna Loa (Mensal):* `https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv`
  - *Média Global Marinha (Mensal):* `https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv`
  - *Médias Anuais:* `https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.csv`
- **Campos principais:** `year` (ano), `month` (mês), `decimal date` (data decimal), `average` (média mensal em ppm), `deseasonalized` (série dessazonalizada em ppm), `ndays` (dias observados), `sdev` (desvio padrão), `unc` (incerteza).

## 2. World Bank Climate Indicators (Opcional)
- **Tipo:** Tabelas de indicadores por país (emissões per capita, intensidade energética)
- **Formato:** CSV
- **Licença:** Open Data
- **Uso:** Benchmark internacional e cálculo de metas

---

