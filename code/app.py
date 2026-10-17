import streamlit as st
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Garantir visibilidade do diretório raiz para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.scrape_news import extrair_noticias_ods13
from src.process_data import processar_dados
from src.scrape_seeg_brasil import extrair_seeg_brasil_estados_selenium




st.set_page_config(
    page_title='Painel Climático - ODS 13',
    page_icon='🌍',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Constantes e Listas
TODOS_OS_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Inicialização de Estado da Sessão (Session State)
if "termo_pesquisa_noticia" not in st.session_state:
    st.session_state.termo_pesquisa_noticia = ""

if "meses_selecionados" not in st.session_state:
    st.session_state.meses_selecionados = TODOS_OS_MESES.copy()


# --- FUNÇÕES DE CARREGAMENTO OTIMIZADO DE DADOS (CACHE) ---
@st.cache_data
def obter_dados_historicos_demo():
    dados_historicos = {
        "Data de Registro": [
            "2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", 
            "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01", 
            "2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01"
        ],
        "Ano": [2024] * 12,
        "Mês": TODOS_OS_MESES,
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
    if not os.path.exists(caminho_arquivo):
        caminho_arquivo = "data/raw/noticias_ods13.csv"
    if os.path.exists(caminho_arquivo):
        return pd.read_csv(caminho_arquivo)
    return pd.DataFrame()


@st.cache_data
def obter_texto_nuvem():
    caminho_texto = "data/processed/texto_nuvem_palavras.txt"
    if not os.path.exists(caminho_texto):
        caminho_texto = "data/raw/conteudo_ods13.txt"
    if os.path.exists(caminho_texto):
        with open(caminho_texto, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    return ""





@st.cache_data(show_spinner="Carregando dados nacionais do SEEG Brasil...")
def obter_dados_seeg_brasil():
    caminho_proc = "data/processed/seeg_brasil_estados_limpo.csv"
    caminho_raw = "data/raw/seeg_brasil_estados.csv"
    caminho = caminho_proc if os.path.exists(caminho_proc) else caminho_raw
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()




# ==========================================
# DEFINIÇÃO DAS PÁGINAS DA APLICAÇÃO
# ==========================================

def pagina_inicio():
    st.title("🌍 Painel Integrado de Ação Climática - ODS 13")
    st.subheader("Plataforma de Monitoramento de Emissões e Análise de Dados Climáticos")
    
    st.markdown("""
    Esta plataforma foi desenvolvida para apoiar a tomada de decisões socioambientais,
    centralizando dados confiáveis sobre emissões de gases de efeito estufa e temas em alta 
    alinhados ao **Objetivo de Desenvolvimento Sustentável 13 (Ação Contra a Mudança Global do Clima)**.
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 📈 Indicadores Globais\nAcompanhe a evolução temporal das concentrações atmosféricas de CO₂ e médias registradas.")
    with col2:
        st.info("### 📰 Notícias & Tendências\nExplore o panorama de matérias dos principais veículos de comunicação e os tópicos mais citados.")
    with col3:
        st.success("### 🇧🇷 SEEG - Emissões Brasil\nVisão completa a nível Brasil clusterizada por estado com séries históricas (1990–2024).")

    st.markdown("---")
    
    st.markdown("""
    ### 🧭 Como Navegar pela Plataforma
    Utilize o menu lateral para alternar entre as diferentes seções:
    - **Visão Geral**: Apresentação da plataforma e síntese dos objetivos.
    - **Indicadores Globais de CO₂**: Gráficos de séries temporais e filtros mensais interativos.
    - **Panorama de Notícias & NLP**: Acompanhamento de publicações jornalísticas e nuvem de tópicos em destaque.
    - **SEEG - Emissões Brasil**: Panorama nacional das emissões consolidadas por todos os Estados brasileiros.
    - **Gestão de Arquivos & Dados**: Envio de relatórios próprios e download de bases consolidadas.
    """)


def pagina_indicadores():
    st.title("📈 Indicadores Globais de Emissão de CO₂")
    st.caption("Séries temporais e monitoramento de concentrações atmosféricas (ppm)")
    
    # Filtros laterais
    st.sidebar.markdown("### 🎛️ Filtro de Período")
    meses_filtrados = st.sidebar.multiselect(
        "Selecione os Meses:",
        options=TODOS_OS_MESES,
        default=st.session_state.meses_selecionados,
        help="Escolha os meses para filtrar os indicadores de concentração de CO₂."
    )
    st.session_state.meses_selecionados = meses_filtrados
    
    if st.sidebar.button("🧹 Restaurar Meses"):
        st.session_state.meses_selecionados = TODOS_OS_MESES.copy()
        st.rerun()

    df_registros = obter_dados_historicos_demo()
    
    if meses_filtrados:
        df_exibicao = df_registros[df_registros["Mês"].isin(meses_filtrados)]
    else:
        df_exibicao = pd.DataFrame()

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Média do Período (ppm)", f"{df_exibicao['Nível de CO2 (ppm)'].mean():.2f}" if not df_exibicao.empty else "-")
    col_m2.metric("Pico de Concentração (ppm)", f"{df_exibicao['Nível de CO2 (ppm)'].max():.2f}" if not df_exibicao.empty else "-")
    col_m3.metric("Medições Analisadas", len(df_exibicao))

    st.markdown("---")
    col_tabela, col_grafico = st.columns([1, 2])
    with col_tabela:
        st.markdown("**Tabela de Registros**")
        st.dataframe(df_exibicao[["Mês", "Nível de CO2 (ppm)", "Tendência Ajustada (ppm)"]], height=350, hide_index=True)
    with col_grafico:
        st.markdown("**Gráfico de Tendência Temporal**")
        if not df_exibicao.empty:
            st.line_chart(data=df_exibicao, x='Data de Registro', y='Nível de CO2 (ppm)')
        else:
            st.warning("Selecione pelo menos um mês no menu lateral para visualizar os dados.")


def pagina_noticias():
    st.title("📰 Panorama de Notícias & Temas em Alta (ODS 13)")
    st.caption("Acompanhe as principais notícias e tendências sobre mudanças climáticas e sustentabilidade")
    
    # Barra de Ações Rápidas (Atualização sob Demanda)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Atualizar Notícias Agora", type="primary", help="Sincroniza as matérias recentes e atualiza os temas em alta"):
            with st.spinner("Buscando as notícias mais recentes e atualizando a análise de temas..."):
                try:
                    extrair_noticias_ods13()
                    processar_dados()
                    st.cache_data.clear()
                    st.success("Notícias e temas em alta atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error("Ocorreu uma instabilidade ao conectar aos portais de notícias. Tente novamente em instantes.")
    with col_info:
        st.caption("ℹ️ Clique para verificar e carregar as últimas publicações disponíveis.")

    st.markdown("---")

    st.sidebar.markdown("### 🔎 Busca Textual")
    termo = st.sidebar.text_input(
        "Pesquisar termo ou fonte:",
        value=st.session_state.termo_pesquisa_noticia,
        placeholder="Ex: calor, metas, floresta..."
    )
    st.session_state.termo_pesquisa_noticia = termo
    
    if st.sidebar.button("🧹 Limpar Pesquisa"):
        st.session_state.termo_pesquisa_noticia = ""
        st.rerun()

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
        st.info("Nenhuma matéria carregada no momento. Utilize o botão acima para sincronizar.")

    st.markdown("---")
    st.subheader("💬 Nuvem de Palavras - Tópicos em Destaque")
    st.write("Termos e conceitos mais recorrentes nas publicações analisadas:")

    texto_compilado = obter_texto_nuvem()
    if len(texto_compilado.strip()) > 0:
        nuvem = WordCloud(
            width=900, 
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
        st.info("Ainda não há conteúdo suficiente para exibir a nuvem de palavras.")


def pagina_arquivos():
    st.title("📁 Gestão de Arquivos & Upload/Download")
    st.caption("Intercâmbio de dados e exportação de relatórios analíticos")
    
    df_registros = obter_dados_historicos_demo()
    df_exibicao = df_registros[df_registros["Mês"].isin(st.session_state.meses_selecionados)]

    col_up, col_down = st.columns(2)
    
    with col_up:
        st.markdown("### 📤 Upload de Dados Próprios")
        st.write("Envie seu próprio arquivo CSV de medições climáticas para visualização:")
        arquivo_enviado = st.file_uploader(
            "Selecione um arquivo CSV", 
            type=["csv"],
            help="Arquivo CSV contendo dados de emissão."
        )
        if arquivo_enviado is not None:
            try:
                df_custom = pd.read_csv(arquivo_enviado)
                st.success("Arquivo processado com sucesso!")
                st.write(f"Dimensões: {df_custom.shape[0]} linhas x {df_custom.shape[1]} colunas")
                st.dataframe(df_custom.head(50), use_container_width=True)
                
                # Gráfico automático
                eixo_x = "Data de Registro" if "Data de Registro" in df_custom.columns else ("Mês" if "Mês" in df_custom.columns else None)
                eixo_y = "Nível de CO2 (ppm)" if "Nível de CO2 (ppm)" in df_custom.columns else (df_custom.select_dtypes(include=['float64', 'int64']).columns[0] if len(df_custom.select_dtypes(include=['float64', 'int64']).columns) > 0 else None)
                
                if eixo_y:
                    st.line_chart(data=df_custom, x=eixo_x, y=eixo_y)
                else:
                    st.line_chart(data=df_custom)
            except Exception as e:
                st.error("Erro ao ler o arquivo CSV. Verifique a formatação.")

    with col_down:
        st.markdown("### 📥 Download de Relatórios")
        st.write("Exporte os dados das medições globais selecionadas:")
        
        if not df_exibicao.empty:
            csv_dados = df_exibicao.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Baixar Relatório de Indicadores Globais (CSV)",
                data=csv_dados,
                file_name="relatorio_emissoes_ods13.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhum mês selecionado para download.")
            
        st.markdown("---")
        st.write("Exporte a base de dados oficial do **SEEG Brasil por Estados**:")
        if os.path.exists("data/raw/seeg_brasil_estados.csv"):
            with open("data/raw/seeg_brasil_estados.csv", "rb") as f_seeg_br:
                st.download_button(
                    label="📄 Baixar Tabela Completa SEEG Brasil (CSV)",
                    data=f_seeg_br,
                    file_name="seeg_brasil_estados.csv",
                    mime="text/csv"
                )



def pagina_seeg_brasil():
    st.title("🇧🇷 SEEG - Emissões Brasil por Estado")
    st.caption("Visão histórica consolidada das emissões brutas (1990–2024) desagregadas por Unidade Federativa")
    
    st.markdown("""
    > **Panorama Nacional**: Esta página apresenta os dados oficiais da **Plataforma SEEG**, 
    > capturados dinamicamente via **Selenium** a partir da tabela com filtros de emissões por Estado. 
    > Permite analisar a evolução das emissões em todo o território nacional e comparar o desempenho dos estados brasileiros.
    """)

    # Barra de Ações Rápidas (Atualização Dinâmica via Selenium)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Sincronizar Plataforma SEEG", type="primary", help="Acessa a plataforma online do SEEG e extrai a tabela consolidada mais recente de emissões por Estado"):
            with st.spinner("Conectando à Plataforma SEEG e extraindo dados dos Estados do Brasil..."):
                try:
                    extrair_seeg_brasil_estados_selenium()
                    processar_dados()
                    st.cache_data.clear()
                    st.success("Dados do SEEG Brasil atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error("Não foi possível sincronizar com a plataforma no momento. Tente novamente mais tarde.")
    with col_info:
        st.caption("ℹ️ Clique para consultar a plataforma oficial em tempo real e sincronizar a tabela de emissões estaduais.")

    st.markdown("---")

    df_brasil = obter_dados_seeg_brasil()

    if df_brasil.empty:
        st.warning("Nenhum registro de emissões nacionais disponível. Clique no botão acima para sincronizar.")
        return

    # Lista de anos disponíveis
    colunas_anos = [c for c in df_brasil.columns if c.isdigit()]
    ultimo_ano = colunas_anos[-1] if colunas_anos else "2024"
    primeiro_ano = colunas_anos[0] if colunas_anos else "1990"

    # Separar linha de Total e dados dos estados
    df_estados = df_brasil[~df_brasil["Estado"].isin(["Total", "total"])].copy()
    linha_total = df_brasil[df_brasil["Estado"].isin(["Total", "total"])]

    # Métricas de destaque
    total_recente = linha_total[ultimo_ano].values[0] if not linha_total.empty and ultimo_ano in linha_total.columns else df_estados[ultimo_ano].sum()
    total_1990 = linha_total[primeiro_ano].values[0] if not linha_total.empty and primeiro_ano in linha_total.columns else df_estados[primeiro_ano].sum()
    variacao_pct = ((total_recente - total_1990) / total_1990) * 100 if total_1990 > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estados Monitorados", f"{len(df_estados)}")
    col2.metric(f"Emissão Brasil em {ultimo_ano} (t CO₂e)", f"{total_recente:,.0f}".replace(",", "."))
    col3.metric(f"Emissão Brasil em {primeiro_ano} (t CO₂e)", f"{total_1990:,.0f}".replace(",", "."))
    col4.metric(f"Variação ({primeiro_ano} vs {ultimo_ano})", f"{variacao_pct:+.1f}%")

    st.markdown("---")

    # Filtro de Estados para comparação personalizada
    st.sidebar.markdown("### 🗺️ Comparativo entre Estados")
    lista_todos_estados = sorted(df_estados["Estado"].unique().tolist())
    estados_selecionados = st.sidebar.multiselect(
        "Selecione Estados para Comparar:",
        options=lista_todos_estados,
        default=["Rio de Janeiro", "São Paulo", "Minas Gerais", "Pará", "Mato Grosso"],
        help="Escolha dois ou mais estados para visualizar a curva comparativa de emissões."
    )

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader(f"🏆 Top 10 Estados com Maiores Emissões ({ultimo_ano})")
        df_top10 = df_estados.sort_values(by=ultimo_ano, ascending=False).head(10)
        st.bar_chart(df_top10, x="Estado", y=ultimo_ano)
        st.caption("Classificação dos estados com maior volume de emissões brutas registradas.")

    with col_g2:
        st.subheader("📈 Evolução Histórica Comparativa (1990–2024)")
        if estados_selecionados:
            df_filtro_est = df_estados[df_estados["Estado"].isin(estados_selecionados)]
            # Reestruturar para formato longo (tidy) para o gráfico de linha
            df_melt = df_filtro_est.melt(id_vars=["Estado"], value_vars=colunas_anos, var_name="Ano", value_name="Emissão (t CO₂e)")
            df_melt["Ano"] = df_melt["Ano"].astype(int)
            
            # Pivotar para colunas = Estados e índice = Ano
            df_pivot = df_melt.pivot(index="Ano", columns="Estado", values="Emissão (t CO₂e)")
            st.line_chart(df_pivot)
            st.caption("Comparação das trajetórias históricas de emissão entre os estados selecionados.")
        else:
            st.info("Selecione ao menos um Estado no menu lateral para visualizar o gráfico temporal.")

    st.markdown("---")
    st.subheader("📋 Tabela Completa de Emissões por Estado (Plataforma SEEG)")
    st.caption("Valores anuais em toneladas de gases de efeito estufa (CO₂e):")
    st.dataframe(df_brasil, use_container_width=True, hide_index=True)

    # Download direto dos dados
    csv_br = df_brasil.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📄 Baixar Tabela SEEG Brasil (CSV)",
        data=csv_br,
        file_name="seeg_brasil_emissoes_estados.csv",
        mime="text/csv"
    )


# ==========================================
# CONFIGURAÇÃO DE NAVEGAÇÃO MULTIPÁGINAS
# ==========================================

navegacao = st.navigation({
    "Navegação Principal": [
        st.Page(pagina_inicio, title="Visão Geral", icon="🏠", default=True),
        st.Page(pagina_indicadores, title="Indicadores Globais de CO₂", icon="📈"),
        st.Page(pagina_noticias, title="Panorama de Notícias & NLP", icon="📰"),
        st.Page(pagina_seeg_brasil, title="SEEG - Emissões Brasil", icon="🇧🇷"),
        st.Page(pagina_arquivos, title="Gestão de Arquivos & Dados", icon="📁"),
    ]
})

# Rodapé no Sidebar
st.sidebar.markdown("---")
st.sidebar.caption("🌍 **Projeto de Bloco - TP3**\nInstituto Infnet | Aluno: Nelson C. de Araujo")

# Executa a página selecionada
navegacao.run()

