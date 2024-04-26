from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox

url_ecac = 'https://cav.receita.fazenda.gov.br/'
driver = None

def ecac_get_relacao_pgtos():
    relacao = RelacaoPgtos()
    
    return relacao.get_relacao_pgtos()

class RelacaoPgtos:
    
    url_ecac = 'https://cav.receita.fazenda.gov.br/'
    driver = None
    
    def __init__(self):
        self.driver = webdriver.Chrome()
        
    def get_relacao_pgtos(self):
        self.login()
        
        pass
    
    def login(self):
        url = self.url_ecac + 'autenticacao/login'
        
        self.driver.get(url)
        
        selector_botao_fazer_login = '#login-dados-certificado input[onclick*="validarHc'
        self.driver.find_element(By.CSS_SELECTOR, selector_botao_fazer_login).click()
        
        
        selector_botao_selecionar_certificado = 'button#login-certificate'
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_botao_selecionar_certificado)))
        self.driver.find_element(By.CSS_SELECTOR, selector_botao_selecionar_certificado).click()
        
        msgbox('Resolva o captcha e selecione o certificado digital')
        
        pass


if __name__ == '__main__':
    ecac_get_relacao_pgtos()