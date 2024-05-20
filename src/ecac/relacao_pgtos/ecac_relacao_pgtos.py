import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from easygui import msgbox
import pandas as pd
import io

from src.ecac.ecac import get_driver_ecac_logado
from src.planilha.planilha import Planilha

url_ecac = 'https://cav.receita.fazenda.gov.br/'
driver = None

def get_codigos_receita():
    json_path = './src/ecac/relacao_pgtos/codigos_receita.json'
    
    codigos_receita = {}
    
    with open(json_path, encoding='utf-8') as json_file:
        codigos_receita = json.load(json_file)
        
    return codigos_receita

def get_competencia(data: str) -> str:
    data_split = data.split('/')
    mes_MM = data_split[1].zfill(2)
    ano = data_split[2]
    
    return f'{ano}-{mes_MM}'

def ecac_get_relacao_pgtos(driver, data_inicial, data_final) -> list[dict[str, dict[str, str | float]]]:

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
        total_pgtos = 0
        
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
            total_pgtos+= apuracao['Valor Total']
            
            denominacao_da_receita = codigos_receita[str(codigo_receita)] if str(codigo_receita) in codigos_receita else None
            apuracao['Denominação da Receita'] = denominacao_da_receita
            apuracao['Descrição'] = str(codigo_receita) + ' - ' + str(denominacao_da_receita) if denominacao_da_receita else str(codigo_receita)
            
            relacao_pgtos[codigo_receita][apuracao['Período de Apuração']] = apuracao
        
        return relacao_pgtos, total_pgtos

    except Exception as e:
        print('(ECAC) ERRO NA RELAÇÃO DE PAGAMENTOS')
        print(e)
        raise Exception('Erro ao tentar acessar a aplicação de comprovante de arrecadação')

def converter_relacao_pgtos_lista_planilha(relacao_pgtos: dict[str, dict[str, dict[str, str | float]]]) -> list[dict[str, str | float]]:
    lista_planilha = []
    
    for codigo_receita in relacao_pgtos:
        dado = dict()
        
        for periodo_apuracao in relacao_pgtos[codigo_receita]:
            apuracao = relacao_pgtos[codigo_receita][periodo_apuracao]
            
            dado['descricao'] = apuracao['Descrição']
            
            competencia = get_competencia(apuracao['Período de Apuração'])
            dado[f'{competencia}'] = apuracao['Valor Total']
            
        lista_planilha.append(dado)
    
    return lista_planilha

if __name__ == '__main__':
    tipo_teste = input('Tipo de teste:\n (1 - Teste ECAC)\n (2 - Teste Inserção na planilha)\n')
    
    if tipo_teste == '1':
        driver = get_driver_ecac_logado()
        relacao_pgtos, total_pgtos = ecac_get_relacao_pgtos(driver, data_inicial='01/03/2019', data_final='31/03/2023')
        print(relacao_pgtos)
        print(total_pgtos)

        driver.quit()
    elif tipo_teste == '2':
        relacao_pgtos = {
            '0211': {
                '01/03/2019': {
                    'Tipo do Documento': 'DARF',
                    'Número do Documento': '0211.2019.03.001',
                    'Período de Apuração': '01/03/2019',
                    'Data de Arrecadação': '15/03/2019',
                    'Data de Vencimento': '16/03/2019',
                    'Código de Receita': '0211',
                    'Valor Total': 100.0,
                    'Denominação da Receita': 'IRPF - Carnê-Leão',
                    'Descrição': '0211 - IRPF - Carnê-Leão'
                },
                '01/04/2019': {
                    'Tipo do Documento': 'DARF',
                    'Número do Documento': '0211.2019.04.001',
                    'Período de Apuração': '01/04/2019',
                    'Data de Arrecadação': '15/04/2019',
                    'Data de Vencimento': '16/04/2019',
                    'Código de Receita': '0211',
                    'Valor Total': 200.0,
                    'Denominação da Receita': 'IRPF - Carnê-Leão',
                    'Descrição': '0211 - IRPF - Carnê-Leão'
                }
            }
        }
        
        lista_planilha = converter_relacao_pgtos_lista_planilha(relacao_pgtos)
        print(lista_planilha)
        
        planilha_path = 'template.xlsx'
    
        planilha = Planilha(planilha_path)
        planilha.inserir_colunas_mes_aba_dados(1, 2019, 12, 2021)
        planilha.insert_dados_aba_dados(lista_planilha, True)
        
        planilha.save('output.xlsx')
        
    else:
        print('Opção inválida')
        
    exit()