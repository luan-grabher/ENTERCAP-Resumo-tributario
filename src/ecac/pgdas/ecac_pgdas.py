import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
from numba import jit

from src.ecac.ecac import get_driver_ecac_logado


def get_pgdas(driver, anos: list):
    filtro_arquivo_download_regex = "PGDASD-.*\.pdf"
    quantidade_arquivos_antes = get_quantidade_downloads(filtro_arquivo_download_regex)
    
    url = 'https://sinac.cav.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgdasd2018.app/Consulta'        
    
    driver.get(url)
    
    selector_input_ano = 'form input#ano'
    selector_button_submit = 'form button[type=submit]'
    
    WebDriverWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_input_ano)))
    
    selector_botoes_download_pdf = "a[data-content='Imprimir Declaração']"
    for ano in anos:
        driver.find_element_by_css_selector(selector_input_ano).send_keys(ano)
        driver.find_element_by_css_selector(selector_button_submit).click()
        
        WebDriverWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_botoes_download_pdf)))
        
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
    
    return

@jit
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
    exit(0)