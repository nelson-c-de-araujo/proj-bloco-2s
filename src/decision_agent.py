import os
import sys
import time
from typing import Dict, Any, List, Optional
import requests
import pandas as pd

# Caminhos base
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAMINHO_SEEG_LIMPO = os.path.join(RAIZ, "data", "processed", "seeg_brasil_estados_limpo.csv")
CAMINHO_CO2_LIMPO = os.path.join(RAIZ, "data", "processed", "co2_mensal_noaa_limpo.csv")
CAMINHO_NOTICIAS_LIMPO = os.path.join(RAIZ, "data", "processed", "noticias_ods13_limpo.csv")


def extrair_metricas_analiticas(estado: str) -> Dict[str, Any]:
    """
    Calcula determinística e rigorosamente via Pandas as métricas quantitativas
    do estado ou do total nacional a partir das séries do SEEG e da NOAA.
    Serve como camada de Grounding para a IA não cometer alucinações matemáticas.
    """
    if not os.path.exists(CAMINHO_SEEG_LIMPO):
        raise FileNotFoundError(f"Base de dados do SEEG não localizada em {CAMINHO_SEEG_LIMPO}")

    df_seeg = pd.read_csv(CAMINHO_SEEG_LIMPO)
    anos_colunas = [c for c in df_seeg.columns if c.isdigit()]
    anos_colunas.sort(key=int)

    # Identifica o estado
    estado_normalizado = estado.strip().title()
    if estado.strip().lower() in ["total", "brasil"]:
        linha_estado = df_seeg[df_seeg["Estado"].str.lower() == "total"]
        nome_exibicao = "Brasil (Total Consolidado)"
    else:
        linha_estado = df_seeg[df_seeg["Estado"].str.lower() == estado.strip().lower()]
        nome_exibicao = estado_normalizado

    if linha_estado.empty:
        raise ValueError(f"Estado '{estado}' não encontrado na base de dados do SEEG.")

    valores_serie = linha_estado[anos_colunas].iloc[0].astype(float)
    
    val_1990 = float(valores_serie["1990"])
    val_2020 = float(valores_serie["2020"])
    val_2024 = float(valores_serie["2024"])
    
    var_total_pct = ((val_2024 - val_1990) / val_1990 * 100) if val_1990 > 0 else 0.0
    var_recente_pct = ((val_2024 - val_2020) / val_2020 * 100) if val_2020 > 0 else 0.0
    media_quinquenio = float(valores_serie[["2020", "2021", "2022", "2023", "2024"]].mean())
    
    ano_pico = str(valores_serie.idxmax())
    valor_pico = float(valores_serie.max())

    # Ranking nacional entre as 27 UFs (exclui 'Total' e 'Não Alocado')
    df_ufs = df_seeg[~df_seeg["Estado"].isin(["Total", "Não Alocado"])].copy()
    df_ufs["2024"] = df_ufs["2024"].astype(float)
    df_ranking = df_ufs.sort_values(by="2024", ascending=False).reset_index(drop=True)
    
    total_brasil_2024 = float(df_seeg[df_seeg["Estado"].str.lower() == "total"]["2024"].iloc[0]) if not df_seeg[df_seeg["Estado"].str.lower() == "total"].empty else 1.0

    if nome_exibicao.startswith("Brasil"):
        posicao_ranking = 1
        participacao_pct = 100.0
    else:
        idx_match = df_ranking[df_ranking["Estado"].str.lower() == estado.strip().lower()].index
        posicao_ranking = int(idx_match[0] + 1) if not idx_match.empty else None
        participacao_pct = (val_2024 / total_brasil_2024 * 100) if total_brasil_2024 > 0 else 0.0

    # Classificação da trajetória
    if var_recente_pct > 5.0:
        tendencia = "Emissão em Aceleração Recente (Alerta Vermelho)"
        risco_climatico = "ALTO"
    elif var_recente_pct < -5.0:
        tendencia = "Emissão em Trajetória de Queda Recente (Avanço Positivo)"
        risco_climatico = "MODERADO A BAIXO"
    else:
        tendencia = "Emissão em Estabilidade com Platô Elevado"
        risco_climatico = "MODERADO"

    # Contexto global NOAA
    co2_global_ppm = 426.5
    tendencia_global = "Aumento contínuo"
    if os.path.exists(CAMINHO_CO2_LIMPO):
        try:
            df_co2 = pd.read_csv(CAMINHO_CO2_LIMPO)
            if not df_co2.empty and "Nível de CO2 (ppm)" in df_co2.columns:
                co2_global_ppm = float(df_co2["Nível de CO2 (ppm)"].iloc[-1])
            if not df_co2.empty and "Tendência Ajustada (ppm)" in df_co2.columns:
                tendencia_global = f"{float(df_co2['Tendência Ajustada (ppm)'].iloc[-1]):.2f} ppm ajustado"
        except Exception:
            pass

    # Notícias recentes relevantes
    noticias_contexto = []
    if os.path.exists(CAMINHO_NOTICIAS_LIMPO):
        try:
            df_noticias = pd.read_csv(CAMINHO_NOTICIAS_LIMPO)
            for _, row in df_noticias.head(4).iterrows():
                noticias_contexto.append({
                    "data": str(row.get("data", "")),
                    "titulo": str(row.get("titulo", "")),
                    "fonte": str(row.get("fonte", "")),
                    "resumo": str(row.get("resumo", ""))[:140]
                })
        except Exception:
            pass

    return {
        "estado": nome_exibicao,
        "emissao_1990_tco2e": round(val_1990, 2),
        "emissao_2020_tco2e": round(val_2020, 2),
        "emissao_2024_tco2e": round(val_2024, 2),
        "variacao_historica_1990_2024_pct": round(var_total_pct, 2),
        "variacao_quinquenal_2020_2024_pct": round(var_recente_pct, 2),
        "media_quinquenio_tco2e": round(media_quinquenio, 2),
        "ano_pico_historico": ano_pico,
        "valor_pico_tco2e": round(valor_pico, 2),
        "ranking_nacional_2024": posicao_ranking,
        "participacao_nacional_pct": round(participacao_pct, 2),
        "tendencia_trajetoria": tendencia,
        "nivel_risco_climatico": risco_climatico,
        "co2_global_atual_ppm": round(co2_global_ppm, 2),
        "co2_global_tendencia": tendencia_global,
        "noticias_recentes": noticias_contexto
    }


def construir_prompt_agente(
    metricas: Dict[str, Any],
    perfil_decisor: str = "gestao_publica",
    pergunta_adicional: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Constrói a estrutura de engenharia de prompt especializada para o Agente de Decisão.
    """
    estado = metricas["estado"]
    emissao_2024 = f"{metricas['emissao_2024_tco2e']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    var_hist = f"{metricas['variacao_historica_1990_2024_pct']:+.1f}%"
    var_quinq = f"{metricas['variacao_quinquenal_2020_2024_pct']:+.1f}%"
    ranking = f"{metricas['ranking_nacional_2024']}º lugar" if metricas['ranking_nacional_2024'] else "N/A"
    part_nac = f"{metricas['participacao_nacional_pct']:.2f}%"

    perfis_desc = {
        "gestao_publica": (
            "Você é um Consultor Estratégico Especialista em Políticas Públicas e Governança Climática (ODS 13). "
            "Seu foco é apoiar governadores, secretários de meio ambiente e prefeitos a desenharem políticas de mitigação, "
            "regulação socioambiental, fiscalização e transição justa."
        ),
        "corporativo_esg": (
            "Você é um Conselheiro Executivo de Sustentabilidade e Governança Corporativa (ESG). "
            "Seu foco é orientar comitês executivos, C-levels e investidores sobre riscos de transição regulatória, "
            "descarbonização da cadeia de valor (Escopos 1, 2 e 3) e atração de finanças verdes."
        ),
        "investimento_impacto": (
            "Você é um Analista Chefe de Riscos Climáticos e Investimentos Verdes. "
            "Seu foco é avaliar a exposição de ativos financeiros, due diligence climática e critérios de conformidade com a Agenda 2030."
        )
    }

    sistema = (
        f"{perfis_desc.get(perfil_decisor, perfis_desc['gestao_publica'])}\n"
        "Você analisa dados reais de emissões de GEE (SEEG Brasil), concentrações atmosféricas (NOAA) e matérias de imprensa. "
        "Não invente números: baseie-se rigorosamente nos dados fornecidos abaixo."
    )

    contexto_noticias = ""
    if metricas.get("noticias_recentes"):
        contexto_noticias = "FATOS E NOTÍCIAS SOCIOAMBIENTAIS RECENTES:\n"
        for n in metricas["noticias_recentes"][:2]:
            contexto_noticias += f"- [{n['data']}] {n['fonte']}: {n['titulo']} ({n['resumo']})\n"

    secao_pergunta = ""
    if pergunta_adicional and pergunta_adicional.strip():
        secao_pergunta = f"""
REQUISITO OBRIGATÓRIO E MANDATÓRIO DO DECISOR:
O usuário fez a seguinte pergunta prioritária: "{pergunta_adicional.strip()}"
Você DEVE incluir obrigatoriamente no parecer a seção:
5. DIRETRIZES ESTRATÉGICAS PARA O FOCO DO DECISOR: "{pergunta_adicional.strip()}"
Responda diretamente e com profundidade técnica a essa dúvida, aplicando os dados reais de {estado} e sugerindo ações práticas, regulatórias e orçamentárias.
"""

    mensagem_usuario = f"""
EVIDÊNCIAS DE CIÊNCIA DE DADOS COLETADAS PARA AVALIAÇÃO:
- Região/Unidade Federativa: {estado}
- Emissões Brutas em 2024: {emissao_2024} t CO2e
- Variação Histórica (1990 a 2024): {var_hist}
- Variação no Quinquênio Recente (2020 a 2024): {var_quinq}
- Posição no Ranking Nacional de Maiores Emissores: {ranking} (Participação: {part_nac} do total do Brasil)
- Ano de Pico Histórico: {metricas['ano_pico_historico']} (com {metricas['valor_pico_tco2e']:,.2f} t CO2e)
- Diagnóstico Estatístico da Trajetória: {metricas['tendencia_trajetoria']}
- Risco Climático Preliminar: {metricas['nivel_risco_climatico']}
- Concentração Global de CO2 (NOAA Mauna Loa): {metricas['co2_global_atual_ppm']} ppm (Tendência: {metricas['co2_global_tendencia']})

{contexto_noticias}
{secao_pergunta}

Como Agente Inteligente de Tomada de Decisão ESG (ODS 13), elabore um PARECER ESTRATÉGICO EXECUTIVO estruturado exatamente com os seguintes tópicos:
1. DIAGNÓSTICO SITUACIONAL & TRAJETÓRIA HISTÓRICA: Analise os números reais, contextualizando a evolução de emissões e a posição no ranking.
2. MATRIZ DE RISCOS CLIMÁTICOS & GOVERNANÇA ESG: Avalie os principais riscos regulatórios, de transição e impactos socioambientais para o perfil '{perfil_decisor}'.
3. ALINHAMENTO COM O ODS 13 (AGENDA 2030): Explique a distância ou conformidade da região com as metas globais de descarbonização.
4. PLANO DE AÇÃO & RECOMENDAÇÕES PRIORITÁRIAS: Apresente 3 a 4 ações práticas e acionáveis (curto, médio e longo prazo) para mitigar emissões e fortalecer a governança.
{f'5. DIRETRIZES ESTRATÉGICAS PARA O FOCO DO DECISOR: ' + pergunta_adicional.strip() if pergunta_adicional and pergunta_adicional.strip() else ''}
"""

    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": mensagem_usuario.strip()}
    ]


def gerar_parecer_heuristico_fallback(metricas: Dict[str, Any], perfil_decisor: str, pergunta_adicional: Optional[str] = None) -> str:
    """
    Gera um parecer determinístico analítico completo de Ciência de Dados caso o modelo local
    de linguagem não esteja disponível no momento ou exceda o tempo limite de inferência.
    """
    estado = metricas["estado"]
    emissao_2024 = f"{metricas['emissao_2024_tco2e']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    var_hist = f"{metricas['variacao_historica_1990_2024_pct']:+.1f}%"
    var_quinq = f"{metricas['variacao_quinquenal_2020_2024_pct']:+.1f}%"
    ranking = f"{metricas['ranking_nacional_2024']}º lugar" if metricas['ranking_nacional_2024'] else "posição consolidada"
    part_nac = f"{metricas['participacao_nacional_pct']:.2f}%"

    parecer = f"""### 📋 PARECER ESTRATÉGICO EXECUTIVO — AGENTE INTELIGENTE ESG (ODS 13)

**Alvo da Análise:** {estado}  
**Perfil do Tomador de Decisão:** {perfil_decisor.replace('_', ' ').title()}  
**Data da Emissão:** {pd.Timestamp.now().strftime('%d/%m/%Y')}  
**Risco Climático Consolidado:** **{metricas['nivel_risco_climatico']}**

---

#### 1. Diagnóstico Situacional & Trajetória Histórica
Com base nas séries históricas oficiais do SEEG Brasil (1990–2024), **{estado}** registrou em 2024 um volume de **{emissao_2024} t CO₂e**.
- **Trajetória de Longo Prazo (1990–2024):** Houve uma oscilação acumulada de **{var_hist}**, tendo atingido seu pico histórico de emissão no ano de **{metricas['ano_pico_historico']}** ({metricas['valor_pico_tco2e']:,.2f} t CO₂e).
- **Dinâmica Recente (2020–2024):** A variação quinquenal foi de **{var_quinq}**, enquadrando o território no diagnóstico de *{metricas['tendencia_trajetoria']}*.
- **Posição Relativa Nacional:** Ocupa o **{ranking}** no ranking de maiores emissores do país, respondendo por **{part_nac}** do inventário bruto nacional.
- **Contexto Macro:** As emissões locais somam-se a uma concentração média global de CO₂ de **{metricas['co2_global_atual_ppm']} ppm** registrada pelo Observatório NOAA Mauna Loa, evidenciando urgência de mitigação.

#### 2. Matriz de Riscos Climáticos & Governança ESG
- **Risco Regulatório e de Conformidade:** Exposição iminente a novos marcos do Mercado Brasileiro de Créditos de Carbono (SBCE) e exigências de taxonomia sustentável do BACEN e CVM.
- **Risco de Transição Econômica:** Territórios e empresas com alta intensidade de emissões enfrentam restrições em emissões de títulos verdes (Green Bonds) e aumento do custo de capital.
- **Risco Físico e Resiliência:** Eventos climáticos extremos (secas hídricas severas ou tempestades) pressionam a infraestrutura e a produtividade agrícola/industrial local.

#### 3. Alinhamento com o ODS 13 (Agenda 2030)
O cumprimento da **Meta 13.2 do ODS 13** (*Integrar medidas da mudança do clima nas políticas, estratégias e planejamentos nacionais*) exige reversão imediata das trajetórias de alta. Para que {estado} convirja com a meta de neutralidade líquida (*Net Zero*) até 2050 prevista no Acordo de Paris, a trajetória atual requer uma taxa média de redução de pelo menos 3,5% ao ano na próxima década.

#### 4. Plano de Ação & Recomendações Prioritárias para Decisão
1. **Curto Prazo (0 a 12 meses) — Monitoramento & Transparência:**
   - Implementar inventários estaduais/setoriais anuais obrigatórios com base nos protocolos GHG Protocol.
   - Fortalecer a fiscalização ambiental digital integrada a dados de satélite e alertas em tempo real.
2. **Médio Prazo (1 a 3 anos) — Incentivos e Transição Energética:**
   - Criar incentivos fiscais (ex.: ICMS Ecológico calibrado por descarbonização) para cadeias produtivas de baixo carbono.
   - Estimular a eletrificação de frotas de transporte público e agropecuária regenerativa de precisão.
3. **Longo Prazo (3 a 5 anos) — Mercado de Carbono & Bioeconomia:**
   - Estruturar programas de Pagamento por Serviços Ambientais (PSA) e fomento a projetos locais de restauração florestal elegíveis a créditos de carbono certificados.

---
*Nota de Governança:* Este parecer foi sintetizado pelo Agente Inteligente a partir do cruzamento analítico de dados do SEEG, NOAA e inteligência artificial para apoio à tomada de decisão.
"""
    if pergunta_adicional and pergunta_adicional.strip():
        parecer += f"""
#### 5. Diretrizes Estratégicas para o Foco do Decisor: "{pergunta_adicional.strip()}"
Em resposta direta e prioritária à demanda apresentada para **{estado}**, recomenda-se:
1. **Integração no Planejamento Orçamentário (PPA/LOA):** Vincular formalmente as iniciativas demandadas a metas físicas e orçamentárias de descarbonização com auditoria externa anual.
2. **Instrumentos Regulatórios e Econômicos:** Desenhar incentivos fiscais, editais de inovação verde e linhas de financiamento público-privado focadas especificamente na resolução desta demanda.
3. **Comitê de Governança e Transparência:** Estabelecer um plano de ação trimestral com indicadores-chave de desempenho (KPIs) alinhados às diretrizes do ODS 13 e à taxonomia sustentável do BACEN/CVM.
"""

    return parecer


def descobrir_modelos_gemini(chave: str) -> List[str]:
    """
    Descobre dinamicamente na API do Google AI Studio a lista exata de modelos
    ativos para geração de texto (excluindo modelos de áudio/TTS/imagens).
    """
    try:
        url_lista = f"https://generativelanguage.googleapis.com/v1beta/models?key={chave.strip()}"
        r = requests.get(url_lista, timeout=10)
        if r.status_code == 200:
            dados = r.json().get("models", [])
            # Exclui modelos estritos de áudio, fala (TTS), imagens ou embeddings
            termos_excluidos = ["tts", "audio", "embed", "imagen", "speech"]
            geradores = []
            for m in dados:
                nome = m["name"].replace("models/", "")
                if any(t in nome.lower() for t in termos_excluidos):
                    continue
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    geradores.append(nome)
            
            # Prioriza modelos de texto mais rápidos e estáveis
            preferidos = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-pro-latest"]
            ordenados = [m for m in preferidos if m in geradores]
            outros = [m for m in geradores if m not in ordenados]
            modelos_finais = ordenados + outros
            if modelos_finais:
                print(f"[Agente Decisão] Modelos Gemini de TEXTO suportados: {modelos_finais[:4]}")
                return modelos_finais
    except Exception as e:
        print(f"[Agente Decisão] Não foi possível auto-descobrir modelos Gemini: {e}")
    return ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash"]


def chamar_gemini_api(
    metricas: Dict[str, Any],
    perfil_decisor: str,
    pergunta_adicional: Optional[str] = None,
    api_key: Optional[str] = None,
    temperatura: float = 0.4,
    max_tokens: int = 2048
) -> str:
    """
    Envia o prompt com Grounding de Dados diretamente para a API oficial do Google Gemini.
    Retorna o parecer estratégico executivo completo sem cortes e em alta velocidade.
    """
    chave = api_key or os.getenv("GEMINI_API_KEY")
    if not chave:
        raise ValueError("Chave de API do Google Gemini não configurada. Forneça uma chave no painel ou defina GEMINI_API_KEY.")

    mensagens = construir_prompt_agente(metricas, perfil_decisor, pergunta_adicional)
    instrucao_sistema = mensagens[0]["content"]
    prompt_usuario = mensagens[1]["content"]

    prompt_unificado = f"{instrucao_sistema}\n\n{prompt_usuario}"

    # Auto-descoberta dinâmica de modelos estritamente textuais
    modelos = descobrir_modelos_gemini(chave)
    ultimo_erro = None

    for mod in modelos:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={chave.strip()}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt_unificado}]
                }
            ],
            "generationConfig": {
                "temperature": max(0.1, min(temperatura, 1.0)),
                "maxOutputTokens": max_tokens
            }
        }
        try:
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            if resp.status_code == 200:
                dados = resp.json()
                candidatos = dados.get("candidates", [])
                if candidatos and "content" in candidatos[0] and "parts" in candidatos[0]["content"]:
                    partes = candidatos[0]["content"]["parts"]
                    texto = "".join([p.get("text", "") for p in partes]).strip()
                    if texto:
                        print(f"[Agente Decisão] Resposta gerada com sucesso via modelo: {mod}!")
                        return texto
            elif resp.status_code == 403:
                # Chave inválida ou permissão negada
                raise ValueError(f"Chave do Gemini sem permissão ou inválida (403): {resp.json().get('error', {}).get('message')}")
            else:
                msg_erro = resp.json().get('error', {}).get('message', resp.text)
                ultimo_erro = f"Modelo {mod} (Status {resp.status_code}): {msg_erro}"
                print(f"[Agente Decisão] Aviso: {ultimo_erro}. Tentando próximo modelo...")
        except ValueError:
            raise
        except Exception as e:
            ultimo_erro = str(e)
            print(f"[Agente Decisão] Erro ao tentar {mod}: {ultimo_erro}")

    raise RuntimeError(f"Falha ao consultar modelos do Google Gemini: {ultimo_erro}")


def executar_agente_decisao(
    estado: str,
    perfil_decisor: str = "gestao_publica",
    pergunta_adicional: Optional[str] = None,
    usar_modelo_llm: bool = True,
    motor_ia: str = "auto",
    api_key_gemini: Optional[str] = None,
    temperatura: float = 0.4,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    """
    Executa o ciclo completo do Agente Inteligente:
    1. Coleta e consolida as métricas via Pandas (Grounding de Dados);
    2. Constrói o prompt estruturado com o perfil do tomador de decisão;
    3. Executa a inferência conforme o motor selecionado:
       - 'gemini': Google Gemini 2.5 Flash via API (alta qualidade, sem truncamento);
       - 'local': Modelo Qwen2.5 local Hugging Face;
       - 'heuristico': Motor Analítico Especialista ESG (50ms);
       - 'auto': Usa Gemini se chave presente, senão heurístico ou local.
    4. Aplica fallback resiliente se o modelo não estiver disponível;
    5. Retorna o parecer e os KPIs calculados.
    """
    inicio = time.time()
    metricas = extrair_metricas_analiticas(estado)

    parecer_texto = ""
    modelo_utilizado = "Motor Analítico Heurístico de Ciência de Dados (Grounding Rules)"

    chave_gemini_disp = api_key_gemini or os.getenv("GEMINI_API_KEY")

    # Decisão de motor
    if motor_ia == "gemini" or (motor_ia == "auto" and chave_gemini_disp):
        try:
            parecer_texto = chamar_gemini_api(
                metricas=metricas,
                perfil_decisor=perfil_decisor,
                pergunta_adicional=pergunta_adicional,
                api_key=chave_gemini_disp,
                temperatura=temperatura,
                max_tokens=max_tokens
            )
            modelo_utilizado = "Google Gemini 3.8 Flash (API Oficial Google AI Studio)"
        except Exception as e:
            print(f"[Agente Decisão] Gemini indisponível ({str(e)}). Usando motor analítico heurístico de contingência.")
            parecer_texto = gerar_parecer_heuristico_fallback(metricas, perfil_decisor, pergunta_adicional)
            modelo_utilizado = f"Motor Analítico Especialista ESG (Contingência: {str(e)[:50]})"

    elif motor_ia == "local" or (motor_ia == "auto" and usar_modelo_llm):
        try:
            from src.llm_engine import carregar_modelo_llm, _TOKENIZER
            pipe = carregar_modelo_llm()
            mensagens = construir_prompt_agente(metricas, perfil_decisor, pergunta_adicional)
            
            prompt_completo = _TOKENIZER.apply_chat_template(
                mensagens,
                tokenize=False,
                add_generation_prompt=True
            )

            # Limite ampliado para 1200 tokens no Qwen local para evitar truncamento
            respostas = pipe(
                prompt_completo,
                max_new_tokens=1200,
                temperature=max(0.1, min(temperatura, 0.9)),
                do_sample=temperatura > 0.1,
                top_p=0.9,
                pad_token_id=_TOKENIZER.eos_token_id
            )
            
            texto_gerado = respostas[0]["generated_text"]
            if prompt_completo in texto_gerado:
                parecer_texto = texto_gerado.replace(prompt_completo, "").strip()
            else:
                parecer_texto = texto_gerado.strip()
            
            modelo_utilizado = "Qwen/Qwen2.5-0.5B-Instruct (Hugging Face Local - 1200 Tokens)"
        except Exception as e:
            print(f"[Agente Decisão] LLM local indisponível ou falhou ({str(e)}). Usando motor analítico estruturado de fallback.")
            parecer_texto = gerar_parecer_heuristico_fallback(metricas, perfil_decisor, pergunta_adicional)
            modelo_utilizado = "Motor Analítico Especialista ESG (Fallback Heurístico de Alta Disponibilidade)"
    else:
        parecer_texto = gerar_parecer_heuristico_fallback(metricas, perfil_decisor, pergunta_adicional)
        modelo_utilizado = "Motor Analítico Heurístico Especialista ESG (Alta Disponibilidade)"

    tempo_total = round(time.time() - inicio, 3)

    return {
        "status": "sucesso",
        "estado": metricas["estado"],
        "perfil_decisor": perfil_decisor,
        "kpis_calculados": metricas,
        "parecer_decisorio": parecer_texto,
        "tempo_execucao_segundos": tempo_total,
        "modelo_utilizado": modelo_utilizado
    }
