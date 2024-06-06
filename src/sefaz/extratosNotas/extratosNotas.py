
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from src.sefaz.sefaz import get_driver_sefaz_logado, acessar_painel_usuario
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss
from src.planilha.planilha import Planilha


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
    
    try:
        selector_filtro_cnpj = '#filtroCnpj'
        waitAndSendKeys(driver, selector_filtro_cnpj, cnpj_so_numeros)
    except:
        raise Exception('SEFAZ - Não foi possivel encontrar o campo de filtro de CNPJ')
    
    time.sleep(1)
    
    try:
        selector_link_painel_contribuinte = 'a[href*="Receita/PainelContribuinte"]'
        driver.find_element(By.CSS_SELECTOR, selector_link_painel_contribuinte).click()
    except:
        raise Exception('SEFAZ - Não foi possivel encontrar o CNPJ na lista de contribuintes')
    
    try:
        WebDriverWait(driver, 10).until(EC.url_contains('/Receita/PainelContribuinte'))
        url_painel_contribuinte = driver.current_url
    except:
        raise Exception('SEFAZ - Não foi possivel acessar o painel do contribuinte')
    
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
                    
        return get_resultados_formato_planilha(resultados, tipo_operacao)
    except Exception as e:
        raise e
        #return False

def get_resultados_formato_planilha(resultados, tipo_operacao):
    resultados_formatados = {
        'descricao': 'FATURAMENTO' if tipo_operacao == TIPOS_OPERACAO['emissao'] else 'COMPRAS'
    }
    
    for ano in resultados:
        dataframe = resultados[ano]
        
        for index, row in dataframe.iterrows():
            mes = row['Mês Emit'].split('/')[0]            
            mes = str(mes).zfill(2)
                        
            resultados_formatados[f'{ano}-{mes}'] = float(row['Total NF-e'].replace('.', '').replace(',', '.')) if row['Total NF-e'] else 0
    
    return resultados_formatados

if __name__ == '__main__':
    tipo_teste = input('Tipo de teste:\n1 - Teste webdriver\n2 - Teste planilha\n3 - Teste completo\n')
    
    if tipo_teste == '1':
        
        driver = get_driver_sefaz_logado()
        if driver:
            cnpj = '46.540.315/0003-94'        
            anos = [2019, 2020, 2021, 2022, 2023]
            faturamento = get_sefaz_extrato_notas(driver, cnpj, anos, TIPOS_OPERACAO['emissao'])
            compras = get_sefaz_extrato_notas(driver, cnpj, anos, TIPOS_OPERACAO['recebimento'])
            print('faturamento', faturamento)
            print('compras', compras)
            
            driver.close()
            
    elif tipo_teste == '2':
        resultados = {
            2023: pd.DataFrame({
                'Mês Emit': [11, 12],
                'Qtd NF-e\'s': [2200, 6069],
                'Total NF-e': ['93.352,92', '259.887,89'],
                'Total BC ICMS': ['000', '37.711,13'],
                'Total ICMS': ['000', '6.410,85'],
                'Total BC ICMS ST': [0, 0],
                'Total ICMS ST': [0, 0],
                'Total FCP': [0, 0],
                'FCP Interest UF Dest': [0, 0],
                'ICMS Interest UF Dest': [0, 0],
                'ICMS Interest UF Rem': [0, 0]
            }),
            2022: pd.DataFrame({
                'Mês Emit': [11, 12],
                'Qtd NF-e\'s': [17, 4],
                'Total NF-e': ['127.996,44', '12.858,30'],
                'Total BC ICMS': ['000', '10.571,16'],
                'Total ICMS': ['000', '1.268,54'],
                'Total BC ICMS ST': [0, 0],
                'Total ICMS ST': [0, 0],
                'Total FCP': [0, 0],
                'FCP Interest UF Dest': [0, 0],
                'ICMS Interest UF Dest': [0, 0],
                'ICMS Interest UF Rem': [0, 0]
            })
        }
        tipo_operacao_faturamento = 'emissao'
        tipo_operacao_compras = 'recebimento'
        
        dados_faturamento = get_resultados_formato_planilha(resultados, tipo_operacao_faturamento)
        dados_compras = get_resultados_formato_planilha(resultados, tipo_operacao_compras)
        
        
        planilha_path = 'template.xlsx'
    
        planilha = Planilha(planilha_path)
        planilha.inserir_colunas_mes_aba_dados(1, 2022, 12, 2023)
        planilha.insert_dados_aba_dados([dados_faturamento], False)
        planilha.inserir_valor_dado_na_apresentacao_pela_descricao(dados_faturamento['descricao'], dados_faturamento['descricao'])
        planilha.insert_dados_aba_dados([dados_compras], False)
        planilha.inserir_valor_dado_na_apresentacao_pela_descricao(dados_compras['descricao'], dados_compras['descricao'])
        
        planilha.save('output.xlsx')
        
    elif tipo_teste == '3':
        pass