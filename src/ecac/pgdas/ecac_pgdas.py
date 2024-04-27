import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time

from src.ecac.ecac import get_driver_ecac_logado


def get_pgdas(driver, anos: list):
    url = 'https://sinac.cav.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgdasd2018.app/Consulta'        
    driver.get(url)

    filtro_arquivo_download_regex = "PGDASD-.*\\.pdf"
    baixar_pgdas(driver, anos, filtro_arquivo_download_regex)

def baixar_pgdas(driver, anos: list, filtro_arquivo_download_regex: str):
    
    quantidade_arquivos_antes = get_quantidade_downloads(filtro_arquivo_download_regex)
    
    selector_input_ano = 'form input#ano'
    selector_button_submit = 'form button[type=submit]'
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_input_ano)))
    
    selector_botoes_download_pdf = "a[data-content='Imprimir Declaração']"
    for ano in anos:
        driver.find_element(By.CSS_SELECTOR, selector_input_ano).send_keys(ano)
        driver.find_element(By.CSS_SELECTOR, selector_button_submit).click()
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_botoes_download_pdf)))
        except:
            continue
        
        botoes_dowload = driver.find_elements(By.CSS_SELECTOR, selector_botoes_download_pdf)
        for botao in botoes_dowload:
            botao.click()

        tentativas_maximas = 30
        tentativas = 0
        while True:
            tentativas += 1
            
            quantidade_arquivos_depois = get_quantidade_downloads(filtro_arquivo_download_regex)
            if quantidade_arquivos_depois == quantidade_arquivos_antes + len(botoes_dowload):
                break
            
            if tentativas > tentativas_maximas:
                break
        
            time.sleep(1)
    
    return True

def get_dados_dos_arquivos_downloads(filtro_arquivo_download_regex):
    user_download_path = os.path.expanduser('~') + '\\Downloads'
    downloads = os.listdir(user_download_path)
    dados = []
    for download in downloads:
        if re.match(filtro_arquivo_download_regex, download):
            dados.append(download)
    return dados

def get_quantidade_downloads(filtro_arquivo_download_regex):
    user_download_path = os.path.expanduser('~') + '\\Downloads'
    downloads = os.listdir(user_download_path)
    quantidade_arquivos = 0
    for download in downloads:
        if re.match(filtro_arquivo_download_regex, download):
            quantidade_arquivos += 1
    return quantidade_arquivos

if __name__ == '__main__':
    driver = get_driver_ecac_logado()
    get_pgdas(driver=driver, anos=[2019, 2020, 2021, 2022, 2023])
    driver.close()
    
    print('Fim do programa')
    
    exit(0)