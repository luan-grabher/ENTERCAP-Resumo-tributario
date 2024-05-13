import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox
import pandas as pd
import io

from src.ecac.ecac import get_driver_ecac_logado

url_ecac = 'https://cav.receita.fazenda.gov.br/'
driver = None

def get_codigos_receita():
    json_path = './src/ecac/relacao_pgtos/codigos_receita.json'
    
    codigos_receita = {}
    
    with open(json_path, encoding='utf-8') as json_file:
        codigos_receita = json.load(json_file)
        
    return codigos_receita

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
        
        selectorTabelas = "form table#listagemDARF"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selectorTabelas)))
        tabelaElement = driver.find_element(By.CSS_SELECTOR, selectorTabelas)        
        
        tabelaHtml = tabelaElement.get_attribute('outerHTML')
        
        dicionario = pd.read_html(io=io.StringIO(tabelaHtml))[0].to_dict(orient='records')
        
        codigos_receita = get_codigos_receita()
        
        relacao_pgtos = dict()
        
        for i, item in enumerate(dicionario):
            codigo_receita = item['Código de Receita'] if 'Código de Receita' in item else None
            if not codigo_receita:
                continue
            
            if codigo_receita not in relacao_pgtos:
                relacao_pgtos[codigo_receita] = dict()
            
            apuracao = dict()
            apuracao['Tipo do Documento'] = item['Tipo do Documento'] if 'Tipo do Documento' in item else None
            apuracao['Número do Documento'] = item['Número do Documento'] if 'Número do Documento' in item else None
            apuracao['Período de Apuração'] = item['Período de Apuração'] if 'Período de Apuração' in item else None
            apuracao['Data de Arrecadação'] = item['Data de Arrecadação'] if 'Data de Arrecadação' in item else None
            apuracao['Data de Vencimento'] = item['Data de Vencimento'] if 'Data de Vencimento' in item else None
            apuracao['Código de Receita'] = item['Código de Receita'] if 'Código de Receita' in item else None
            
            apuracao['Valor Total'] = item['Valor Total'] if 'Valor Total' in item else None
            apuracao['Valor Total'] = apuracao['Valor Total'].replace('.', '').replace(',', '.')
            apuracao['Valor Total'] = float(apuracao['Valor Total'])
            
            denominacao_da_receita = codigos_receita[str(codigo_receita)] if str(codigo_receita) in codigos_receita else None
            apuracao['Denominação da Receita'] = denominacao_da_receita
            apuracao['Descrição'] = str(codigo_receita) + ' - ' + str(denominacao_da_receita) if denominacao_da_receita else str(codigo_receita)
            
            relacao_pgtos[codigo_receita][apuracao['Período de Apuração']] = apuracao
        
        return relacao_pgtos

    except Exception as e:
        print(e)
        msgbox('Erro ao tentar acessar a aplicação de comprovante de arrecadação')
        return False

if __name__ == '__main__':
    driver = get_driver_ecac_logado()
    relacao_pgtos = ecac_get_relacao_pgtos(driver, data_inicial='01/03/2019', data_final='31/03/2023')
    print(relacao_pgtos)

    driver.quit()
    exit()