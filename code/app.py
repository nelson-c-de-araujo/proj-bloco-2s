import streamlit as st
import pandas as pd

"""
Monitor de Emissões (ODS 13)
Aluno: Nelson C. de Araujo | Instituto Infnet
"""



st.set_page_config(
    page_title='Monitor de Emissões - ODS 13',
    page_icon='🌍',
    layout='centered'
)


st.title('Monitor de Emissões - Projeto ODS 13')

"""
## Problema e Objetivo:
Muitas organizações não dispõem de ferramentas práticas para acompanhar suas emissões de gases de efeito estufa. 
Este protótipo simples visa centralizar dados de emissões para apoiar decisões alinhadas ao 
**ODS 13 (Ação Contra a Mudança Global do Clima)**.
"""

"""---"""

"""## Links Úteis:"""
"""
- **NOAA Global Monitoring Laboratory:** [gml.noaa.gov/ccgg/trends/](https://gml.noaa.gov/ccgg/trends/)
- **Nações Unidas - ODS 13 Brasil:** [brasil.un.org/pt-br/sdgs/13](https://brasil.un.org/pt-br/sdgs/13)
- **World Bank Climate Data:** [data.worldbank.org](https://data.worldbank.org)

"""

"""---"""

"""## Amostra de Dados de Emissões (Demo)"""

dados_simulados = {
    "Data": [
        "2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", 
        "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01", 
        "2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01"
    ],
    "Ano": [2024] * 12,
    "Mes": list(range(1, 13)),
    "CO2_Mensal_ppm": [
        125.80, 245.65, 144.20, 691.90, 
        427.50, 426.10, 424.30, 422.10, 
        420.80, 421.50, 423.10, 424.60
    ],
    "CO2_Dessazonalizado_ppm": [
        423.90, 424.15, 424.40, 424.65, 
        424.90, 425.10, 425.35, 425.60, 
        425.80, 426.05, 426.30, 426.50
    ],
    "Variacao_Anual_ppm": [
        +2.35, +2.40, +2.60, +2.75, 
        +2.50, +2.45, +2.30, +2.20, 
        +2.15, +2.30, +2.40, +2.50
    ]
}

df_teste = pd.DataFrame(dados_simulados)

st.dataframe(df_teste)

st.bar_chart(
    data=df_teste,
    x='Data',
    y='CO2_Mensal_ppm',
    width='stretch',
    color='#ffaa00'
)

st.line_chart(
    data=df_teste,
    x='Data',
    y='CO2_Mensal_ppm',
    width='stretch'
)

st.caption("Nota: Dados simulados para demo do projeto.")

