
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_driver_esocial_logado(driver=None):
    if not driver:
        driver = uc.Chrome()
        
    if not login(driver):
        return False
    
    print('Logado com sucesso no eSocial')
        
    return driver
    
def login(driver):
    try:
        url = "https://login.esocial.gov.br/login.aspx"
        
        driver.get(url)
        
        
        selector_botao_login_com_gov = '#login-acoes button.sign-in'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_botao_login_com_gov)))
        driver.find_element(By.CSS_SELECTOR, selector_botao_login_com_gov).click()
        
        try:
            if 'www.esocial.gov.br/portal/Home/Inicial?tipoEmpregador=EMPREGADOR_GERAL' in driver.current_url:
                return True
            
            WebDriverWait(driver, 4).until(
                EC.url_contains('www.esocial.gov.br/portal/Home/Inicial?tipoEmpregador=EMPREGADOR_GERAL'))
            
            return True
        except:
            pass
        
        selector_botao_selecionar_certificado = 'button#login-certificate'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector_botao_selecionar_certificado)))
        driver.find_element(
            By.CSS_SELECTOR, selector_botao_selecionar_certificado).click()
        
        esperar_usuario_escolher_certificado = True
        while esperar_usuario_escolher_certificado:
            try:
                WebDriverWait(driver, 2).until(
                    EC.url_contains('www.esocial.gov.br/portal/Home/Inicial?tipoEmpregador=EMPREGADOR_GERAL'))
                break
            except:
                pass
        
        return True
    except Exception as e:
        print('(ESOCIAL) Erro ao tentar fazer login no eSocial:', e)
        
        return False    
    
if __name__ == '__main__':
    driver = get_driver_esocial_logado()
    if driver:
        driver.close()