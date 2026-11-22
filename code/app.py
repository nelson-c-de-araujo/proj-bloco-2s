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
    from src.decision_agent import executar_agente_decisao, extrair_metricas_analiticas
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
    st.title("🌍 Plataforma Integrada de Ação Climática & Governança ESG")
    st.subheader("Monitoramento de Emissões, Indicadores Globais e Tomada de Decisão com IA (ODS 13)")
    st.caption("Instituto Infnet | Ciência de Dados e Inteligência Artificial | Aluno: Nelson C. de Araujo")
    
    st.markdown("""
    Esta solução foi concebida para superar a fragmentação de dados socioambientais e viabilizar **decisões práticas e fundamentadas** 
    em sustentabilidade e governança corporativa, diretamente alinhadas ao **Objetivo de Desenvolvimento Sustentável 13 (Ação Contra a Mudança Global do Clima)**.
    
    Ao integrar o ciclo de vida completo da **Ciência de Dados Aplicada** — da extração automatizada de fontes oficiais à inteligência 
    estratégica com Modelos de Linguagem (LLMs) —, o sistema transforma dados complexos em **planos de ação executivos**.
    """)
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("### 📈 Indicadores CO₂\nSéries temporais oficiais da NOAA (Mauna Loa) com concentrações mensais e tendência global.")
    with col2:
        st.info("### 🇧🇷 SEEG Emissões\nInventário histórico das 27 UFs do Brasil (1990–2024) extraído via Selenium dinâmico.")
    with col3:
        st.info("### 📰 Notícias & NLP\nAcervo jornalístico socioambiental atualizado via scraping com extração profunda de resumos.")
    with col4:
        st.success("### 🎯 Agente Decisório\nA cereja do bolo: inteligência com LLM e Data Grounding para guiar políticas e estratégias ESG.")

    st.markdown("---")
    
    st.markdown(f"""
    ### 🧭 Estrutura da Apresentação & Navegação pelo Painel

    A plataforma está organizada em dois blocos complementares no menu lateral:

    #### 📊 1. Monitoramento e Dados (A Base Empírica)
    1. **🏠 Visão Geral da Solução**: Ponto de partida com o panorama de negócio, metodologia e arquitetura da solução.
    2. **📈 Indicadores Globais de CO₂**: Acompanhamento do contexto macroclimático do planeta através das medições da NOAA (ppm).
    3. **🇧🇷 SEEG - Emissões por Estado**: Panorama desagregado das 27 Unidades Federativas do Brasil (1990–2024), com rankings de maiores emissores e gráficos temporais comparativos.
    4. **📰 Panorama de Notícias & NLP**: Monitoramento de matérias jornalísticas socioambientais com mineração de termos e nuvem semântica de tópicos em alta.
    5. **📁 Gestão de Arquivos & Dados**: Módulo de intercâmbio com upload de bases customizadas e download dos dados oficiais consolidados.

    #### 🎯 2. Inteligência & Decisão ESG (O Ponto Alto da Aplicação)
    * **🎯 Agente Decisório ESG (ODS 13)**: O ápice do ciclo de Ciência de Dados. Cruza os dados do SEEG, NOAA e notícias, aplica cálculos estatísticos prévios (*Data Grounding*) e aciona Inteligência Artificial para gerar diagnósticos de risco e planos de ação sob medida para gestores públicos, executivos de sustentabilidade e investidores.

    ---
    > 💡 **Integração Desacoplada**: Todo o backend opera via microsserviço **API RESTful (FastAPI)** no endpoint configurado: `{API_URL}`.
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


def pagina_llm():
    st.title("🤖 Assistente de Inteligência Artificial (LLM)")
    st.caption("Ferramenta Interativa com LLM integrada. Faça bom uso!")
    
    col_origem, col_tipo = st.columns([2, 1])
    
    with col_origem:
        fonte_dados = st.radio(
            "Origem do Texto para Análise:",
            options=["📰 Selecionar Notícia do Acervo", "✍️ Digitar / Colar Texto Próprio"],
            horizontal=True
        )
    
    with col_tipo:
        tarefas = [
            ("resumo", "📝 Resumo Executivo"),
            ("sentimento", "⚖️ Tom e Impacto Climático"),
            ("insights", "💡 Insights Socioambientais")
        ]
        tarefa_selecionada = st.selectbox(
            "Tarefa desejada:",
            options=[t[0] for t in tarefas],
            format_func=lambda x: dict(tarefas)[x]
        )

    texto_para_processar = ""
    
    if fonte_dados == "📰 Selecionar Notícia do Acervo":
        df_noticias = obter_noticias_relevantes()
        if not df_noticias.empty:
            noticia_escolhida = st.selectbox(
                "Escolha a notícia:",
                options=df_noticias["titulo"].tolist()
            )
            item = df_noticias[df_noticias["titulo"] == noticia_escolhida].iloc[0]
            texto_para_processar = f"Título: {item['titulo']}\nData: {item.get('data', '-')}\nVeículo: {item['fonte']}\nConteúdo: {item.get('resumo', '')}"
            st.info(f"**Texto selecionado:**\n\n{texto_para_processar}")
        else:
            st.warning("Nenhuma notícia disponível na base. Use a opção de texto próprio.")
    else:
        texto_para_processar = st.text_area(
            "Insira o texto para a IA responder",
            placeholder="Exemplo: Os investimentos em energia solar no Brasil aumentaram 30% em 2024, impulsionados por incentivos à geração distribuída e políticas de transição ecológica...",
            height=120
        )

    with st.expander("⚙️ Parâmetros Avançados de Inferência (Opcional)"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            tokens = st.slider("Máximo de Novos Tokens", min_value=50, max_value=2048, value=1000, step=50, help="Defina um teto alto para que a resposta nunca seja truncada no meio.")
        with col_p2:
            temp = st.slider("Temperatura (Criatividade)", min_value=0.1, max_value=1.0, value=0.7, step=0.1)

    if st.button("⚡ Executar Processamento com IA", type="primary"):
        if not texto_para_processar or len(texto_para_processar.strip()) < 15:
            st.warning("Por favor, insira ou selecione um texto com pelo menos 15 caracteres para processamento.")
        else:
            with st.spinner("Enviando requisição, já já o modelo responde..."):
                payload = {
                    "texto": texto_para_processar.strip(),
                    "tipo_analise": tarefa_selecionada,
                    "max_novos_tokens": tokens,
                    "temperatura": temp
                }
                try:
                    resp = requests.post(f"{API_URL}/processar_texto", json=payload, timeout=90)
                    if resp.status_code == 200:
                        dados_resp = resp.json()
                        st.success("Processamento concluído com sucesso!")
                        
                        # Exibição estruturada do Response Model
                        st.markdown("### 📋 Resultado Gerado pelo Modelo")
                        st.markdown(f"> {dados_resp['resultado']}")
                        
                        # Metadados de execução
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        col_m1.metric("Status da Resposta", f"{resp.status_code} OK")
                        col_m2.metric("Tempo de Inferência", f"{dados_resp['tempo_execucao_segundos']} s")
                        col_m3.metric("Modelo Utilizado", dados_resp['modelo_utilizado'].split('/')[-1])
                        col_m4.metric("Tarefa Realizada", dados_resp['tipo_analise'].capitalize())
                    elif resp.status_code == 503:
                        st.error(f"⚠️ Serviço Local Indisponível (503): {resp.json().get('detail', 'O modelo local ainda não foi inicializado ou faltam pacotes PyTorch/Transformers.')}")
                    elif resp.status_code == 422:
                        st.warning(f"⚠️ Conteúdo Incompatível (422): {resp.json().get('detail', 'Entrada de dados não atende aos requisitos.')}")
                    else:
                        st.error(f"Erro na API (Status {resp.status_code}): {resp.json().get('detail', 'Falha na requisição.')}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Não foi possível conectar à API em `{API_URL}`. Certifique-se de que a API FastAPI está em execução (`uvicorn src.api:app --reload`).")
                except Exception as e:
                    st.error(f"Erro ao processar requisição: {str(e)}")


# ==========================================
# PÁGINA DO AGENTE INTELIGENTE ESG (TP5)
# ==========================================

def pagina_agente_decisao():
    st.title("🎯 Agente Inteligente ESG — Tomada de Decisão (ODS 13)")
    st.caption("Ciclo Completo de Ciência de Dados Aplicada: Coleta ➔ Engenharia ➔ IA ➔ Decisão Estratégica")

    st.markdown("""
    Este agente demonstra como a **Ciência de Dados e a Inteligência Artificial** resolvem problemas reais de negócio e sustentabilidade.
    Ele cruza automaticamente os dados oficiais de emissões do **SEEG Brasil (1990–2024)**, medições de **CO₂ da NOAA** e notícias 
    socioambientais coletadas via web scraping, calculando evidências estatísticas em tempo real e gerando **pareceres executivos de governança**.
    """)

    # Carrega dados do SEEG para popular a lista de estados
    df_seeg = obter_dados_seeg_brasil()
    if df_seeg.empty:
        st.error("Base de dados de emissões do SEEG não localizada. Execute a sincronização dos dados.")
        return

    # Lista de estados para seleção
    estados_disponiveis = [e for e in df_seeg["Estado"].unique() if e != "Não Alocado"]
    if "Total" in estados_disponiveis:
        estados_disponiveis.remove("Total")
    estados_disponiveis = sorted(estados_disponiveis)
    estados_disponiveis.insert(0, "Brasil (Total Consolidado)")

    # Layout de controles interativos
    col_uf, col_perfil = st.columns([1, 1])

    with col_uf:
        estado_selecionado = st.selectbox(
            "📍 Selecione o Território / Unidade Federativa:",
            options=estados_disponiveis,
            index=estados_disponiveis.index("São Paulo") if "São Paulo" in estados_disponiveis else 0,
            help="Escolha o estado brasileiro ou o total nacional para avaliação do Agente."
        )

    with col_perfil:
        perfis_map = {
            "🏛️ Gestão Pública & Regulação (Políticas estaduais, fiscalização, transição justa)": "gestao_publica",
            "🏢 Governança Corporativa & ESG (Riscos regulatórios, cadeias Escopos 1-3, compliance)": "corporativo_esg",
            "💼 Investimento de Impacto & Riscos Climáticos (Due diligence climática, finanças verdes)": "investimento_impacto"
        }
        perfil_label = st.selectbox(
            "👤 Perfil do Tomador de Decisão:",
            options=list(perfis_map.keys()),
            help="Personaliza o tom, os riscos e as recomendações geradas pelo Agente de IA."
        )
        perfil_chave = perfis_map[perfil_label]

    # Obter métricas analíticas em tempo real (Grounding via Pandas)
    nome_busca = "Total" if estado_selecionado.startswith("Brasil") else estado_selecionado
    metricas = None
    try:
        if "extrair_metricas_analiticas" in globals():
            metricas = extrair_metricas_analiticas(nome_busca)
        else:
            # Consulta via API
            resp_met = requests.get(f"{API_URL}/agente/metricas", params={"estado": nome_busca}, timeout=3)
            if resp_met.status_code == 200:
                metricas = resp_met.json().get("metricas")
    except Exception:
        pass

    # Exibição de KPIs Quantitativos em Cards Métricos
    if metricas:
        st.markdown("### 📊 Evidências Estatísticas Coletadas (Data Grounding)")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        emissao_formatada = f"{metricas['emissao_2024_tco2e']:,.0f}".replace(",", ".")
        delta_quinq = f"{metricas['variacao_quinquenal_2020_2024_pct']:+.1f}% (2020-2024)"
        delta_color = "inverse" if metricas['variacao_quinquenal_2020_2024_pct'] > 0 else "normal"
        
        kpi1.metric("Emissões em 2024", f"{emissao_formatada} t CO₂e", delta=delta_quinq, delta_color=delta_color)
        kpi2.metric("Variação 1990–2024", f"{metricas['variacao_historica_1990_2024_pct']:+.1f}%", help="Variação total acumulada na série histórica")
        
        ranking_txt = f"{metricas['ranking_nacional_2024']}º de 27 UFs" if metricas['ranking_nacional_2024'] else "Consolidado Nacional"
        kpi3.metric("Ranking Nacional", ranking_txt, delta=f"{metricas['participacao_nacional_pct']:.1f}% do Brasil", delta_color="off")
        
        kpi4.metric("Risco Climático Preliminar", metricas['nivel_risco_climatico'], delta=f"Pico: {metricas['ano_pico_historico']}", delta_color="off")

        # Gráfico dinâmico da série histórica da UF
        anos = [c for c in df_seeg.columns if c.isdigit()]
        anos.sort(key=int)
        linha_uf = df_seeg[df_seeg["Estado"].str.lower() == nome_busca.lower()]
        if not linha_uf.empty:
            serie_grafico = linha_uf[anos].iloc[0].astype(float)
            df_plot = pd.DataFrame({"Ano": [int(a) for a in anos], "Emissões (t CO₂e)": serie_grafico.values})
            with st.expander("📈 Visualizar Trajetória Histórica das Emissões (1990–2024)", expanded=False):
                st.line_chart(df_plot.set_index("Ano"))
                st.caption(f"Curva histórica oficial de emissões brutas para {metricas['estado']} extraída da Plataforma SEEG.")

    st.markdown("---")

    # Área de interação e foco específico
    st.markdown("### 💬 Interação & Foco Estratégico do Decisor")
    pergunta_usuario = st.text_input(
        "Foco estratégico ou pergunta específica do decisor (opcional):",
        value="",
        placeholder="Exemplo: Quais medidas imediatas devem ser tomadas para conter as emissões do setor de transportes neste estado?",
        help="O Agente Inteligente analisará este questionamento e criará uma seção prioritária e dedicada no parecer final com orientações práticas."
    )

    with st.expander("⚙️ Configurações do Agente Inteligente & Motores de IA", expanded=True):
        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            opcoes_motor = {
                "⚡ Google Gemini 3.8 Flash (Recomendado — Parecer Completo, Profundo & Sem Cortes)": "gemini",
                "🧠 Motor Analítico Especialista ESG (Instantâneo 50ms — Zero Falhas e Alta Precisão)": "heuristico",
                "🤖 Modelo Local Hugging Face (Qwen2.5 — 100% Local na Máquina)": "local"
            }
            motor_label = st.radio(
                "Motor de Inteligência do Agente:",
                options=list(opcoes_motor.keys()),
                index=0,
                help="O Gemini oferece máxima profundidade executiva; o Heurístico responde instantaneamente; o Local roda na CPU/GPU."
            )
            motor_chave = opcoes_motor[motor_label]

        with col_cfg2:
            temp_agente = st.slider("Temperatura da IA", min_value=0.1, max_value=0.9, value=0.4, step=0.1, help="Valores menores (0.3 - 0.4) garantem rigor analítico e técnico.")
            tokens_max_agente = st.slider("Teto Máximo de Tokens", min_value=500, max_value=3000, value=2048, step=100, help="Espaço amplo de geração para que o parecer executivo nunca seja truncado.")

        chave_gemini_digitada = ""
        if motor_chave == "gemini":
            chave_env = os.getenv("GEMINI_API_KEY", "")
            ajuda_chave = "Chave gratuita gerada em https://aistudio.google.com/ (começa com AIza...)"
            if chave_env:
                st.success("✅ Chave da API do Google Gemini detectada automaticamente via variável de ambiente!")
                chave_gemini_digitada = chave_env
            else:
                chave_gemini_digitada = st.text_input(
                    "🔑 Chave Google AI Studio (Gemini API Key):",
                    value="",
                    type="password",
                    placeholder="Cole aqui sua chave (ex.: AIzaSy...) - ⚠️ Importante: Sua chave não é salva em nenhum arquivo. Ninguém, além de você, tem acesso à ela.",
                    help=ajuda_chave
                )
                if not chave_gemini_digitada:
                    st.info("💡 **Como obter em 30 segundos (Grátis):** Acesse [aistudio.google.com](https://aistudio.google.com/) ➔ Faça login com o Google ➔ Clique em *'Get API key'* ➔ *'Create API key'*. É 100% gratuito!")

    # Botão de Ação Principal
    if st.button("🚀 Acionar Agente e Gerar Parecer Estratégico", type="primary", use_container_width=True):
        if motor_chave == "gemini" and not chave_gemini_digitada:
            st.warning("⚠️ Para utilizar o Google Gemini, informe sua chave gratuita do Google AI Studio no campo acima ou selecione o 'Motor Analítico Especialista ESG' para resposta imediata!")
        else:
            with st.spinner(f"O Agente Inteligente está cruzando dados do SEEG, NOAA e notícias para formular a decisão estratégica de {estado_selecionado}..."):
                parecer_final = ""
                modelo_usado = ""
                tempo_exec = 0.0
                
                # Tentativa 1: Via API FastAPI
                sucesso_api = False
                try:
                    payload = {
                        "estado": nome_busca,
                        "perfil_decisor": perfil_chave,
                        "pergunta_adicional": pergunta_usuario.strip() if pergunta_usuario else None,
                        "usar_modelo_llm": motor_chave != "heuristico",
                        "motor_ia": motor_chave,
                        "api_key_gemini": chave_gemini_digitada.strip() if chave_gemini_digitada else None,
                        "temperatura": temp_agente,
                        "max_tokens": tokens_max_agente
                    }
                    resp = requests.post(f"{API_URL}/agente/decisao", json=payload, timeout=90)
                    if resp.status_code == 200:
                        dados = resp.json()
                        parecer_final = dados.get("parecer_decisorio", "")
                        modelo_usado = dados.get("modelo_utilizado", "")
                        tempo_exec = dados.get("tempo_execucao_segundos", 0.0)
                        sucesso_api = True
                except Exception:
                    sucesso_api = False

                # Tentativa 2: Fallback local direto
                if not sucesso_api:
                    try:
                        if "executar_agente_decisao" in globals():
                            dados = executar_agente_decisao(
                                estado=nome_busca,
                                perfil_decisor=perfil_chave,
                                pergunta_adicional=pergunta_usuario.strip() if pergunta_usuario else None,
                                usar_modelo_llm=motor_chave != "heuristico",
                                motor_ia=motor_chave,
                                api_key_gemini=chave_gemini_digitada.strip() if chave_gemini_digitada else None,
                                temperatura=temp_agente,
                                max_tokens=tokens_max_agente
                            )
                            parecer_final = dados.get("parecer_decisorio", "")
                            modelo_usado = dados.get("modelo_utilizado", "")
                            tempo_exec = dados.get("tempo_execucao_segundos", 0.0)
                            sucesso_api = True
                    except Exception as ex:
                        st.error(f"Erro ao gerar parecer com o agente: {str(ex)}")

            if parecer_final:
                st.success("Parecer Estratégico elaborado com sucesso!")
                
                # Exibição do Parecer
                st.markdown(parecer_final)
                
                st.markdown("---")
                
                # Metadados de Execução e Auditoria
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("Território Avaliado", estado_selecionado)
                m_c2.metric("Perfil da Decisão", perfil_chave.replace('_', ' ').title())
                m_c3.metric("Tempo de Síntese", f"{tempo_exec:.2f} s")
                m_c4.metric("Origem do Processamento", "FastAPI (HTTP)" if sucesso_api else "Fallback Local")
                
                # Download do Parecer
                st.download_button(
                    label="📥 Baixar Parecer Executivo em Markdown (.md)",
                    data=parecer_final,
                    file_name=f"parecer_esg_ods13_{nome_busca.lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
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
# CONFIGURAÇÃO DE NAVEGAÇÃO MULTIPÁGINAS (TP5)
# ==========================================

navegacao = st.navigation({
    "Monitoramento e Dados": [
        st.Page(pagina_inicio, title="Visão Geral da Solução", icon="🏠", default=True),
        st.Page(pagina_indicadores, title="Indicadores Globais de CO₂", icon="📈"),
        st.Page(pagina_seeg_brasil, title="SEEG - Emissões por Estado", icon="🇧🇷"),
        st.Page(pagina_noticias, title="Panorama de Notícias & NLP", icon="📰"),
        st.Page(pagina_arquivos, title="Gestão de Arquivos & Dados", icon="📁"),
    ],
    "Inteligência & Decisão ESG": [
        st.Page(pagina_agente_decisao, title="Agente Decisório ESG (ODS 13)", icon="🎯"),
    ]
})

# Rodapé no Sidebar
st.sidebar.markdown("---")
st.sidebar.caption(f"🌍 **Projeto de Bloco - TP5 (Solução Final)**\nInstituto Infnet | Aluno: Nelson C. de Araujo\n*Backend API:* `{API_URL}`")

# Executa a página selecionada
navegacao.run()
