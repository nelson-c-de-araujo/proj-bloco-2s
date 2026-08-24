# TP1 - Projeto de Bloco - Instituto Infnet - Aluno: Nelson C. de Araujo
## Projeto da Agenda 2030 - ODS 13: Ação Contra a Mudança Global do Clima

## 1. Definição do Problema de Negócio 

**Problema**: Muitas organizações não têm ferramentas prontas para acompanhar quantos gases emitem e impactam o planeta. Sem esses números, fica difícil planejar como reduzir as emissões.

**Objetivo**: Criar um protótipo simples que mostre esses números de forma clara e dê uma ideia de como eles podem mudar no futuro, com base nos parâmetros do ODS 13 – *Ação Contra a Mudança Global do Clima*.

**Metas para o sucesso**
- Um painel fácil de usar que mostre o total de emissões por período, comparativo, evolução e dados sazonais.
- Feedback positivo de pelo menos 80% dos usuários que testarem a ferramenta.

### **ODS utilizado no TP**: **ODS 13 – Ação Contra a Mudança Global do Clima** 

**Justificativa:** Esse assunto disponibiliza dados e insights públicos que possibilitam a análise completa e estudos para a mitigação das emissões de gases, dados esses que permitam que o estudo e o projeto caminhem de maneira sólida.

**Público‑Alvo**
- Empresas que precisam reportar emissões aos reguladores.
- Gestores de sustentabilidade e equipes de ESG.
- Órgãos públicos interessados em monitorar a emissão de carbono dos seus locais de atuação.
- Curiosos sobre dados climáticos.

## 2. Organização do Projeto (CRISP‑DM + TDSP)

- **(CRISP-DM + TDSP) Etapa: Business Understanding** - Aqui a gente compreende o problema de negócio a ser resolvido.
- **(CRISP-DM + TDSP) Etapa: Data Understanding** - Aqui a gente entende o dado disponível e se ele é de fato "usável".
- **(CRISP-DM + TDSP) Etapa: Data Preparation** - Aqui a gente gasta nossa energia pra preparar o dado (dá trabalho)
- **(CRISP-DM + TDSP) Etapa: Modeling** - Aqui nós começamos a preparar os modelos.
- **(CRISP-DM + TDSP) Etapa: Evaluation** - Aqui realizamos checks se as previsões funcionam o suficiente.
- **(CRISP-DM + TDSP) Etapa: Deployment** - Aqui realizamos o lançamento da ferramenta.
- **(TDSP) Etapa: Acceptance:** Aqui, dentro do TDSP, entendemos se a situação foi bem absorvida pelo cliente/stakeholder.



## 3. Estrutura de Diretórios Inicial

```
Projeto_Bloco_TP1/
|-- data/  # Dados brutos e processados
|-- code/  # Código-fonte da aplicação
|   |--app.py # Script principal
|-- artifacts/  # Documentos do projeto (charter, reports, etc.)
|   |-- Project_Charter.md # Possui o detalhamento do projeto e as respostas aos itens 1, 2 e 3.
|   |-- Data_Summary_Report.md # Contém os dados disponibilizados no app
|-- requirements.txt  # Dependências Python
|-- README.md # Visão geral do projeto
```

## 4. Artefatos Iniciais

- **Project Charter** (arquivo `artifacts/Project_Charter.md`): descreve escopo, stakeholders, cronograma e recursos.
- **Data Summary Report** (arquivo `artifacts/Data_Summary_Report.md`): Lista as fontes de dados previstas e o objetivo de uso de cada conjunto.

## 5. Aplicação Demo (Streamlit)

A aplicação conterá:  
- Título: "Monitor de Emissões – Projeto ODS 13"
- Descrição do problema e objetivos.
- Links úteis para bases de dados climáticas e referências de projetos de ESG.
- Tabela interativa exibindo amostras dos dados de emissões.  
  

---