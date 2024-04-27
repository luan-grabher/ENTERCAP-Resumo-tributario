from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox
import undetected_chromedriver as uc

def get_driver_ecac_logado():
    try:
        url = 'https://cav.receita.fazenda.gov.br/autenticacao/login'        
        
        driver = uc.Chrome()

        driver.get(url)

        selector_botao_fazer_login = '#login-dados-certificado input[onclick*="validarHc'
        driver.find_element(
            By.CSS_SELECTOR, selector_botao_fazer_login).click()

        selector_botao_selecionar_certificado = 'button#login-certificate'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_botao_selecionar_certificado)))
        driver.find_element(
            By.CSS_SELECTOR, selector_botao_selecionar_certificado).click()

        msgbox('Resolva o captcha caso apareça e selecione o certificado digital')

        WebDriverWait(driver, 10).until(
            EC.url_contains('cav.receita.fazenda.gov.br/ecac'))
        
        return driver
    except:
        msgbox('Erro ao tentar fazer login no ECAC')
        return False    

if __name__ == '__main__':
    driver = get_driver_ecac_logado()
    if driver:
        driver.close()
