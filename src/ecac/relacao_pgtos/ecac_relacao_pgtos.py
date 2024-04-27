from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox
import pandas as pd

from src.ecac.ecac import get_driver_ecac_logado

url_ecac = 'https://cav.receita.fazenda.gov.br/'
driver = None


def ecac_get_relacao_pgtos(driver, data_inicial, data_final):

    try:
        url_aplicacao = 'https://cav.receita.fazenda.gov.br/Servicos/ATFLA/PagtoWeb.app/Default.aspx'
        
        driver.get(url_aplicacao)
                    
        selectorDataInicial = "input[name=campoDataArrecadacaoInicial]"        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorDataInicial)))
        driver.find_element(By.CSS_SELECTOR, selectorDataInicial).send_keys(data_inicial)
        
        selectorDataFinal = "input[name=campoDataArrecadacaoFinal]"            
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorDataFinal)))
        driver.find_element(By.CSS_SELECTOR, selectorDataFinal).send_keys(data_final)
                    
        selectorBotaoConsultar = "#botaoConsultar"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorBotaoConsultar)))
        driver.find_element(By.CSS_SELECTOR, selectorBotaoConsultar).click()
        
        
        selectorChecboxTodos = "#CheckBoxTodos"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorChecboxTodos)))
        driver.find_element(By.CSS_SELECTOR, selectorChecboxTodos).click()
        
        
        selectorBtnImprimirRelacao = "#BtnImprimirRelacao"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorBtnImprimirRelacao)))
        driver.find_element(By.CSS_SELECTOR, selectorBtnImprimirRelacao).click()
        
        selectorTabelas = "form table"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorTabelas)))
        tabelas = driver.find_elements(By.CSS_SELECTOR, selectorTabelas)
        
        tabela3 = tabelas[3]
        tabelaHtml = tabela3.get_attribute('outerHTML')
        
        dicionario = pd.read_html(tabelaHtml)
        return dicionario

    except:
        msgbox('Erro ao tentar acessar a aplicação de comprovante de arrecadação')
        return False

if __name__ == '__main__':
    driver = get_driver_ecac_logado()
    ecac_get_relacao_pgtos(driver, data_inicial='01/03/2019', data_final='31/03/2023')
