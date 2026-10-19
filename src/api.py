import os
import sys

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Garantir que o diretório raiz do projeto possa ser importado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.process_data import limpar_texto

"""
API do TP3 - ODS 13 (Ação Contra a Mudança Global do Clima)
Permite consultar (GET) e enviar (POST) dados de notícias climáticas e emissões do SEEG Brasil.

Como executar, a partir da raiz do projeto:
    uvicorn src.api:app --reload

Documentação interativa (Swagger):
    http://127.0.0.1:8000/docs
"""

# Caminhos dos arquivos, sempre relativos à raiz do projeto
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAMINHO_NOTICIAS_RAW = os.path.join(RAIZ, "data", "raw", "noticias_ods13.csv")
CAMINHO_NOTICIAS_LIMPO = os.path.join(RAIZ, "data", "processed", "noticias_ods13_limpo.csv")
CAMINHO_SEEG_LIMPO = os.path.join(RAIZ, "data", "processed", "seeg_brasil_estados_limpo.csv")
CAMINHO_SEEG_RAW = os.path.join(RAIZ, "data", "raw", "seeg_brasil_estados.csv")

app = FastAPI(
    title="API Painel Climático - ODS 13",
    description="Consulta e envio de dados de notícias climáticas e de emissões do SEEG Brasil por estado.",
    version="1.0.0"
)


# Modelo dos dados que a API aceita no POST de notícias
class NoticiaNova(BaseModel):
    fonte: str
    titulo: str
    link: str
    resumo: str = "Notícia sobre Ação Climática e ODS 13."
    categoria: str = "ODS 13 - Ação Climática"


# Converte NaN em None para o JSON não quebrar
def df_para_lista(df):
    df_limpo = df.where(pd.notna(df), None)
    return df_limpo.to_dict(orient="records")


@app.get("/", tags=["Status"], summary="Verifica se a API está no ar")
def raiz():
    # Rota simples para confirmar que a API está funcionando
    return {"status": "online", "mensagem": "API do Painel Climático ODS 13 em funcionamento."}


@app.get("/noticias", tags=["Notícias"], summary="Consulta notícias climáticas")
def consultar_noticias(termo: str = None, limite: int = 50):
    # Verifica se o arquivo limpo existe; se não, usa o bruto
    caminho = CAMINHO_NOTICIAS_LIMPO
    if not os.path.exists(caminho):
        caminho = CAMINHO_NOTICIAS_RAW
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Nenhuma notícia disponível. Execute o scraping primeiro.")

    df = pd.read_csv(caminho)

    # Filtro opcional por termo no título ou na fonte
    if termo:
        busca = termo.lower()
        mascara = (
            df["titulo"].str.lower().str.contains(busca, na=False)
            | df["fonte"].str.lower().str.contains(busca, na=False)
        )
        df = df[mascara]

    # Limita a quantidade de resultados devolvidos
    df = df.head(limite)

    return {"total": len(df), "noticias": df_para_lista(df)}


@app.post("/noticias", tags=["Notícias"], summary="Envia uma nova notícia", status_code=201)
def enviar_noticia(noticia: NoticiaNova):
    # Carrega a base bruta atual (ou cria uma vazia, se não existir)
    if os.path.exists(CAMINHO_NOTICIAS_RAW):
        df_raw = pd.read_csv(CAMINHO_NOTICIAS_RAW)
    else:
        df_raw = pd.DataFrame(columns=["fonte", "titulo", "resumo", "link", "categoria"])

    # Não aceita título repetido
    if noticia.titulo in df_raw["titulo"].values:
        raise HTTPException(status_code=409, detail="Esta notícia já existe na base.")

    # Adiciona a nova linha na base bruta
    nova_linha = noticia.model_dump()
    df_raw = pd.concat([df_raw, pd.DataFrame([nova_linha])], ignore_index=True)
    os.makedirs(os.path.dirname(CAMINHO_NOTICIAS_RAW), exist_ok=True)
    df_raw.to_csv(CAMINHO_NOTICIAS_RAW, index=False, encoding="utf-8-sig")

    # Atualiza também a base limpa, para a nova notícia aparecer no painel
    nova_limpa = dict(nova_linha)
    nova_limpa["titulo_limpo"] = limpar_texto(noticia.titulo)
    if os.path.exists(CAMINHO_NOTICIAS_LIMPO):
        df_limpo = pd.read_csv(CAMINHO_NOTICIAS_LIMPO)
        df_limpo = pd.concat([df_limpo, pd.DataFrame([nova_limpa])], ignore_index=True)
    else:
        df_limpo = pd.DataFrame([nova_limpa])
    df_limpo.to_csv(CAMINHO_NOTICIAS_LIMPO, index=False, encoding="utf-8-sig")

    return {"mensagem": "Notícia cadastrada com sucesso.", "noticia": nova_linha}


@app.get("/emissoes", tags=["Emissões SEEG"], summary="Consulta emissões por estado (SEEG Brasil)")
def consultar_emissoes(estado: str = None):
    # Verifica se o arquivo limpo existe; se não, usa o bruto
    caminho = CAMINHO_SEEG_LIMPO
    if not os.path.exists(caminho):
        caminho = CAMINHO_SEEG_RAW
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Nenhum dado do SEEG disponível. Execute a extração primeiro.")

    df = pd.read_csv(caminho)

    # Filtro opcional por nome do estado (ex.: "Rio de Janeiro")
    if estado:
        df = df[df["Estado"].str.lower() == estado.lower()]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Estado '{estado}' não encontrado.")

    return {"total": len(df), "emissoes": df_para_lista(df)}
