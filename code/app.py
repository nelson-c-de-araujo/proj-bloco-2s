import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from wordcloud import WordCloud

# Configuração da URL da API via variável de ambiente (com fallback local padrão)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# Garantir visibilidade do diretório raiz para importar src em casos de fallback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from src.scrape_news import extrair_noticias_ods13
    from src.process_data import processar_dados, padronizar_data, ordenar_noticias_por_data
    from src.scrape_seeg_brasil import extrair_seeg_brasil_estados_selenium
except ImportError:
    pass

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

if "ano_selecionado_co2" not in st.session_state:
    st.session_state.ano_selecionado_co2 = [2022, 2023, 2024]


# --- FUNÇÕES DE CONSUMO HTTP VIA FASTAPI (COM CACHE E RESILIÊNCIA) ---

@st.cache_data(show_spinner="Carregando medições reais de CO₂...")
def obter_dados_co2():
    """Consome a série histórica oficial de CO2 (NOAA Mauna Loa) via API ou fallback local."""
    try:
        resp = requests.get(f"{API_URL}/co2", timeout=3)
        if resp.status_code == 200:
            dados = resp.json().get("dados", [])
            if dados:
                return pd.DataFrame(dados)
    except Exception:
        pass

    for caminho in ["data/processed/co2_mensal_noaa_limpo.csv", "data/raw/co2_mensal_noaa.csv"]:
        if os.path.exists(caminho):
            return pd.read_csv(caminho)
    return pd.DataFrame()


@st.cache_data(show_spinner="Carregando notícias socioambientais...")
def obter_noticias_relevantes():
    """Consome as notícias climáticas e institucionais via API ou fallback local com ordenação cronológica."""
    df_resultado = pd.DataFrame()
    try:
        resp = requests.get(f"{API_URL}/noticias", timeout=3)
        if resp.status_code == 200:
            itens = resp.json().get("noticias", [])
            if itens:
                df_resultado = pd.DataFrame(itens)
    except Exception:
        pass

    if df_resultado.empty:
        for caminho in ["data/processed/noticias_ods13_limpo.csv", "data/raw/noticias_ods13.csv"]:
            if os.path.exists(caminho):
                df_resultado = pd.read_csv(caminho)
                break

    if not df_resultado.empty and "ordenar_noticias_por_data" in globals():
        df_resultado = ordenar_noticias_por_data(df_resultado)
    return df_resultado


@st.cache_data
def obter_texto_nuvem():
    """Carrega o texto compilado para a geração da Nuvem de Palavras."""
    for caminho in ["data/processed/texto_nuvem_palavras.txt", "data/raw/conteudo_ods13.txt"]:
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return arquivo.read()
    return ""


@st.cache_data(show_spinner="Carregando dados nacionais do SEEG Brasil...")
def obter_dados_seeg_brasil():
    """Consome a tabela histórica de emissões por estado do SEEG Brasil via API ou fallback local."""
    try:
        resp = requests.get(f"{API_URL}/emissoes", timeout=3)
        if resp.status_code == 200:
            itens = resp.json().get("emissoes", [])
            if itens:
                return pd.DataFrame(itens)
    except Exception:
        pass

    for caminho in ["data/processed/seeg_brasil_estados_limpo.csv", "data/raw/seeg_brasil_estados.csv"]:
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
        st.info("### 📈 Indicadores Globais\nAcompanhe a evolução temporal das concentrações atmosféricas reais de CO₂ registradas pela NOAA (Mauna Loa).")
    with col2:
        st.info("### 📰 Notícias & Tendências\nExplore o panorama de matérias dos principais veículos de comunicação e os tópicos mais citados.")
    with col3:
        st.success("### 🇧🇷 SEEG - Emissões Brasil\nVisão completa a nível Brasil clusterizada pelas 27 Unidades Federativas (1990–2024).")

    st.markdown("---")
    
    st.markdown(f"""
    ### 🧭 Como Navegar pela Plataforma
    Utilize o menu lateral para alternar entre as diferentes seções:
    - **Visão Geral**: Apresentação da plataforma e síntese dos objetivos.
    - **Indicadores Globais de CO₂**: Séries históricas oficiais com medições mensais e tendências de concentração (ppm).
    - **Panorama de Notícias & NLP**: Acompanhamento jornalístico, resumos em tempo real e nuvem de tópicos.
    - **SEEG - Emissões Brasil**: Panorama nacional consolidado para todos os Estados brasileiros.
    - **Gestão de Arquivos & Dados**: Envio de dados, formulário de ingestão e download de relatórios.
    
    > 💡 **Integração Backend**: A plataforma consome dados via **API RESTful (FastAPI)** no endpoint configurado: `{API_URL}`.
    """)


def pagina_indicadores():
    st.title("📈 Indicadores Globais de Concentração de CO₂")
    st.caption("Séries históricas reais oficiais do Observatório de Mauna Loa (NOAA Global Monitoring Laboratory)")
    
    df_registros = obter_dados_co2()
    
    if df_registros.empty:
        st.warning("Não foi possível carregar a série de dados de CO₂ no momento.")
        return

    # Filtros laterais
    st.sidebar.markdown("### 🎛️ Filtros de Indicadores de CO₂")
    anos_disponiveis = sorted(df_registros["Ano"].unique().tolist())
    anos_selecionados = st.sidebar.multiselect(
        "Selecione os Anos:",
        options=anos_disponiveis,
        default=[a for a in [2022, 2023, 2024] if a in anos_disponiveis],
        help="Escolha os anos para avaliar a evolução da concentração de dióxido de carbono."
    )
    
    meses_filtrados = st.sidebar.multiselect(
        "Selecione os Meses:",
        options=TODOS_OS_MESES,
        default=st.session_state.meses_selecionados,
        help="Escolha os meses para filtrar os indicadores de concentração de CO₂."
    )
    st.session_state.meses_selecionados = meses_filtrados
    
    if st.sidebar.button("🧹 Restaurar Filtros"):
        st.session_state.meses_selecionados = TODOS_OS_MESES.copy()
        st.rerun()

    df_exibicao = df_registros.copy()
    if anos_selecionados:
        df_exibicao = df_exibicao[df_exibicao["Ano"].isin(anos_selecionados)]
    if meses_filtrados:
        df_exibicao = df_exibicao[df_exibicao["Mês"].isin(meses_filtrados)]

    col_m1, col_m2, col_m3 = st.columns(3)
    media_ppm = df_exibicao['Nível de CO2 (ppm)'].mean() if not df_exibicao.empty else 0
    pico_ppm = df_exibicao['Nível de CO2 (ppm)'].max() if not df_exibicao.empty else 0
    col_m1.metric("Média do Período (ppm)", f"{media_ppm:.2f}" if not df_exibicao.empty else "-")
    col_m2.metric("Pico Registrado (ppm)", f"{pico_ppm:.2f}" if not df_exibicao.empty else "-")
    col_m3.metric("Medições Analisadas", len(df_exibicao))

    st.markdown("---")
    col_tabela, col_grafico = st.columns([1, 2])
    with col_tabela:
        st.markdown("**Tabela de Registros Mensais (ppm)**")
        st.dataframe(
            df_exibicao[["Data de Registro", "Ano", "Mês", "Nível de CO2 (ppm)", "Tendência Ajustada (ppm)"]], 
            height=370, 
            hide_index=True,
            use_container_width=True
        )
    with col_grafico:
        st.markdown("**Evolução da Concentração Atmosférica de CO₂**")
        if not df_exibicao.empty:
            st.line_chart(data=df_exibicao, x='Data de Registro', y=['Nível de CO2 (ppm)', 'Tendência Ajustada (ppm)'])
            st.caption("Valores observados em partes por milhão (ppm) e curva de tendência dessazonalizada calculada pela NOAA.")
        else:
            st.warning("Selecione ao menos um ano e mês nos filtros para visualizar a curva de dados.")


def pagina_noticias():
    st.title("📰 Panorama de Notícias & Temas em Alta (ODS 13)")
    st.caption("Acompanhe notícias em tempo real e análises temáticas sobre emergência climática e sustentabilidade")
    
    # Barra de Ações Rápidas (Atualização via API POST)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Atualizar Notícias Agora", type="primary", help="Dispara a extração ao vivo via API e atualiza os temas em alta"):
            with st.spinner("Conectando à API e sincronizando as notícias mais recentes..."):
                sucesso = False
                try:
                    resp = requests.post(f"{API_URL}/noticias/sincronizar", timeout=60)
                    if resp.status_code == 200:
                        sucesso = True
                except Exception:
                    pass

                # Fallback se a API não estiver respondendo diretamente ao trigger
                if not sucesso:
                    try:
                        extrair_noticias_ods13()
                        processar_dados()
                        sucesso = True
                    except Exception:
                        sucesso = False

                if sucesso:
                    st.cache_data.clear()
                    st.success("Notícias e temas em alta sincronizados com sucesso!")
                    st.rerun()
                else:
                    st.error("Instabilidade momentânea ao sincronizar notícias. Tente novamente em instantes.")
    with col_info:
        st.caption("ℹ️ Clique para acionar a sincronização em tempo real e recarregar os dados.")

    # Formulário de Cadastro / Envio de Notícia (Consumo de POST via API)
    with st.expander("➕ Cadastrar Nova Notícia no Sistema"):
        with st.form("form_cadastro_noticia", clear_on_submit=True):
            st.markdown("Envie uma publicação relevante sobre clima para enriquecer o acervo:")
            col_cad1, col_cad2, col_cad3 = st.columns([2, 1, 1])
            with col_cad1:
                cad_titulo = st.text_input("Título da Matéria*", placeholder="Ex: Investimentos em energia solar crescem no Brasil")
            with col_cad2:
                cad_fonte = st.text_input("Veículo / Fonte*", placeholder="Ex: Portal de Notícias Ambientais")
            with col_cad3:
                cad_data = st.date_input("Data de Publicação*", value=datetime.today(), format="DD/MM/YYYY")

            col_cad4, col_cad5 = st.columns([1, 2])
            with col_cad4:
                cad_link = st.text_input("Link de Acesso*", placeholder="https://exemplo.com/materia")
            with col_cad5:
                cad_resumo = st.text_area("Resumo da Notícia*", placeholder="Síntese dos principais pontos abordados na matéria...", height=70)

            btn_salvar = st.form_submit_button("📤 Salvar Notícia")
            if btn_salvar:
                if not cad_titulo.strip() or not cad_fonte.strip() or not cad_link.strip() or not cad_resumo.strip():
                    st.warning("Por favor, preencha todos os campos obrigatórios marcados com *.")
                else:
                    data_formatada = cad_data.strftime("%d/%m/%Y") if hasattr(cad_data, "strftime") else str(cad_data)
                    payload = {
                        "data": data_formatada,
                        "fonte": cad_fonte.strip(),
                        "titulo": cad_titulo.strip(),
                        "link": cad_link.strip(),
                        "resumo": cad_resumo.strip(),
                        "categoria": "ODS 13 - Ação Climática"
                    }
                    cadastrado = False
                    try:
                        resp_post = requests.post(f"{API_URL}/noticias", json=payload, timeout=6)
                        if resp_post.status_code == 201:
                            cadastrado = True
                        elif resp_post.status_code == 409:
                            st.warning("Esta notícia já existe cadastrada no sistema.")
                        else:
                            st.error(f"Erro ao salvar: {resp_post.json().get('detail', 'Falha na requisição')}")
                    except Exception:
                        # Fallback local direto se a API estiver offline
                        caminho_raw = "data/raw/noticias_ods13.csv"
                        df_raw = pd.read_csv(caminho_raw) if os.path.exists(caminho_raw) else pd.DataFrame()
                        if not df_raw.empty and "titulo" in df_raw.columns and cad_titulo.strip() in df_raw["titulo"].values:
                            st.warning("Esta notícia já existe cadastrada no sistema.")
                        else:
                            df_raw = pd.concat([df_raw, pd.DataFrame([payload])], ignore_index=True)
                            df_raw = ordenar_noticias_por_data(df_raw)
                            df_raw.to_csv(caminho_raw, index=False, encoding="utf-8-sig")

                            # Atualiza também a base processada
                            caminho_limpo = "data/processed/noticias_ods13_limpo.csv"
                            nova_limpa = dict(payload)
                            nova_limpa["titulo_limpo"] = payload["titulo"].lower()
                            df_limpo = pd.read_csv(caminho_limpo) if os.path.exists(caminho_limpo) else pd.DataFrame()
                            df_limpo = pd.concat([df_limpo, pd.DataFrame([nova_limpa])], ignore_index=True)
                            df_limpo = ordenar_noticias_por_data(df_limpo)
                            df_limpo.to_csv(caminho_limpo, index=False, encoding="utf-8-sig")
                            cadastrado = True

                    if cadastrado:
                        st.cache_data.clear()
                        st.success("Notícia cadastrada e ordenada com sucesso!")
                        st.rerun()

    st.markdown("---")

    st.sidebar.markdown("### 🔎 Busca Textual")
    termo = st.sidebar.text_input(
        "Pesquisar termo ou fonte:",
        value=st.session_state.termo_pesquisa_noticia,
        placeholder="Ex: energia, transição, metas..."
    )
    st.session_state.termo_pesquisa_noticia = termo
    
    if st.sidebar.button("🧹 Limpar Pesquisa"):
        st.session_state.termo_pesquisa_noticia = ""
        st.rerun()

    noticias_carregadas = obter_noticias_relevantes()

    if not noticias_carregadas.empty:
        if st.session_state.termo_pesquisa_noticia:
            busca = st.session_state.termo_pesquisa_noticia.lower()
            mascara_busca = (
                noticias_carregadas['titulo'].str.lower().str.contains(busca, na=False) |
                noticias_carregadas['fonte'].str.lower().str.contains(busca, na=False) |
                noticias_carregadas['resumo'].str.lower().str.contains(busca, na=False)
            )
            if 'data' in noticias_carregadas.columns:
                mascara_busca = mascara_busca | noticias_carregadas['data'].astype(str).str.lower().str.contains(busca, na=False)
            noticias_filtradas = noticias_carregadas[mascara_busca]
        else:
            noticias_filtradas = noticias_carregadas

        col_n1, col_n2 = st.columns(2)
        col_n1.metric("Publicações Encontradas", len(noticias_filtradas))
        col_n2.metric("Veículos de Comunicação", noticias_filtradas['fonte'].nunique() if not noticias_filtradas.empty else 0)
        
        colunas_tabela = ['data', 'fonte', 'titulo', 'resumo', 'link'] if 'data' in noticias_filtradas.columns else ['fonte', 'titulo', 'resumo', 'link']

        st.dataframe(
            noticias_filtradas[colunas_tabela], 
            column_config={
                "data": st.column_config.TextColumn("Data de Publicação", width="small", help="Data de publicação ou veiculação da matéria"),
                "fonte": "Veículo / Fonte",
                "titulo": "Título da Publicação",
                "resumo": "Resumo / Lead da Matéria",
                "link": st.column_config.LinkColumn("Acessar Matéria")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma matéria carregada no momento. Utilize o botão acima para sincronizar.")

    st.markdown("---")
    st.subheader("💬 Nuvem de Palavras - Tópicos em Destaque")
    st.write("Conceitos e temas mais recorrentes nos conteúdos jornalísticos e institucionais analisados:")

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


def pagina_seeg_brasil():
    st.title("🇧🇷 SEEG - Emissões Brasil por Estado")
    st.caption("Visão histórica consolidada das emissões brutas (1990–2024) desagregadas por Unidade Federativa")
    
    st.markdown("""
    > **Panorama Nacional**: Esta página apresenta os dados oficiais da **Plataforma SEEG**.
    > Permite analisar a evolução das emissões em todo o território nacional e comparar o desempenho dos estados brasileiros.
    """)

    # Barra de Ações Rápidas (Sincronização via API POST)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Sincronizar Plataforma SEEG", type="primary", help="Acessa a plataforma online do SEEG e extrai a tabela consolidada mais recente"):
            with st.spinner("Conectando à API e sincronizando dados oficiais do SEEG Brasil..."):
                sucesso = False
                try:
                    resp = requests.post(f"{API_URL}/emissoes/sincronizar", timeout=90)
                    if resp.status_code == 200:
                        sucesso = True
                except Exception:
                    pass

                # Fallback se a API não estiver respondendo ao trigger
                if not sucesso:
                    try:
                        extrair_seeg_brasil_estados_selenium()
                        processar_dados()
                        sucesso = True
                    except Exception:
                        sucesso = False

                if sucesso:
                    st.cache_data.clear()
                    st.success("Dados do SEEG Brasil sincronizados com sucesso!")
                    st.rerun()
                else:
                    st.error("Não foi possível sincronizar com a plataforma no momento. Tente novamente mais tarde.")
    with col_info:
        st.caption("ℹ️ Clique para consultar a plataforma oficial e sincronizar a tabela de emissões estaduais.")

    st.markdown("---")

    df_brasil = obter_dados_seeg_brasil()

    if df_brasil.empty:
        st.warning("Nenhum registro de emissões nacionais disponível. Clique no botão acima para sincronizar.")
        return

    # Lista de anos disponíveis
    colunas_anos = [c for c in df_brasil.columns if c.isdigit()]
    ultimo_ano = colunas_anos[-1] if colunas_anos else "2024"
    primeiro_ano = colunas_anos[0] if colunas_anos else "1990"

    # Separar linha de Total, Não Alocado e dados estaduais
    # Unidades Federativas oficiais = 26 Estados + Distrito Federal = exatamente 27 UFs
    df_estados = df_brasil[~df_brasil["Estado"].isin(["Total", "total", "Não Alocado"])].copy()
    linha_total = df_brasil[df_brasil["Estado"].isin(["Total", "total"])]
    linha_nao_alocado = df_brasil[df_brasil["Estado"].isin(["Não Alocado"])]

    # Métricas de destaque
    total_recente = linha_total[ultimo_ano].values[0] if not linha_total.empty and ultimo_ano in linha_total.columns else df_brasil[ultimo_ano].sum()
    total_1990 = linha_total[primeiro_ano].values[0] if not linha_total.empty and primeiro_ano in linha_total.columns else df_brasil[primeiro_ano].sum()
    variacao_pct = ((total_recente - total_1990) / total_1990) * 100 if total_1990 > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estados Monitorados", f"{len(df_estados)}")
    col2.metric(f"Emissão Brasil em {ultimo_ano} (t CO₂e)", f"{total_recente:,.0f}".replace(",", "."))
    col3.metric(f"Emissão Brasil em {primeiro_ano} (t CO₂e)", f"{total_1990:,.0f}".replace(",", "."))
    col4.metric(f"Variação ({primeiro_ano} vs {ultimo_ano})", f"{variacao_pct:+.1f}%")

    st.caption("ℹ️ **Nota Metodológica SEEG**: As **27 Unidades Federativas** (26 estados e o Distrito Federal) correspondem à totalidade dos entes subnacionais monitorados. O volume nacional consolidado inclui também a parcela *'Não Alocado'*, representativa de emissões não regionalizadas a um estado específico (como aviação doméstica e operações offshore em alto-mar).")

    st.markdown("---")

    # Filtro de Estados para comparação personalizada
    st.sidebar.markdown("### 🗺️ Comparativo entre Estados")
    lista_todos_estados = sorted(df_estados["Estado"].unique().tolist())
    estados_selecionados = st.sidebar.multiselect(
        "Selecione Estados para Comparar:",
        options=lista_todos_estados,
        default=[e for e in ["Rio de Janeiro", "São Paulo", "Minas Gerais", "Pará", "Mato Grosso"] if e in lista_todos_estados],
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
            df_melt = df_filtro_est.melt(id_vars=["Estado"], value_vars=colunas_anos, var_name="Ano", value_name="Emissão (t CO₂e)")
            df_melt["Ano"] = df_melt["Ano"].astype(int)
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


def pagina_arquivos():
    st.title("📁 Gestão de Arquivos & Upload/Download")
    st.caption("Intercâmbio de dados e exportação de relatórios analíticos")
    
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
                colunas_num = df_custom.select_dtypes(include=['float64', 'int64']).columns
                eixo_y = "Nível de CO2 (ppm)" if "Nível de CO2 (ppm)" in df_custom.columns else (colunas_num[0] if len(colunas_num) > 0 else None)
                
                if eixo_y:
                    st.line_chart(data=df_custom, x=eixo_x, y=eixo_y)
                else:
                    st.line_chart(data=df_custom)
            except Exception:
                st.error("Erro ao ler o arquivo CSV. Verifique a formatação.")

    with col_down:
        st.markdown("### 📥 Download de Relatórios")
        st.write("Exporte a base histórica oficial de **CO₂ da NOAA**:")
        df_co2 = obter_dados_co2()
        if not df_co2.empty:
            csv_co2 = df_co2.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Baixar Série Histórica NOAA CO₂ (CSV)",
                data=csv_co2,
                file_name="serie_historica_co2_noaa.csv",
                mime="text/csv"
            )
            
        st.markdown("---")
        st.write("Exporte a base oficial de **Emissões SEEG Brasil**:")
        df_seeg = obter_dados_seeg_brasil()
        if not df_seeg.empty:
            csv_seeg = df_seeg.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Baixar Tabela Completa SEEG Brasil (CSV)",
                data=csv_seeg,
                file_name="seeg_brasil_estados.csv",
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
st.sidebar.caption(f"🌍 **Projeto de Bloco - Etapa 4**\nInstituto Infnet | Aluno: Nelson C. de Araujo\n*Backend API:* `{API_URL}`")

# Executa a página selecionada
navegacao.run()
