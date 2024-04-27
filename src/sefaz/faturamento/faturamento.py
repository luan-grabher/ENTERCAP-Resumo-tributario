
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.sefaz.sefaz import get_driver_sefaz_logado, acessar_painel_usuario

def get_faturamento_sefaz(driver, cnpj):
    try:
        acessar_painel_usuario(driver)
        
        cnpj_so_numeros = ''.join(filter(str.isdigit, cnpj))
        
        selector_filtro_cnpj = '#filtroCnpj'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_filtro_cnpj)))
        driver.find_element(By.CSS_SELECTOR, selector_filtro_cnpj).send_keys(cnpj_so_numeros)
        
        time.sleep(1)
        
        selector_link_painel_contribuinte = 'a[href*="Receita/PainelContribuinte"]'
        driver.find_element(By.CSS_SELECTOR, selector_link_painel_contribuinte).click()
        
        
        return faturamento
    except:
        return False

if __name__ == '__main__':
    driver = get_driver_sefaz_logado()
    if driver:
        cnpj = '46.540.315/0003-94'        
        faturamento = get_faturamento_sefaz(driver, cnpj)
        
        driver.close()