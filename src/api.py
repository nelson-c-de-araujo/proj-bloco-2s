import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Garantir que o diretório raiz do projeto possa ser importado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.process_data import limpar_texto, processar_dados, padronizar_data, ordenar_noticias_por_data
from src.scrape_news import extrair_noticias_ods13
from src.scrape_seeg_brasil import extrair_seeg_brasil_estados_selenium
from src.llm_engine import executar_processamento_texto, MODEL_ID_PADRAO

"""
API do TP3 / Etapa 4 - ODS 13 (Ação Contra a Mudança Global do Clima)
Permite consultar (GET) e enviar/sincronizar (POST) dados de notícias climáticas,
emissões do SEEG Brasil por estado e série histórica de CO2 da NOAA.

Como executar, a partir da raiz do projeto:
    uvicorn src.api:app --reload --port 8000

Documentação interativa (Swagger UI):
    http://127.0.0.1:8000/docs
"""

# Caminhos dos arquivos, sempre relativos à raiz do projeto
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAMINHO_NOTICIAS_RAW = os.path.join(RAIZ, "data", "raw", "noticias_ods13.csv")
CAMINHO_NOTICIAS_LIMPO = os.path.join(RAIZ, "data", "processed", "noticias_ods13_limpo.csv")
CAMINHO_SEEG_LIMPO = os.path.join(RAIZ, "data", "processed", "seeg_brasil_estados_limpo.csv")
CAMINHO_SEEG_RAW = os.path.join(RAIZ, "data", "raw", "seeg_brasil_estados.csv")
CAMINHO_CO2_LIMPO = os.path.join(RAIZ, "data", "processed", "co2_mensal_noaa_limpo.csv")
CAMINHO_CO2_RAW = os.path.join(RAIZ, "data", "raw", "co2_mensal_noaa.csv")

app = FastAPI(
    title="API Painel Climático - ODS 13",
    description="API RESTful para consulta e ingestão de indicadores climáticos, notícias socioambientais e emissões SEEG Brasil.",
    version="2.0.0"
)

# Configuração de CORS para permitir consumo pelo Streamlit e clientes externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic para validação das requisições
class NoticiaNova(BaseModel):
    data: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%d/%m/%Y"),
        description="Data de publicação da matéria (DD/MM/AAAA)"
    )
    fonte: str = Field(..., description="Nome do veículo de comunicação ou instituição")
    titulo: str = Field(..., description="Título da matéria jornalística")
    link: str = Field(..., description="URL para acesso à notícia completa")
    resumo: str = Field(
        default="Notícia sobre Ação Climática e ODS 13.",
        description="Resumo ou lead da publicação"
    )
    categoria: str = Field(
        default="ODS 13 - Ação Climática",
        description="Categoria temática da publicação"
    )


class RegistroEmissaoEstado(BaseModel):
    Estado: str = Field(..., description="Nome da Unidade Federativa ou região")
    valores_anuais: Dict[str, float] = Field(
        default_factory=dict,
        description="Dicionário com os anos e respectivos volumes de emissão em t CO2e"
    )


# Modelos de Requisição e Resposta para Processamento com LLM Local
class RequisicaoProcessamentoTexto(BaseModel):
    texto: str = Field(
        ...,
        min_length=15,
        description="Texto jornalístico, técnico ou pergunta sobre clima a ser processado",
        example="A concentração de dióxido de carbono na atmosfera atingiu 426 ppm em 2024, acelerando as secas no Semiárido brasileiro."
    )
    tipo_analise: str = Field(
        default="resumo",
        description="Tipo de processamento desejado: 'resumo', 'sentimento' ou 'insights'",
        example="resumo"
    )
    max_novos_tokens: Optional[int] = Field(
        default=150,
        ge=20,
        le=512,
        description="Quantidade máxima de novos tokens a serem gerados"
    )
    temperatura: Optional[float] = Field(
        default=0.7,
        ge=0.1,
        le=1.0,
        description="Temperatura de amostragem da geração (criatividade/aleatoriedade)"
    )


class RespostaProcessamentoTexto(BaseModel):
    status: str = Field(default="sucesso", description="Estado da execução do processamento")
    tipo_analise: str = Field(..., description="Tipo de análise executada ('resumo', 'sentimento', 'insights')")
    modelo_utilizado: str = Field(..., description="Identificador do modelo Hugging Face executado localmente")
    texto_original: str = Field(..., description="Texto de entrada fornecido na requisição")
    resultado: str = Field(..., description="Texto gerado ou classificação realizada pelo modelo de linguagem")
    tempo_execucao_segundos: float = Field(..., description="Tempo de inferência gasto em segundos")
    detalhes: Optional[Dict[str, Any]] = Field(default=None, description="Metadados adicionais de geração de texto")


# Converte NaN em None para o JSON não quebrar na serialização
def df_para_lista(df: pd.DataFrame) -> List[Dict[str, Any]]:
    df_limpo = df.where(pd.notna(df), None)
    return df_limpo.to_dict(orient="records")


@app.get("/", tags=["Status"], summary="Verifica se a API está online")
def raiz():
    """Retorna o status da API e confirmação de prontidão para atendimento de requisições."""
    return {
        "status": "online",
        "versao": "2.0.0",
        "mensagem": "API do Painel Climático ODS 13 ativa e operante."
    }


# ==========================================
# ROTAS DE NOTÍCIAS
# ==========================================

@app.get("/noticias", tags=["Notícias"], summary="Consulta notícias climáticas e temas em alta")
def consultar_noticias(termo: Optional[str] = None, limite: int = Query(50, ge=1, le=200)):
    """
    Retorna a lista de publicações jornalísticas e institucionais cadastradas,
    ordenadas cronologicamente da mais recente para a mais antiga.
    """
    caminho = CAMINHO_NOTICIAS_LIMPO if os.path.exists(CAMINHO_NOTICIAS_LIMPO) else CAMINHO_NOTICIAS_RAW
    if not os.path.exists(caminho):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma notícia disponível. Execute a coleta primeiro."
        )

    df = pd.read_csv(caminho)
    df = ordenar_noticias_por_data(df)

    if termo:
        busca = termo.lower()
        mascara = (
            df["titulo"].str.lower().str.contains(busca, na=False)
            | df["fonte"].str.lower().str.contains(busca, na=False)
            | df["resumo"].str.lower().str.contains(busca, na=False)
        )
        if "data" in df.columns:
            mascara = mascara | df["data"].astype(str).str.lower().str.contains(busca, na=False)
        df = df[mascara]

    df = df.head(limite)
    return {"total": len(df), "noticias": df_para_lista(df)}


@app.post("/noticias", tags=["Notícias"], summary="Cadastra uma nova notícia manualmente", status_code=status.HTTP_201_CREATED)
def enviar_noticia(noticia: NoticiaNova):
    """
    Recebe um payload JSON com os dados de uma matéria, padroniza a data (DD/MM/AAAA)
    e a posiciona na ordem cronológica correta (mais recentes primeiro).
    """
    if os.path.exists(CAMINHO_NOTICIAS_RAW):
        df_raw = pd.read_csv(CAMINHO_NOTICIAS_RAW)
    else:
        df_raw = pd.DataFrame(columns=["data", "fonte", "titulo", "resumo", "link", "categoria"])

    # Evita duplicações por título
    if not df_raw.empty and "titulo" in df_raw.columns and noticia.titulo.strip() in df_raw["titulo"].values:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta notícia já existe na base de dados."
        )

    nova_linha = noticia.model_dump()
    nova_linha["data"] = padronizar_data(nova_linha.get("data", ""))
    
    # Adiciona e ordena imediatamente por data decrescente
    df_raw = pd.concat([df_raw, pd.DataFrame([nova_linha])], ignore_index=True)
    df_raw = ordenar_noticias_por_data(df_raw)
    os.makedirs(os.path.dirname(CAMINHO_NOTICIAS_RAW), exist_ok=True)
    df_raw.to_csv(CAMINHO_NOTICIAS_RAW, index=False, encoding="utf-8-sig")

    # Atualiza também a base processada
    nova_limpa = dict(nova_linha)
    nova_limpa["titulo_limpo"] = limpar_texto(noticia.titulo)
    if os.path.exists(CAMINHO_NOTICIAS_LIMPO):
        df_limpo = pd.read_csv(CAMINHO_NOTICIAS_LIMPO)
        df_limpo = pd.concat([df_limpo, pd.DataFrame([nova_limpa])], ignore_index=True)
    else:
        df_limpo = pd.DataFrame([nova_limpa])
    
    df_limpo = ordenar_noticias_por_data(df_limpo)
    df_limpo.to_csv(CAMINHO_NOTICIAS_LIMPO, index=False, encoding="utf-8-sig")

    return {
        "mensagem": "Notícia cadastrada e ordenada cronologicamente com sucesso.",
        "noticia": nova_linha
    }


@app.post("/noticias/sincronizar", tags=["Notícias"], summary="Dispara scraping ao vivo de notícias")
def sincronizar_noticias():
    """
    Aciona a rotina de web scraping nos portais monitorados e atualiza
    o pré-processamento de NLP e nuvem de palavras.
    """
    try:
        extrair_noticias_ods13()
        processar_dados()
        df = pd.read_csv(CAMINHO_NOTICIAS_LIMPO) if os.path.exists(CAMINHO_NOTICIAS_LIMPO) else pd.read_csv(CAMINHO_NOTICIAS_RAW)
        return {
            "status": "sucesso",
            "mensagem": "Sincronização de notícias concluída com êxito.",
            "total_noticias": len(df)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao sincronizar notícias: {str(e)}"
        )


# ==========================================
# ROTAS DE EMISSÕES SEEG BRASIL
# ==========================================

@app.get("/emissoes", tags=["Emissões SEEG"], summary="Consulta emissões brutas por estado (SEEG Brasil)")
def consultar_emissoes(estado: Optional[str] = None):
    """
    Retorna a série histórica de emissões anuais (1990–2024) desagregada
    por Estados e regiões brasileiras.
    """
    caminho = CAMINHO_SEEG_LIMPO if os.path.exists(CAMINHO_SEEG_LIMPO) else CAMINHO_SEEG_RAW
    if not os.path.exists(caminho):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum dado do SEEG disponível. Execute a extração primeiro."
        )

    df = pd.read_csv(caminho)

    if estado:
        df = df[df["Estado"].str.lower() == estado.lower()]
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estado ou registro '{estado}' não encontrado."
            )

    return {"total": len(df), "emissoes": df_para_lista(df)}


@app.post("/emissoes", tags=["Emissões SEEG"], summary="Atualiza ou cadastra registros de emissão estadual")
def cadastrar_emissao(registro: RegistroEmissaoEstado):
    """
    Permite enviar novas medições de emissão para uma Unidade Federativa.
    """
    caminho = CAMINHO_SEEG_LIMPO if os.path.exists(CAMINHO_SEEG_LIMPO) else CAMINHO_SEEG_RAW
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Base de dados do SEEG não localizada.")

    df = pd.read_csv(caminho)
    idx = df[df["Estado"].str.lower() == registro.Estado.lower()].index
    
    nova_linha = {"Estado": registro.Estado}
    nova_linha.update(registro.valores_anuais)

    if not idx.empty:
        for k, v in registro.valores_anuais.items():
            df.loc[idx[0], k] = v
    else:
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

    df.to_csv(CAMINHO_SEEG_LIMPO, index=False, encoding="utf-8-sig")
    return {"status": "sucesso", "mensagem": f"Dados de emissão de {registro.Estado} registrados com sucesso."}


@app.post("/emissoes/sincronizar", tags=["Emissões SEEG"], summary="Dispara extração do SEEG via Selenium")
def sincronizar_seeg():
    """
    Aciona a extração dinâmica em tempo real na Plataforma SEEG Brasil
    via Selenium em modo headless e recalcula a base limpa.
    """
    try:
        extrair_seeg_brasil_estados_selenium()
        processar_dados()
        df = pd.read_csv(CAMINHO_SEEG_LIMPO) if os.path.exists(CAMINHO_SEEG_LIMPO) else pd.read_csv(CAMINHO_SEEG_RAW)
        return {
            "status": "sucesso",
            "mensagem": "Extração SEEG Brasil concluída com êxito.",
            "total_estados": len(df)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na sincronização via Selenium da plataforma SEEG: {str(e)}"
        )


# ==========================================
# ROTAS DE CONCENTRAÇÃO GLOBAL DE CO2 (NOAA)
# ==========================================

@app.get("/co2", tags=["Indicadores Globais"], summary="Consulta série histórica real de CO2 atmosférico (NOAA)")
def consultar_co2(ano: Optional[int] = None, mes: Optional[str] = None):
    """
    Retorna medições oficiais de partes por milhão (ppm) de CO2 na atmosfera
    registradas pelo Observatório de Mauna Loa da NOAA.
    """
    caminho = CAMINHO_CO2_LIMPO if os.path.exists(CAMINHO_CO2_LIMPO) else CAMINHO_CO2_RAW
    if not os.path.exists(caminho):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série de dados de CO2 não encontrada."
        )

    df = pd.read_csv(caminho)

    if ano:
        df = df[df["Ano"] == ano]
    if mes:
        df = df[df["Mês"].str.lower() == mes.lower()]

    return {"total": len(df), "dados": df_para_lista(df)}


# ==========================================
# ROTAS DE INTELIGÊNCIA ARTIFICIAL (LLM LOCAL)
# ==========================================

@app.post(
    "/processar_texto",
    response_model=RespostaProcessamentoTexto,
    tags=["Inteligência Artificial (LLM Local)"],
    summary="Processa texto com modelo de linguagem natural (LLM) local",
    status_code=status.HTTP_200_OK
)
def processar_texto(requisicao: RequisicaoProcessamentoTexto):
    """
    Recebe um texto enviado pelo cliente e processa através do modelo local da Hugging Face
    (Qwen2.5-0.5B-Instruct), executando tarefas como:
    - Resumo executivo ('resumo')
    - Análise de tom e impacto climático ('sentimento')
    - Geração de recomendações e implicações socioambientais ('insights')
    
    Retorna uma resposta estruturada e validada via Pydantic com tratamento robusto de erros.
    """
    tipos_permitidos = ["resumo", "sentimento", "insights"]
    if requisicao.tipo_analise.lower() not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de análise '{requisicao.tipo_analise}' inválido. Escolha entre: {', '.join(tipos_permitidos)}."
        )

    # Validação de conteúdo não trivial
    texto_limpo = requisicao.texto.strip()
    if len(texto_limpo) < 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Texto de entrada muito curto. Forneça ao menos 15 caracteres com conteúdo significativo para análise."
        )

    try:
        resultado_dict = executar_processamento_texto(
            texto=texto_limpo,
            tipo_analise=requisicao.tipo_analise.lower(),
            max_novos_tokens=requisicao.max_novos_tokens or 150,
            temperatura=requisicao.temperatura or 0.7
        )

        return RespostaProcessamentoTexto(
            status="sucesso",
            tipo_analise=requisicao.tipo_analise.lower(),
            modelo_utilizado=resultado_dict["modelo"],
            texto_original=texto_limpo,
            resultado=resultado_dict["resultado"],
            tempo_execucao_segundos=resultado_dict["tempo_execucao_segundos"],
            detalhes={"tokens_gerados": resultado_dict.get("tokens_gerados")}
        )

    except RuntimeError as e:
        # Modelo não pôde ser carregado (ex: falta de dependências torch/transformers no host)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço de IA local temporariamente indisponível: {str(e)}"
        )
    except Exception as e:
        # Falha genérica durante a geração
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante a inferência do modelo local: {str(e)}"
        )


@app.get(
    "/llm/status",
    tags=["Inteligência Artificial (LLM Local)"],
    summary="Verifica o status de prontidão do modelo local"
)
def status_modelo_llm():
    """Informa o modelo configurado e a prontidão do engine de inferência local."""
    import src.llm_engine as engine
    return {
        "modelo_configurado": engine.MODEL_ID_PADRAO,
        "carregado_em_memoria": engine._PIPELINE is not None,
        "erro_previo": engine._ERRO_INICIALIZACAO,
        "ambiente": "100% Local (Hugging Face Transformers / PyTorch)"
    }

