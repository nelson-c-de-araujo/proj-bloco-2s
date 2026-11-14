import pandas as pd
import os
import re
from datetime import datetime

"""
Script de Pré-processamento de Dados para o TP2 - ODS 13
Lê os dados brutos de data/raw/, realiza limpeza de texto e gera artefatos em data/processed/
"""

STOPWORDS_PT = set([
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "não", "uma", "os", "no", 
    "se", "na", "por", "mais", "as", "dos", "como", "mas", "ao", "ele", "das", "à", "seu", "sua", 
    "ou", "quando", "muito", "nos", "já", "eu", "também", "só", "pelo", "pela", "até", "isso", 
    "ela", "entre", "depois", "sem", "mesmo", "aos", "seus", "quem", "nas", "me", "esse", "eles", 
    "você", "essa", "num", "nem", "suas", "meu", "às", "minha", "numa", "pelos", "elas", "qual", 
    "nós", "lhe", "deles", "essas", "esses", "pelas", "este", "dele", "tu", "te", "vocês", "vos", 
    "lhes", "meus", "minhas", "teu", "tua", "teus", "tuas", "nosso", "nossa", "nossos", "nossas", 
    "dela", "delas", "esta", "estes", "estas", "aquele", "aquela", "aqueles", "aquela", "diz", 
    "sobre", "notícia", "ação", "climática", "ods", "13", "facebooktwitter", "br"
])

MESES_PT = {
    'janeiro': 1, 'fev': 2, 'fevereiro': 2, 'março': 3, 'marco': 3, 'mar': 3,
    'abril': 4, 'abr': 4, 'maio': 5, 'mai': 5, 'junho': 6, 'jun': 6,
    'julho': 7, 'jul': 7, 'agosto': 8, 'ago': 8, 'setembro': 9, 'set': 9,
    'outubro': 10, 'out': 10, 'novembro': 11, 'nov': 11, 'dezembro': 12, 'dez': 12
}


def padronizar_data(texto_data: str) -> str:
    """
    Padroniza qualquer variação textual de data para o formato brasileiro DD/MM/AAAA.
    Exemplos:
      - '11 Novembro 2026' -> '11/11/2026'
      - '9 Novembro 2026'  -> '09/11/2026'
      - '2026-11-09'       -> '09/11/2026'
      - '09/11/2026'       -> '09/11/2026'
    """
    if not texto_data or not isinstance(texto_data, str):
        return datetime.now().strftime("%d/%m/%Y")
    
    texto = texto_data.strip().lower()

    # 1. Padrão numérico: DD/MM/AAAA ou DD-MM-AAAA
    m_ddmmyyyy = re.search(r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b', texto)
    if m_ddmmyyyy:
        dia, mes, ano = m_ddmmyyyy.groups()
        if len(ano) == 2:
            ano = f"20{ano}"
        try:
            dt = datetime(int(ano), int(mes), int(dia))
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            pass

    # 2. Padrão ISO: AAAA-MM-DD
    m_iso = re.search(r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b', texto)
    if m_iso:
        ano, mes, dia = m_iso.groups()
        try:
            dt = datetime(int(ano), int(mes), int(dia))
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            pass

    # 3. Padrão por extenso: '11 Novembro 2026' ou '9 de Novembro de 2026'
    m_ext = re.search(r'\b(\d{1,2})\s*(?:de\s+)?([a-zçã]+)\s*(?:de\s+)?(\d{4})\b', texto)
    if m_ext:
        dia, nome_mes, ano = m_ext.groups()
        if nome_mes in MESES_PT:
            mes = MESES_PT[nome_mes]
            try:
                dt = datetime(int(ano), int(mes), int(dia))
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                pass

    return datetime.now().strftime("%d/%m/%Y")


def ordenar_noticias_por_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza todas as datas da coluna 'data' e ordena o DataFrame
    de forma decrescente (as notícias mais recentes aparecem primeiro).
    """
    if df.empty or 'data' not in df.columns:
        return df
    
    df_ord = df.copy()
    df_ord['data'] = df_ord['data'].apply(padronizar_data)
    
    # Coluna auxiliar datetime para ordenação estrita
    df_ord['_dt_temp'] = pd.to_datetime(df_ord['data'], format='%d/%m/%Y', errors='coerce')
    df_ord = df_ord.sort_values(by=['_dt_temp'], ascending=False).drop(columns=['_dt_temp'])
    return df_ord


def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    # Remover caracteres especiais e números
    texto_limpo = re.sub(r'[^\w\s]', ' ', texto.lower())
    texto_limpo = re.sub(r'\d+', ' ', texto_limpo)
    
    palavras = texto_limpo.split()
    palavras_filtradas = [p for p in palavras if p not in STOPWORDS_PT and len(p) > 2]
    return " ".join(palavras_filtradas)

def processar_dados():
    os.makedirs("data/processed", exist_ok=True)
    
    # 1. Processar Notícias CSV
    csv_raw = "data/raw/noticias_ods13.csv"
    if os.path.exists(csv_raw):
        df = pd.read_csv(csv_raw)
        if 'data' not in df.columns:
            df['data'] = datetime.now().strftime("%d/%m/%Y")
        
        # Padroniza datas e ordena do mais recente para o mais antigo
        df = ordenar_noticias_por_data(df)
        df['titulo_limpo'] = df['titulo'].apply(limpar_texto)
        
        # Atualiza a base bruta já padronizada e ordenada
        df.drop(columns=['titulo_limpo']).to_csv(csv_raw, index=False, encoding='utf-8-sig')

        # Salvar dataset processado
        csv_processed = "data/processed/noticias_ods13_limpo.csv"
        df.to_csv(csv_processed, index=False, encoding='utf-8-sig')
        print(f"Dataset processado salvo em: {csv_processed}")

    # 2. Processar Texto TXT para Nuvem de Palavras
    txt_raw = "data/raw/conteudo_ods13.txt"
    if os.path.exists(txt_raw):
        with open(txt_raw, "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        texto_trata = limpar_texto(conteudo)
        txt_processed = "data/processed/texto_nuvem_palavras.txt"
        with open(txt_processed, "w", encoding="utf-8") as f:
            f.write(texto_trata)
        print(f"Texto tratado para Nuvem de Palavras salvo em: {txt_processed}")

    # 3. Processar Emissões SEEG Brasil por Estados (Extraído via Selenium)
    brasil_raw = "data/raw/seeg_brasil_estados.csv"
    if os.path.exists(brasil_raw):
        try:
            df_br = pd.read_csv(brasil_raw)
            # Converter colunas numéricas de strings com pontos para float
            colunas_anos = [c for c in df_br.columns if c.isdigit()]
            for c in colunas_anos:
                df_br[c] = df_br[c].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df_br[c] = pd.to_numeric(df_br[c], errors='coerce').fillna(0)
            
            brasil_processed = "data/processed/seeg_brasil_estados_limpo.csv"
            df_br.to_csv(brasil_processed, index=False, encoding='utf-8-sig')
            print(f"Dados SEEG Brasil por Estados processados salvos em: {brasil_processed}")
        except Exception as e:
            print(f"Erro ao processar dados SEEG Brasil: {e}")

    # 4. Processar Dados Históricos Reais de CO2 da NOAA (Mauna Loa)
    co2_raw = "data/raw/co2_mensal_noaa.csv"
    if os.path.exists(co2_raw):
        try:
            df_co2 = pd.read_csv(co2_raw)
            df_co2["Nível de CO2 (ppm)"] = pd.to_numeric(df_co2["Nível de CO2 (ppm)"], errors='coerce')
            df_co2["Tendência Ajustada (ppm)"] = pd.to_numeric(df_co2["Tendência Ajustada (ppm)"], errors='coerce')
            co2_processed = "data/processed/co2_mensal_noaa_limpo.csv"
            df_co2.to_csv(co2_processed, index=False, encoding='utf-8-sig')
            print(f"Dados reais de CO2 NOAA processados salvos em: {co2_processed}")
        except Exception as e:
            print(f"Erro ao processar dados de CO2 NOAA: {e}")

if __name__ == "__main__":
    processar_dados()



