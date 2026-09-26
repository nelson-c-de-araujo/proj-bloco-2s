# Monitor de Emissões (ODS 13) - Projeto de Bloco

Este repositório contém o projeto de monitoramento e análise de emissões de CO₂ para apoiar decisões alinhadas ao **ODS 13 (Ação Contra a Mudança Global do Clima)**.

## 📂 Estrutura do Repositório (Padrão TDSP)

A estrutura segue o padrão do **Team Data Science Process (TDSP)**:

- `data/`: Arquivos de dados brutos (`data/raw/`) e processados (`data/processed/`).
- `docs/`: Documentação estruturada pelas fases do ciclo de vida TDSP:
  - `BusinessUnderstanding/`: Compreensão do problema de negócio.
  - `DataUnderstanding/`: Exploração e entendimento das fontes de dados.
  - `DataPreparation/`: Transformação e limpeza de dados.
  - `Modeling/`: Experimentos, modelos e métricas.
  - `Deployment/`: Orientações para implantação da aplicação.
  - `Acceptance/`: Validação e feedback com stakeholders.
- `models/`: Artefatos e pickles de modelos treinados.
- `src/`: Módulos Python reutilizáveis e utilitários.
- `code/`: Aplicação principal ([`app.py`](code/app.py)).
- `artifacts/`: Artefatos principais do projeto ([`project_charter.md`](artifacts/project_charter.md) e [`data_summary_report.md`](artifacts/data_summary_report.md)).

## 🚀 Como Executar a Aplicação

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie a aplicação Streamlit:
   ```bash
   streamlit run code/app.py
   ```