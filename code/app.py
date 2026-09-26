import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud

"""
Painel de Acompanhamento de Emissões e Ação Climática (ODS 13)
Aluno: Nelson C. de Araujo | Instituto Infnet
"""

st.set_page_config(
    page_title='Painel de Acompanhamento Climático - ODS 13',
    page_icon='🌍',
    layout='wide'
)

# --- CARREGAMENTO OTIMIZADO DE DADOS (CACHE) ---
@st.cache_data
def obter_dados_historicos_demo():
    dados_historicos = {
        "Data de Registro": [
            "2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", 
            "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01", 
            "2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01"
        ],
        "Ano": [2024] * 12,
        "Mês": [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ],
        "Nível de CO2 (ppm)": [
            423.80, 424.65, 425.20, 426.90, 
            427.50, 426.10, 424.30, 422.10, 
            420.80, 421.50, 423.10, 424.60
        ],
        "Tendência Ajustada (ppm)": [
            423.90, 424.15, 424.40, 424.65, 
            424.90, 425.10, 425.35, 425.60, 
            425.80, 426.05, 426.30, 426.50
        ]
    }
    return pd.DataFrame(dados_historicos)

@st.cache_data
def obter_noticias_relevantes():
    caminho_arquivo = "data/processed/noticias_ods13_limpo.csv"
    if os.path.exists(caminho_arquivo):
        return pd.read_csv(caminho_arquivo)
    return pd.DataFrame()

@st.cache_data
def obter_texto_nuvem():
    caminho_texto = "data/processed/texto_nuvem_palavras.txt"
    if os.path.exists(caminho_texto):
        with open(caminho_texto, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    return ""

# Lista ordenada dos meses do ano para o filtro
TODOS_OS_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# --- MEMÓRIA DA NAVEGAÇÃO DO USUÁRIO (ESTADO DA SESSÃO) ---
if "termo_pesquisa_noticia" not in st.session_state:
    st.session_state.termo_pesquisa_noticia = ""

if "meses_selecionados" not in st.session_state:
    st.session_state.meses_selecionados = TODOS_OS_MESES.copy()


# --- PAINEL LATERAL DE PERSONALIZAÇÃO ---
st.sidebar.header("🎛️ Personalize sua Consulta")

meses_filtrados = st.sidebar.multiselect(
    "Filtrar por Período (Mês):",
    options=TODOS_OS_MESES,
    default=st.session_state.meses_selecionados,
    help="Escolha um ou mais meses para analisar as medições de emissões."
)

st.session_state.meses_selecionados = meses_filtrados

st.sidebar.markdown("---")
pesquisa_digitada = st.sidebar.text_input(
    "🔎 Pesquisar Assunto ou Notícia:",
    value=st.session_state.termo_pesquisa_noticia,
    placeholder="Ex: calor, metas, floresta..."
)
st.session_state.termo_pesquisa_noticia = pesquisa_digitada

if st.sidebar.button("🧹 Limpar Filtros"):
    st.session_state.termo_pesquisa_noticia = ""
    st.session_state.meses_selecionados = TODOS_OS_MESES.copy()
    st.rerun()


# --- CABEÇALHO PRINCIPAL DA APLICAÇÃO ---
st.title('🌍 Painel de Monitoramento do Clima & Emissões')
st.caption("Uma iniciativa focada no **ODS 13: Ação Contra a Mudança Global do Clima**")

st.markdown("""
### Bem-vindo ao Nosso Espaço de Monitoramento Climático
Compreender como nossas atividades impactam o planeta é o primeiro passo para promover transformações reais. 
Esta ferramenta foi pensada para tornar os dados sobre emissões de carbono transparentes, acessíveis e fáceis de interpretar, 
ajudando empresas, gestores e cidadãos a tomarem decisões mais conscientes em favor do meio ambiente.
""")

st.markdown("---")

# Abas de Conteúdo
aba_indicadores, aba_panorama = st.tabs([
    "📈 Indicadores de Emissão", 
    "📰 Panorama de Notícias & Temas em Alta"
])

df_registros = obter_dados_historicos_demo()

with aba_indicadores:
    st.subheader("Evolução das Concentrações de CO₂")
    st.write("Acompanhe abaixo os dados das medições do período selecionado:")
    
    # Filtrar os dados pelos meses escolhidos pelo usuário
    if meses_filtrados:
        df_exibicao = df_registros[df_registros["Mês"].isin(meses_filtrados)]
    else:
        df_exibicao = pd.DataFrame()

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Média do Período (ppm)", f"{df_exibicao['Nível de CO2 (ppm)'].mean():.2f}" if not df_exibicao.empty else "-")
    col_m2.metric("Pico de Concentração (ppm)", f"{df_exibicao['Nível de CO2 (ppm)'].max():.2f}" if not df_exibicao.empty else "-")
    col_m3.metric("Medições Analisadas", len(df_exibicao))

    col_tabela, col_grafico = st.columns([1, 2])
    with col_tabela:
        st.dataframe(df_exibicao[["Mês", "Nível de CO2 (ppm)", "Tendência Ajustada (ppm)"]], height=320, hide_index=True)
    with col_grafico:
        if not df_exibicao.empty:
            st.line_chart(data=df_exibicao, x='Data de Registro', y='Nível de CO2 (ppm)')
        else:
            st.info("Nenhum mês foi selecionado. Por favor, escolha ao menos um mês no painel lateral para visualizar os gráficos.")

    st.markdown("---")
    st.subheader("📥 Exportar Dados & Upload de Dados Próprios")
    st.write("Você pode baixar o relatório atual ou enviar seu próprio arquivo CSV de emissões para análise:")

    col_up, col_down = st.columns(2)
    
    with col_up:
        st.markdown("**Enviar Novo Arquivo CSV de Emissões**")
        arquivo_enviado = st.file_uploader(
            "Selecione um arquivo CSV no seu computador", 
            type=["csv"],
            help="O arquivo deve conter ao menos as colunas 'Data de Registro' e 'Nível de CO2 (ppm)'."
        )
        if arquivo_enviado is not None:
            try:
                df_custom = pd.read_csv(arquivo_enviado)
                st.success("Arquivo recebido com sucesso!")
                st.write("Dados enviados:")
                st.dataframe(df_custom, use_container_width=True)
                
                # Eixos padrão: Mês no X e Nível de CO2 (ppm) no Y
                eixo_x = "Data de Registro" if "Data de Registro" in df_custom.columns else ("Mês" if "Mês" in df_custom.columns else None)
                eixo_y = "Nível de CO2 (ppm)" if "Nível de CO2 (ppm)" in df_custom.columns else (df_custom.select_dtypes(include=['float64', 'int64']).columns[0] if len(df_custom.select_dtypes(include=['float64', 'int64']).columns) > 0 else None)
                
                if eixo_y:
                    st.line_chart(data=df_custom, x=eixo_x, y=eixo_y)
                else:
                    st.line_chart(data=df_custom)
            except Exception as e:
                st.error("Não foi possível ler o arquivo. Certifique-se de que é um CSV válido.")

    with col_down:
        st.markdown("**Baixar Relatório das Medições Selecionadas**")
        st.write("Exporte os dados filtrados exibidos nesta consulta para utilizar em planilhas ou relatórios:")
        
        if not df_exibicao.empty:
            csv_dados = df_exibicao.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Baixar Relatório em CSV",
                data=csv_dados,
                file_name="relatorio_emissoes_ods13.csv",
                mime="text/csv"
            )
        else:
            st.info("Selecione ao menos um mês para habilitar o download do relatório.")

with aba_panorama:
    st.subheader("Notícias e Atualizações sobre o Clima")
    st.write("Acompanhe o que tem sido noticiado pelos principais veículos e organismos internacionais:")
    
    noticias_carregadas = obter_noticias_relevantes()

    if not noticias_carregadas.empty:
        if st.session_state.termo_pesquisa_noticia:
            busca = st.session_state.termo_pesquisa_noticia.lower()
            noticias_filtradas = noticias_carregadas[
                noticias_carregadas['titulo'].str.lower().str.contains(busca, na=False) |
                noticias_carregadas['fonte'].str.lower().str.contains(busca, na=False)
            ]
        else:
            noticias_filtradas = noticias_carregadas

        col_n1, col_n2 = st.columns(2)
        col_n1.metric("Publicações Encontradas", len(noticias_filtradas))
        col_n2.metric("Veículos de Comunicação", noticias_filtradas['fonte'].nunique() if not noticias_filtradas.empty else 0)
        
        st.dataframe(
            noticias_filtradas[['fonte', 'titulo', 'link']], 
            column_config={
                "fonte": "Veículo / Fonte",
                "titulo": "Título da Publicação",
                "link": st.column_config.LinkColumn("Acessar Matéria")
            },
            use_container_width=True
        )
    else:
        st.info("Ainda não temos matérias carregadas para exibir neste momento.")

    st.markdown("---")
    st.subheader("💬 O Que Mais Se Fala Sobre Mudanças Climáticas?")
    st.write("Esta nuvem de palavras destaca os conceitos e termos mais frequentes nas últimas publicações:")

    texto_compilado = obter_texto_nuvem()
    if len(texto_compilado.strip()) > 0:
        nuvem = WordCloud(
            width=850, 
            height=380, 
            background_color='black',
            colormap='plasma',
            max_words=80
        ).generate(texto_compilado)

        figura, eixo = plt.subplots(figsize=(10, 4.5))
        eixo.imshow(nuvem, interpolation='bilinear')
        eixo.axis('off')
        st.pyplot(figura)
    else:
        st.info("Ainda não há texto suficiente para construir a nuvem de termos.")

st.markdown("---")
st.caption("Infnet - Nelson C. de Araujo")
