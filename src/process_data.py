import pandas as pd
import os
import re

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
        df['titulo_limpo'] = df['titulo'].apply(limpar_texto)
        
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

if __name__ == "__main__":
    processar_dados()
