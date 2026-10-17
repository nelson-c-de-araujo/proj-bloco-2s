import time
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

"""
Módulo de Extração de Emissões Nacionais por Estado via Selenium (Páginas Dinâmicas da Plataforma SEEG).
URL da Plataforma com filtros dinâmicos de 1990 a 2024 clusterizados por Estado:
https://plataforma.seeg.eco.br/?yearRange%5B0%5D=1990&yearRange%5B1%5D=2024&emissionType%5B0%5D=1&gas=8&groupBy=State&rankBy=State&filtersTab=highlights&statisticsTab=historical
"""

SEEG_PLATAFORMA_ESTADOS_URL = (
    "https://plataforma.seeg.eco.br/?yearRange%5B0%5D=1990&yearRange%5B1%5D=2024"
    "&emissionType%5B0%5D=1&gas=8&groupBy=State&rankBy=State"
    "&filtersTab=highlights&statisticsTab=historical"
)

RAW_OUTPUT_CSV = os.path.join("data", "raw", "seeg_brasil_estados.csv")


def extrair_seeg_brasil_estados_selenium(output_path: str = RAW_OUTPUT_CSV) -> pd.DataFrame:
    """
    Executa o navegador Chrome em modo headless via Selenium para acessar a SPA da Plataforma SEEG,
    aguarda a renderização dos componentes assíncronos e extrai a tabela 'sticky-table'
    com o histórico de emissões (1990-2024) desagregado por todos os Estados do Brasil.
    """
    print(f"[Selenium SEEG] Acessando plataforma dinâmica: {SEEG_PLATAFORMA_ESTADOS_URL}")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(SEEG_PLATAFORMA_ESTADOS_URL)
        time.sleep(12)  # Tempo suficiente para carregar D3/React e preencher a tabela

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Localiza o contêiner com a classe informada: 'sc-fqkvVR zBhLB _table_6ijd8_5 sticky-table'
        container = soup.find("div", class_=lambda c: c and "sticky-table" in c)
        
        if not container:
            raise RuntimeError("Elemento da tabela sticky-table não encontrado na página da Plataforma SEEG.")

        rows = container.find_all("div", class_=lambda c: c and "sticky-table-row" in c)
        if not rows:
            raise RuntimeError("Nenhuma linha encontrada dentro de sticky-table.")

        # Linha de cabeçalho
        header_cells = rows[0].find_all("div", class_=lambda c: c and "sticky-table-cell" in c)
        headers = [c.get_text(strip=True) for c in header_cells]
        if headers and headers[0].lower() in ["categoria", ""]:
            headers[0] = "Estado"

        table_data = []
        for r in rows[1:]:
            cells = r.find_all("div", class_=lambda c: c and "sticky-table-cell" in c)
            row_vals = [c.get_text(strip=True) for c in cells]
            if row_vals:
                table_data.append(row_vals)

        df = pd.DataFrame(table_data, columns=headers)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"[Selenium SEEG] Extração concluída com sucesso! {df.shape[0]} estados salvos em: {output_path}")
        return df

    except Exception as e:
        print(f"[Selenium SEEG] Erro na extração da plataforma: {e}")
        # Se ocorrer erro e já existir arquivo em disco, retorna o existente
        if os.path.exists(output_path):
            return pd.read_csv(output_path)
        raise e
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    extrair_seeg_brasil_estados_selenium()

