# TDSP - Preparação para Uso de LLMs (ODS 13)

Este documento mapeia quais dados do projeto podem alimentar tarefas baseadas em LLM na próxima etapa, o que já está pronto e o que ainda precisa ser feito antes de integrar os modelos.

---

## 1. Dados disponíveis hoje

| Base | Arquivo | Conteúdo | Volume atual |
|------|---------|----------|--------------|
| Notícias (metadados) | `data/processed/noticias_ods13_limpo.csv` | Fonte, título, resumo, link, categoria e título limpo | 10 registros |
| Texto compilado | `data/raw/conteudo_ods13.txt` | Título e resumo de cada notícia, em texto corrido | cerca de 1.000 caracteres |
| Nuvem de palavras | `data/processed/texto_nuvem_palavras.txt` | Texto de títulos sem stopwords, pontuação e números | cerca de 490 caracteres |
| Emissões por estado (SEEG) | `data/processed/seeg_brasil_estados_limpo.csv` | 27 unidades federativas, a linha "Não Alocado" (emissões sem estado definido) e a linha "Total", com valores anuais de 1990 a 2024 | 29 linhas × 36 colunas |

**Pontos de atenção para LLM:**

- **As notícias são poucas.** A base bruta tem 10 matérias, sendo 5 da Agência Brasil e 5 da ONU News.
- **O resumo quase não existe.** 7 das 10 notícias usam o texto padrão "Notícia sobre Ação Climática e ODS 13.", porque o scraping não conseguiu ler o parágrafo da matéria. Na prática, o texto disponível para um LLM é quase só o título.
- **Os dados do SEEG são numéricos.** Eles servem para geração de texto e Q&A, mas não têm texto para classificar.

---

## 2. Tarefas candidatas

### 2.1. Análise de texto gerado (resumo automático)

- **Objetivo:** gerar um resumo curto de cada notícia ou do conjunto de matérias de um tema.
- **Dados:** `conteudo_ods13.txt` e, no futuro, o corpo completo das matérias.
- **Situação atual:** possível de testar, mas com baixo valor. Com resumos placeholder, o modelo resumiria apenas os títulos.
- **Antes de integrar:** alterar `src/scrape_news.py` para abrir cada link e extrair o primeiro parágrafo ou o corpo do artigo.

### 2.2. Classificação de sentimentos

- **Objetivo:** classificar cada notícia como positiva, negativa ou neutra em relação à ação climática.
- **Dados:** título e resumo de `noticias_ods13_limpo.csv`.
- **Situação atual:** inviável com 10 registros. Não há amostra suficiente para avaliar um modelo.
- **Antes de integrar:**
  - ampliar a coleta de notícias ao longo do tempo;
  - rotular manualmente uma amostra (sugestão: pelo menos 100 notícias) para servir de referência;
  - definir o que significa "neutro" no contexto do projeto.

### 2.3. Perguntas e respostas (Q&A)

- **Objetivo:** responder perguntas como "Quais estados mais aumentaram suas emissões entre 1990 e 2024?" com base nos dados do projeto.
- **Dados:** SEEG (estados e total), notícias e os documentos do próprio projeto (charter e relatório de dados).
- **Situação atual:** o SEEG já está limpo e pode ser consultado pela API (`GET /emissoes`). As notícias são consultáveis em `GET /noticias`.
- **Antes de integrar:** transformar os dados em trechos de texto (por exemplo, um parágrafo por estado) e definir uma forma de recuperar os trechos relevantes antes de enviar a pergunta ao LLM. Essa técnica é chamada de RAG (*Retrieval-Augmented Generation*).

### 2.4. Geração de texto (relatórios e insights)

- **Objetivo:** produzir um texto descritivo, por exemplo "Panorama de emissões do Rio de Janeiro", a partir dos números.
- **Dados:** `seeg_brasil_estados_limpo.csv`.
- **Situação atual:** é a tarefa mais viável hoje, porque os dados já são numéricos e limpos.
- **Cuidado:** o LLM deve receber apenas números já calculados pelo código (totais, variações, rankings). Assim, ele não precisa fazer contas e reduz o risco de erros no texto.

---

## 3. Princípios para a próxima etapa

1. **Os números vêm do código, não do modelo.** Cálculos como variação percentual e ranking são feitos em pandas, e o LLM apenas redige o texto.
2. **Toda resposta deve citar a fonte.** Cada afirmação sobre notícias deve trazer o veículo e o link.
3. **Só armazenar o necessário das notícias.** A base guarda título, resumo, link e fonte, sem copiar o texto integral das matérias, para respeitar direitos autorais.
4. **Validar a saída do modelo.** Antes de exibir o texto, conferir se os valores citados batem com os dados.
5. **Começar pequeno.** Testar primeiro a geração de texto sobre o SEEG, que já tem dados completos, e só depois avançar para sentimento, que depende de mais dados.

---

## 4. Checklist antes da próxima etapa

- [ ] Ampliar a coleta de notícias e registrar a data de cada coleta.
- [ ] Extrair o corpo ou o primeiro parágrafo das matérias, em vez do resumo padrão.
- [ ] Rotular uma amostra de notícias para avaliação de sentimento.
- [ ] Gerar uma versão textual dos dados do SEEG (um trecho por estado).
- [ ] Definir quais chaves de API e custos serão usados, e onde elas ficarão (variáveis de ambiente, nunca no código).
