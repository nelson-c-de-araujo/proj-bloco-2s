# TDSP - Deployment

Esta pasta descreve como a solução é executada e implantada. Ela cobre duas partes: a aplicação web em Streamlit e a API em FastAPI.

## 1. Aplicação Streamlit

- **Arquivo principal:** [`code/app.py`](../../code/app.py)
- **Páginas:** Visão Geral, Indicadores Globais de CO₂, Panorama de Notícias & NLP, SEEG - Emissões Brasil e Gestão de Arquivos & Dados.
- **Execução:** `streamlit run code/app.py` a partir da raiz do projeto.
- **Atualização de dados:** os botões "Atualizar Notícias" e "Sincronizar Plataforma SEEG" executam os scripts de `src/` e limpam o cache.

## 2. API FastAPI

- **Arquivo principal:** [`src/api.py`](../../src/api.py)
- **Execução:** `uvicorn src.api:app --reload` a partir da raiz do projeto.
- **Documentação interativa:** `http://127.0.0.1:8000/docs`

| Método | Rota | Função |
|--------|------|--------|
| GET | `/` | Verifica se a API está no ar. |
| GET | `/noticias` | Consulta notícias, com filtro opcional por `termo` e limite de resultados (`limite`). |
| POST | `/noticias` | Cadastra uma notícia nova nas bases bruta e limpa. Retorna `409` se o título já existir. |
| GET | `/emissoes` | Consulta as emissões de 1990 a 2024, com filtro opcional por `estado`. |

**Exemplo de envio de notícia (POST /noticias):**

```json
{
  "fonte": "Fonte de teste",
  "titulo": "Título da notícia",
  "link": "https://exemplo.com/noticia",
  "resumo": "Resumo opcional.",
  "categoria": "ODS 13 - Ação Climática"
}
```

## 3. Dependências

Todas as bibliotecas estão em [`requirements.txt`](../../requirements.txt). Para o ambiente local, crie um ambiente virtual e instale com `pip install -r requirements.txt`.

## 4. Pendências de implantação

- A aplicação e a API rodam apenas localmente. Não há ainda um endereço público.
- A API não tem autenticação. Antes de publicar, o `POST /noticias` deve exigir uma chave.
- O scraping do SEEG usa Selenium e Google Chrome, o que exige o navegador instalado no servidor.
