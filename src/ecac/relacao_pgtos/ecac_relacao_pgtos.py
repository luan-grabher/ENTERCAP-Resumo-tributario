from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox
import undetected_chromedriver as uc
import pandas as pd

url_ecac = 'https://cav.receita.fazenda.gov.br/'
driver = None


def ecac_get_relacao_pgtos(data_inicial, data_final):
    relacao = RelacaoPgtos(data_inicial, data_final)

    return relacao.get_relacao_pgtos()


class RelacaoPgtos:

    url_ecac = 'https://cav.receita.fazenda.gov.br/'
    driver = None
    data_inicial = None
    data_final = None

    def __init__(self, data_inicial, data_final):
        self.driver = uc.Chrome()
        self.data_inicial = data_inicial
        self.data_final = data_final

    def get_relacao_pgtos(self):
        if not self.login():
            return False

        comprovante_arrecadacao = self.filtra_compovante_de_arrecadacao()
        if not comprovante_arrecadacao:
            return False
        

        self.driver.close()

    def login(self):
        try:
            url = self.url_ecac + 'autenticacao/login'

            self.driver.get(url)

            selector_botao_fazer_login = '#login-dados-certificado input[onclick*="validarHc'
            self.driver.find_element(
                By.CSS_SELECTOR, selector_botao_fazer_login).click()

            selector_botao_selecionar_certificado = 'button#login-certificate'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector_botao_selecionar_certificado)))
            self.driver.find_element(
                By.CSS_SELECTOR, selector_botao_selecionar_certificado).click()

            msgbox('Resolva o captcha caso apareça e selecione o certificado digital')

            WebDriverWait(self.driver, 10).until(
                EC.url_contains('cav.receita.fazenda.gov.br/ecac'))
        except:
            msgbox('Erro ao tentar fazer login no ECAC')
            return False

        return True

    def filtra_compovante_de_arrecadacao(self):
        try:
            url_aplicacao = 'https://cav.receita.fazenda.gov.br/Servicos/ATFLA/PagtoWeb.app/Default.aspx'
            
            self.driver.get(url_aplicacao)
                        
            selectorDataInicial = "input[name=campoDataArrecadacaoInicial]"        
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selectorDataInicial)))
            self.driver.find_element(By.CSS_SELECTOR, selectorDataInicial).send_keys(self.data_inicial)
            
            selectorDataFinal = "input[name=campoDataArrecadacaoFinal]"            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selectorDataFinal)))
            self.driver.find_element(By.CSS_SELECTOR, selectorDataFinal).send_keys(self.data_final)
                        
            selectorBotaoConsultar = "#botaoConsultar"
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selectorBotaoConsultar)))
            self.driver.find_element(By.CSS_SELECTOR, selectorBotaoConsultar).click()
            
            
            selectorChecboxTodos = "#CheckBoxTodos"
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selectorChecboxTodos)))
            self.driver.find_element(By.CSS_SELECTOR, selectorChecboxTodos).click()
            
            
            selectorBtnImprimirRelacao = "#BtnImprimirRelacao"
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selectorBtnImprimirRelacao)))
            self.driver.find_element(By.CSS_SELECTOR, selectorBtnImprimirRelacao).click()
            
            selectorTabelas = "form table"
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selectorTabelas)))
            tabelas = self.driver.find_elements(By.CSS_SELECTOR, selectorTabelas)
            
            tabela3 = tabelas[3]
            tabelaHtml = tabela3.get_attribute('outerHTML')
            
            dicionario = pd.read_html(tabelaHtml)
            return dicionario

        except:
            msgbox('Erro ao tentar acessar a aplicação de comprovante de arrecadação')
            return False

if __name__ == '__main__':
    ecac_get_relacao_pgtos(data_inicial='01/03/2019', data_final='31/03/2023')
