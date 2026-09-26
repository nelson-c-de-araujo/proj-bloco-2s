import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

"""
Script de Web Scraping para o TP2 - ODS 13 (Ação Contra a Mudança Global do Clima)
Extrai informações e conteúdos sobre ODS 13 de fontes confiáveis e salva em data/raw/
"""

FONTES = [
    {
        "nome": "Agência Brasil - Clima",
        "url": "https://agenciabrasil.ebc.com.br/tags/mudancas-climaticas",
        "base_url": "https://agenciabrasil.ebc.com.br"
    },
    {
        "nome": "ONU News - Meio Ambiente",
        "url": "https://news.un.org/pt/news/topic/climate-change",
        "base_url": "https://news.un.org"
    }
]

def extrair_noticias_ods13():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    dados_noticias = []
    textos_completos = []

    for fonte in FONTES:
        url = fonte["url"]
        print(f"Buscando conteúdos em [{fonte['nome']}]: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Aviso: Status {response.status_code} ao acessar {url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Busca por títulos/links
            links = soup.find_all('a', href=True)
            for a in links:
                titulo = a.get_text(strip=True)
                # Filtrar títulos relevantes sobre clima/emissões/ODS 13
                if len(titulo) > 20 and any(kw in titulo.lower() for kw in ['clima', 'emiss', 'aqueciment', 'carbon', 'ods', 'sustentab', 'cop', 'ambiente', 'gás', 'florest']):
                    link = a['href']
                    if not link.startswith('http'):
                        link = fonte["base_url"] + link

                    # Tentar encontrar elemento pai para pegar resumo
                    pai = a.find_parent(['article', 'div', 'li'])
                    resumo = "Notícia sobre Ação Climática e ODS 13."
                    if pai:
                        p = pai.find('p')
                        if p:
                            resumo = p.get_text(strip=True)

                    dados_noticias.append({
                        "fonte": fonte["nome"],
                        "titulo": titulo,
                        "resumo": resumo,
                        "link": link,
                        "categoria": "ODS 13 - Ação Climática"
                    })
                    textos_completos.append(f"{titulo}. {resumo}")

        except Exception as e:
            print(f"Erro ao processar {url}: {e}")

    # Fallback/dados base garantidos caso os sites restrinjam em momentos específicos
    if len(dados_noticias) < 3:
        print("Adicionando conjunto base de dados institucionais ODS 13...")
        base_ods13 = [
            {
                "fonte": "Nações Unidas Brasil",
                "titulo": "ODS 13: Tomar medidas urgentes para combater a mudança climática e seus impactos",
                "resumo": "A mudança do clima é um desafio global que não respeita fronteiras nacionais. As emissões em qualquer lugar afetam as pessoas em todos os lugares.",
                "link": "https://brasil.un.org/pt-br/sdgs/13",
                "categoria": "ODS 13 - Ação Climática"
            },
            {
                "fonte": "IPCC / ONU",
                "titulo": "Relatório do IPCC alerta para necessidade urgente de redução de emissões de CO2",
                "resumo": "Para limitar o aquecimento global em 1.5°C, as emissões globais de gases de efeito estufa devem ser reduzidas drasticamente até 2030.",
                "link": "https://www.ipcc.ch/",
                "categoria": "ODS 13 - Ação Climática"
            },
            {
                "fonte": "NOAA Global Monitoring Laboratory",
                "titulo": "Concentração atmosférica de CO2 atinge novo recorde histórico em 2024",
                "resumo": "Observatórios mundiais registram aumento contínuo das partes por milhão (ppm) de dióxido de carbono na atmosfera.",
                "link": "https://gml.noaa.gov/ccgg/trends/",
                "categoria": "ODS 13 - Ação Climática"
            }
        ]
        dados_noticias.extend(base_ods13)
        for item in base_ods13:
            textos_completos.append(f"{item['titulo']}. {item['resumo']}")

    # Garantir pasta data/raw
    os.makedirs("data/raw", exist_ok=True)

    # 1. Salvar CSV
    df = pd.DataFrame(dados_noticias)
    df.drop_duplicates(subset=['titulo'], inplace=True)
    csv_path = "data/raw/noticias_ods13.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"Sucesso! {len(df)} registros salvos em: {csv_path}")

    # 2. Salvar TXT
    txt_path = "data/raw/conteudo_ods13.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(textos_completos))
    print(f"Sucesso! Conteúdo compilado salvo em: {txt_path}")

if __name__ == "__main__":
    extrair_noticias_ods13()
