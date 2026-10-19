# Relatório de Sumário de Dados - Projeto_Bloco_EtapaTP3
**Instituto Infnet | Aluno: Nelson C. de Araujo**

Este documento descreve as fontes de dados (estruturadas e não estruturadas), o fluxo de pré-processamento e os arquivos mantidos no projeto para o monitoramento do **ODS 13 (Ação Contra a Mudança Global do Clima)**.

---

## 1. Fontes de Dados de Emissões (Estruturados)

### 1.1. SEEG - Plataforma de Emissões por Estado (ativa)
- **Origem:** Plataforma SEEG (`plataforma.seeg.eco.br`), com a tabela de emissões agrupada por estado.
- **Coleta:** script `src/scrape_seeg_brasil.py`, que usa Selenium e Google Chrome em modo *headless* para renderizar a página dinâmica e ler a tabela de linhas e colunas.
- **Período:** 1990 a 2024, um valor por ano.
- **Unidade:** toneladas de CO₂ equivalente (t CO₂e), conforme o rótulo da própria aplicação.
- **Conteúdo:** 27 unidades federativas, a linha "Não Alocado" (emissões que não podem ser atribuídas a um estado) e a linha "Total".
- **Uso na aplicação:** painel "SEEG - Emissões Brasil", download da tabela e consulta pela rota `GET /emissoes`.

### 1.2. Série de CO₂ atmosférico (planejada, não integrada)
- **Origem prevista:** NOAA Global Monitoring Laboratory (GML).
- **Situação:** o indicador da página "Indicadores Globais de CO₂" usa valores de demonstração de 2024, fixos no código (`obter_dados_historicos_demo`). Nenhum dado da NOAA foi baixado. Isso será adicionado até o final do projeto.

### 1.3. Conjunto de Dados Próprios do Usuário (upload CSV)
- **Tipo:** arquivos CSV enviados pela interface (`st.file_uploader`).
- **Formato esperado:** colunas `Data de Registro` e `Nível de CO2 (ppm)`. Outros formatos são aceitos, mas o gráfico usa a primeira coluna numérica.
- **Uso na aplicação:** visualização em tabela e gráfico de linhas.

---

## 2. Fontes de Notícias & Conteúdo Climático (não estruturados)

### 2.1. Web Scraping via BeautifulSoup (`src/scrape_news.py`)
- **Fontes:** Agência Brasil (editoria de meio ambiente / mudanças climáticas) e ONU News (tópico de mudanças climáticas).
- **Dados extraídos:** título, resumo, link e nome do veículo. Um resumo é aceito apenas se houver um parágrafo (`<p>`) no elemento pai do link.
- **Situação atual:** a última coleta gerou 10 registros (5 por fonte). Em 7 deles, o resumo é o texto padrão "Notícia sobre Ação Climática e ODS 13.", porque o parágrafo não foi encontrado.
- **Resiliência:** se houver menos de 3 notícias válidas, o script acrescenta três registros institucionais (ONU Brasil, IPCC e NOAA) para que a aplicação continue funcionando. Esses registros são fixos e não são notícias coletadas da data da execução. Devem ser considerados ao analisar a base.

---

## 3. Pipeline e Arquivos (`data/`)

### 3.1. Dados brutos (`data/raw/`)
| Arquivo | Origem | Conteúdo |
|---------|--------|----------|
| `noticias_ods13.csv` | `scrape_news.py` e `POST /noticias` | Fonte, título, resumo, link, categoria |
| `conteudo_ods13.txt` | `scrape_news.py` | Título e resumo de cada notícia, em texto corrido |
| `seeg_brasil_estados.csv` | `scrape_seeg_brasil.py` | Tabela do SEEG, com os números no formato brasileiro (ex.: `22.680.790`) |

### 3.2. Dados processados (`data/processed/`)
| Arquivo | Origem | Transformação |
|---------|--------|---------------|
| `noticias_ods13_limpo.csv` | `process_data.py` e `POST /noticias` | Acrescenta a coluna `titulo_limpo`, sem pontuação, números e stopwords |
| `texto_nuvem_palavras.txt` | `process_data.py` | Texto de `conteudo_ods13.txt` sem stopwords em português, pontuação e números. Usado na nuvem de palavras |
| `seeg_brasil_estados_limpo.csv` | `process_data.py` | Converte os valores para número, removendo os pontos de milhar e trocando a vírgula decimal. Valores inválidos viram 0 |

**Observação sobre o SEEG limpo:** a conversão trata inválidos como 0. Isso evita erro na aplicação, mas um dado ausente na fonte passa a aparecer como emissão zero.

---

## 4. Qualidade dos Dados (estado atual)

| Verificação | Resultado |
|-------------|-----------|
| Notícias coletadas | 10 registros, sem valores nulos |
| Resumos padrão | 7 de 10 (70%) |
| Linhas do SEEG | 29 (27 unidades federativas, "Não Alocado" e "Total") |
| Colunas do SEEG | 36 (Estado + 35 anos, de 1990 a 2024) |
| Valores nulos no SEEG limpo | 0 |

**Riscos:**
- A base de notícias é pequena e não tem histórico de coletas.
- "Não Alocado" entra nas contagens de estados se não for filtrado.
- O CSV de upload não tem validação de colunas além da leitura.

---

## 5. Próximos Passos de Dados

1. Coletar notícias em execuções periódicas, guardando a data da coleta.
2. Extrair o corpo das matérias para substituir o resumo padrão.
3. Separar "Não Alocado" das unidades federativas em todas as análises.
4. Integrar a série da NOAA ou remover o indicador de demonstração.
