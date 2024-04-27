import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_driver_sefaz_logado(driver=None):
    if not driver:
        driver = uc.Chrome()
    
    if not login(driver):
        return False
    
    acessar_painel_usuario(driver)
    
    return driver

def login(driver):
    try:
        url = 'https://www.sefaz.rs.gov.br/Login/LoginCertACRS.aspx?codTpLogin=1'
        driver.get(url)
        
        selector_botao_selecionar_certificado = 'a[onclick*="document.frmCert.submit"]'    
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_botao_selecionar_certificado)))
        driver.find_element(
            By.CSS_SELECTOR, selector_botao_selecionar_certificado).click()
        
        selector_confirmar_tipo_de_login = 'input[onclick*="direcionaECnpj"]'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_confirmar_tipo_de_login)))
        driver.find_element(
            By.CSS_SELECTOR, selector_confirmar_tipo_de_login).click()
        
        return True
        
    except:
        return False
        
def acessar_painel_usuario(driver):
    url = 'https://www.sefaz.rs.gov.br/Receita/PainelUsuario.aspx'
    driver.get(url)
    
    try:
        selector_close_modal = "#cboxClose"
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_close_modal)))
        driver.find_element(By.CSS_SELECTOR, selector_close_modal).click()
    except:
        pass
    
    print('Acessou o painel do usuário')    
    
if __name__ == '__main__':
    driver = get_driver_sefaz_logado()
    if driver:
        driver.close()
    
    