import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox
import undetected_chromedriver as uc

def get_driver_ecac_logado(driver=None):
    try:
        url = 'https://cav.receita.fazenda.gov.br/autenticacao/login'        
        
        if not driver:
            print('Driver não informado, criando novo driver')
            driver = uc.Chrome()

        driver.get(url)

        try:
            selector_botao_fazer_login = '#login-dados-certificado input[onclick*="validarHc'
            element = driver.find_element(By.CSS_SELECTOR, selector_botao_fazer_login)
            element.click()
            
            #click by js
            driver.execute_script("arguments[0];", element)
            driver.execute_script("arguments[0].click();", element)
        except:
            raise Exception('Botão de login com certificado não encontrado')

        try:
            selector_botao_selecionar_certificado = 'button#login-certificate'
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector_botao_selecionar_certificado)))
            driver.find_element(
                By.CSS_SELECTOR, selector_botao_selecionar_certificado).click()
        except:
            raise Exception('Botão de selecionar certificado não encontrado')

        msgbox('Resolva o captcha caso apareça e selecione o certificado digital')

        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains('cav.receita.fazenda.gov.br/ecac'))
        except:
            raise Exception('Não fez o redirect correto do login')
        
        return driver
    except Exception as e:
        print("(ECAC) Erro ao tentar fazer login no ECAC:", e)
        msgbox('Erro ao tentar fazer login no ECAC')
        return False    

if __name__ == '__main__':
    driver = get_driver_ecac_logado()
    if driver:
        print('Logado com sucesso')
        driver.close()
