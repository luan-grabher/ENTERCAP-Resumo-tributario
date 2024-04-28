
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from src.sefaz.sefaz import get_driver_sefaz_logado, acessar_painel_usuario
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss


TIPOS_OPERACAO = {
    'emissao': 'Emissão',
    'recebimento': 'Recebimento'
}

def get_url_painel_contribuinte(driver, cnpj):
    is_already_on_painel = '/PainelContribuinte' in driver.current_url
    if is_already_on_painel:
        return driver.current_url
    
    acessar_painel_usuario(driver)
        
    cnpj_so_numeros = ''.join(filter(str.isdigit, cnpj))        
    
    selector_filtro_cnpj = '#filtroCnpj'
    waitAndSendKeys(driver, selector_filtro_cnpj, cnpj_so_numeros)
    
    time.sleep(1)
    
    selector_link_painel_contribuinte = 'a[href*="Receita/PainelContribuinte"]'
    driver.find_element(By.CSS_SELECTOR, selector_link_painel_contribuinte).click()
            
    WebDriverWait(driver, 10).until(EC.url_contains('/Receita/PainelContribuinte'))
    url_painel_contribuinte = driver.current_url
    
    return url_painel_contribuinte

def get_sefaz_extrato_notas(driver, cnpj, anos: list, tipo_operacao):
    try:
        url_painel_contribuinte = get_url_painel_contribuinte(driver, cnpj)
        
        resultados = {}
        
        for ano in anos:       
            is_in_painel_contribuinte = driver.current_url == url_painel_contribuinte
            if not is_in_painel_contribuinte:
                driver.get(url_painel_contribuinte)
             
            selector_aba_extratos = 'li[onclick="mostraAba(20)"]'
            waitAndClick(driver, selector_aba_extratos)
            
            selector_aba_nfe_nfce = '#tab_extrato_5'
            waitAndClick(driver, selector_aba_nfe_nfce)
            
            selector_checkbox_nfce = 'input#ModeloNFCE'
            waitCss(driver, selector_checkbox_nfce)
            is_already_checked = driver.find_element(By.CSS_SELECTOR, selector_checkbox_nfce).is_selected()
            if not is_already_checked:
                driver.find_element(By.CSS_SELECTOR, selector_checkbox_nfce).click()
            
            selector_checkox_totalizando_por_mes = 'input#PorCFOP'
            is_already_checked = driver.find_element(By.CSS_SELECTOR, selector_checkox_totalizando_por_mes).is_selected()
            if not is_already_checked:
                driver.find_element(By.CSS_SELECTOR, selector_checkox_totalizando_por_mes).click()
            
            data_inicio = '01/01/' + str(ano)
            data_fim = '31/12/' + str(ano)
            
            selector_data_inicial = 'input#DtPeriodoInicio'
            driver.find_element(By.CSS_SELECTOR, selector_data_inicial).clear()
            driver.find_element(By.CSS_SELECTOR, selector_data_inicial).send_keys(data_inicio)
            
            selector_data_final = 'input#DtPeriodoFim'
            driver.find_element(By.CSS_SELECTOR, selector_data_final).clear()
            driver.find_element(By.CSS_SELECTOR, selector_data_final).send_keys(data_fim)
            
            selector_emissao_emitente = 'input#SaidaEmitente'
            selector_emissao_terceiros = 'input#SaidaDestinatario'
            selector_tipo_operacao = selector_emissao_emitente if tipo_operacao == TIPOS_OPERACAO['emissao'] else selector_emissao_terceiros
            is_already_checked = driver.find_element(By.CSS_SELECTOR, selector_tipo_operacao).is_selected()
            if not is_already_checked:
                driver.find_element(By.CSS_SELECTOR, selector_tipo_operacao).click()
            
            selector_checkbox_nfe_canceladas = 'input#NFeCancelada'
            is_already_checked = driver.find_element(By.CSS_SELECTOR, selector_checkbox_nfe_canceladas).is_selected()
            if not is_already_checked:
                driver.find_element(By.CSS_SELECTOR, selector_checkbox_nfe_canceladas).click()
            
            selector_botam_consultar = 'input[onclick="preencheParametros();"]'
            driver.find_element(By.CSS_SELECTOR, selector_botam_consultar).click()
            
            is_nenhum_resultado = False
            try:
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
                
                is_nenhum_resultado = True
            except:
                pass
            
            if is_nenhum_resultado:
                print('nenhum resultado encontrado no ano', ano)
                continue
            
            selector_tabela_resultados = '#aba_extrato_5 table.painel'
            waitCss(driver, selector_tabela_resultados)
            elemento_tabela = driver.find_element(By.CSS_SELECTOR, selector_tabela_resultados)
            
            dataframe = pd.read_html(elemento_tabela.get_attribute('outerHTML'))[0]
            resultados[ano] = dataframe
                    
        return resultados
    except Exception as e:
        raise e
        #return False

if __name__ == '__main__':
    driver = get_driver_sefaz_logado()
    if driver:
        cnpj = '46.540.315/0003-94'        
        anos = [2019, 2020, 2021, 2022, 2023]
        faturamento = get_sefaz_extrato_notas(driver, cnpj, anos, TIPOS_OPERACAO['emissao'])
        compras = get_sefaz_extrato_notas(driver, cnpj, anos, TIPOS_OPERACAO['recebimento'])
        print(faturamento)
        print(compras)
        
        driver.close()