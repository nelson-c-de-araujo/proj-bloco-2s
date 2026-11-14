# TDSP - Modeling: Integração de LLM Local (Etapa 4)

Esta pasta documenta a modelagem em Processamento de Linguagem Natural (NLP) e a integração de **Modelos de Linguagem de Grande Porte (LLM)** executados 100% no ambiente local.

---

## 1. Modelo Selecionado no Catálogo Hugging Face

- **Identificador:** [`Qwen/Qwen2.5-0.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
- **Desenvolvedor:** Alibaba Cloud (Open-source)
- **Arquitetura:** Decoder-only autoregressivo com suporte nativo a ChatML e alinhamento por reforço
- **Parâmetros:** ~490 milhões (~980 MB em disco)
- **Consumo de Hardware:** ~1.2 GB a 1.5 GB de RAM em CPU (`torch.float32`), latência de 1 a 3 segundos por inferência
- **Suporte a Língua Portuguesa:** Multilíngue nativo, gerando respostas em PT-BR com coerência e correção gramatical

---

## 2. Tarefas de NLP Implementadas

1. **Resumo Automático (`tipo_analise: "resumo"`):**
   Gera um resumo executivo sintetizando os principais acontecimentos ou dados do texto em 2 a 3 frases.
2. **Análise de Tom e Sentimento Climático (`tipo_analise: "sentimento"`):**
   Classifica o texto sob o prisma do ODS 13 em `POSITIVO` (avanços, acordos, transição verde), `NEGATIVO` (riscos, secas, recordes de emissão) ou `NEUTRO` (técnico/institucional), acompanhado de justificativa sucinta.
3. **Geração de Insights Socioambientais (`tipo_analise: "insights"`):**
   Produz 2 a 3 recomendações e pontos analíticos orientados à tomada de decisão pública e corporativa.

---

## 3. Arquitetura de Inferência Local

- **Módulo:** [`src/llm_engine.py`](../../src/llm_engine.py)
- **Mecanismo:** Padrão *Singleton* com *Lazy Loading* (o modelo é instanciado em memória apenas quando a primeira inferência é solicitada, evitando onerar o tempo de subida do servidor FastAPI).
- **Sem Dependência de Nuvem:** Não são necessárias chaves de API pagas (como OpenAI ou Anthropic); o modelo roda na CPU/GPU local via biblioteca `transformers` da Hugging Face.

---

## 4. Response Models e Rota FastAPI

- **Rota:** `POST /processar_texto`
- **Request Model:** `RequisicaoProcessamentoTexto` (validação de `texto`, `tipo_analise`, `max_novos_tokens`, `temperatura`)
- **Response Model:** `RespostaProcessamentoTexto` (validação de `status`, `tipo_analise`, `modelo_utilizado`, `texto_original`, `resultado`, `tempo_execucao_segundos`, `detalhes`)
- **Tratamento de Exceções HTTP:**
  - `422`: Texto vazio ou inferior a 15 caracteres.
  - `400`: Tipo de tarefa inválido.
  - `503`: Modelo local não carregado / dependências `torch`/`transformers` ausentes.
  - `500`: Erro interno no pipeline de inferência.
