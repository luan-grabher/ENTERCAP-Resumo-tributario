
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.sefaz.sefaz import get_driver_sefaz_logado, acessar_painel_usuario
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss
from src.planilha.planilha import Planilha


def get_dict_list_from_driver_table_element(tableElement) -> list[dict[str, str]]:
    headers = tableElement.find_elements(By.TAG_NAME, 'th')
    headers_text = [header.text.replace("\n", ' ') for header in headers]

    rows = tableElement.find_elements(By.TAG_NAME, 'tr')

    lista = []

    for row in rows:
        colunas = row.find_elements(By.TAG_NAME, 'td')
        row_dict = dict()

        for index_coluna, elemento_coluna in enumerate(colunas):
            if headers_text[index_coluna] in ('', ' '):
                continue

            texto = elemento_coluna.get_attribute('textContent')
            texto = texto.strip()

            row_dict[headers_text[index_coluna]] = texto

        lista.append(row_dict)

    return lista


def get_cnpjs_painel_contribuinte_urls(driver) -> dict[str, str]:
    acessar_painel_usuario(driver)

    urls = {}
    try:
        selector_primeira_linha_tabela = "table#tblListaVinc tr:first-child th"
        headers_tabela = driver.find_elements(
            By.CSS_SELECTOR, selector_primeira_linha_tabela)

        coluna_cnpj = None
        coluna_situacao = None
        for index, header in enumerate(headers_tabela):
            idElemento = header.get_attribute('id')
            if idElemento == 'cnpj14Header':
                coluna_cnpj = index
            elif idElemento == 'situacaoHeader':
                coluna_situacao = index

        if coluna_situacao is None:
            raise Exception(
                'SEFAZ - Não foi possivel encontrar a coluna de situação na tabela de vinculos')

        selector_linhas_tabela_vinculos = 'table#tblListaVinc tr'
        elementos_linhas_tabela = driver.find_elements(
            By.CSS_SELECTOR, selector_linhas_tabela_vinculos)
        for elemento_linha in elementos_linhas_tabela:
            selector_situacao = f'td:nth-child({coluna_situacao + 1})'
            selector_cnpj = f'td:nth-child({coluna_cnpj + 1})'
            try:
                situacao = elemento_linha.find_element(
                    By.CSS_SELECTOR, selector_situacao).get_attribute('textContent')
                if situacao != 'Ativa':
                    continue

                cnpj = elemento_linha.find_element(
                    By.CSS_SELECTOR, selector_cnpj).get_attribute('textContent')

                selector_link_painel_contribuinte = 'a[href*="Receita/PainelContribuinte"]:not([href$="ie="])'
                elementos_link = elemento_linha.find_elements(
                    By.CSS_SELECTOR, selector_link_painel_contribuinte)

                for elemento in elementos_link:
                    link = elemento.get_attribute('href')
                    urls[cnpj] = link
            except:
                pass

    except:
        raise Exception(
            'SEFAZ - Não foi possivel encontrar os links dos CNPJs no painel do contribuinte')

    return urls


def get_conta_corrente_fiscal_from_cnpj(driver, url_painel_contribuinte: str, anos: list, cnpj: str) -> list[dict[str, str | float]]:
    try:
        resultados = {}

        is_in_painel_contribuinte = driver.current_url == url_painel_contribuinte
        if not is_in_painel_contribuinte:
            driver.get(url_painel_contribuinte)

        selector_aba_conta_corrente_fiscal = 'li[onclick="mostraAba(6)"]'
        waitAndClick(driver, selector_aba_conta_corrente_fiscal)

        for ano in anos:
            selector_periodo_inicial = 'input#CCF_DtIni'
            selector_periodo_fim = 'input#CCF_DtFim'
            selector_botao_consultar = 'input[onclick="CCF_Consulta();"]'

            periodo_inicial = '01' + str(ano)
            periodo_fim = '12' + str(ano)

            waitAndSendKeys(driver, selector_periodo_inicial, periodo_inicial)
            waitAndSendKeys(driver, selector_periodo_fim, periodo_fim)

            waitAndClick(driver, selector_botao_consultar)

            is_nenhum_resultado = False
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()

                is_nenhum_resultado = True
            except:
                pass

            if is_nenhum_resultado:
                print('nenhum resultado encontrado no ano', ano)
                continue

            selector_tabela_resultados = 'div#ContaCorrenteFiscal table.painel'
            waitCss(driver, selector_tabela_resultados)
            elemento_tabela = driver.find_element(
                By.CSS_SELECTOR, selector_tabela_resultados)

            dados_tabela = get_dict_list_from_driver_table_element(
                elemento_tabela)
            resultados[ano] = dados_tabela

        return get_resultados_formato_planilha(resultados, cnpj)
    except Exception as e:
        raise e
        # return False

def get_string_value_as_float(string_value: str) -> float:
    if not string_value:
        return 0
    
    formatted_string = string_value.replace('.', '').replace(',', '.')
    return float(formatted_string)

def get_resultados_formato_planilha(resultados: dict[str, list[dict[str, str]]], cnpj: str) -> list[dict[str, str | float]]:
    resultados_dict = {
        'ICMS DIF AL' : {
            'descricao': 'ICMS DIF AL - ' + cnpj,
        },
        'ICMS Mensal' : {
            'descricao': 'ICMS Mensal - ' + cnpj,
        },
        'ICMS - Fundo Combate a Pobresa' : {
            'descricao': 'ICMS - Fundo Combate a Pobresa - ' + cnpj,
        },
        'GIA Mensal' : {
            'descricao': 'GIA Mensal - ' + cnpj,
        },
    }

    for ano in resultados:
        referencia = None
        
        for linha_tabela in resultados[ano]:
            referencia_linha = linha_tabela.get('Referência', '')
            if referencia_linha:
                mes, ano = referencia_linha.split('/')
                mes = str(mes).zfill(2)
                referencia = f'{ano}-{mes}'

            descricao = linha_tabela.get('Documento', '')
            
            if descricao == 'STDA C/ICMS RECOLHER DIF AL':
                valor = get_string_value_as_float(linha_tabela.get('Valor', '0,00'))
                resultados_dict['ICMS DIF AL'][referencia] = valor
            elif descricao == 'Guia de Arrecadacao':
                valor = get_string_value_as_float(linha_tabela.get('Valor', '0,00'))
                resultados_dict['ICMS Mensal'][referencia] = valor
            elif descricao == 'GUIA DE ARRECADACAO-FCP/ICMS-PR':
                valor = get_string_value_as_float(linha_tabela.get('Valor', '0,00'))
                resultados_dict['ICMS - Fundo Combate a Pobresa'][referencia] = valor
            elif descricao == 'GIA Mensal - Saldo Zerado' or 'GIA Mensal - Saldo Credor' in descricao:
                is_zerado = 'Zerado' in descricao
                if is_zerado:
                    valor = 0
                else:
                    valor_by_split = descricao.split('R$')
                    valor = get_string_value_as_float(valor_by_split[-1])
                    
                resultados_dict['GIA Mensal'][referencia] = valor

    resultados_formatados = []
    for dado in resultados_dict:
        resultados_formatados.append(resultados_dict[dado])

    return resultados_formatados


def get_conta_corrente_fiscal(driver, anos: list) -> list[dict[str, dict[str, str | float]]]:
    cnpjs_urls = get_cnpjs_painel_contribuinte_urls(driver)

    resultados = []

    for cnpj in cnpjs_urls:
        cnpj_url = cnpjs_urls[cnpj]
        resultados_cnpj = get_conta_corrente_fiscal_from_cnpj(
            driver, cnpj_url, anos, cnpj)
        resultados = resultados + resultados_cnpj

    return resultados


def test_webdriver():
    driver = get_driver_sefaz_logado()
    if driver:
        anos = [2022, 2023, 2024]
        conta_corrente_fiscal = get_conta_corrente_fiscal(driver, anos)
        print(conta_corrente_fiscal)

        driver.close()

        return True

    return False


def test_create_planilha(resultados: list[dict[str, dict[str, str | float]]]):
    
    planilha_path = 'template.xlsx'

    planilha = Planilha(planilha_path)
    planilha.inserir_colunas_mes_aba_dados(1, 2022, 12, 2024)
    planilha.insert_dados_aba_dados(resultados, False)
    planilha.inserir_soma_dados_na_apresentacao_por_regex_acima_de_TRIBUTOS('GIA Mensal - *', 'ICMS - Saldo Credor')
    planilha.ajustar_width_colunas_aba('Dados')

    planilha.save('output.xlsx')


if __name__ == '__main__':
    tipo_teste = input(
        'Tipo de teste:\n1 - Teste webdriver\n2 - Teste planilha\n3 - Teste completo\n')

    if tipo_teste == '1':
        test_webdriver()

    elif tipo_teste == '2':
        resultados = {
            2023: [
                {},
                {
                    'Referência': '11/2023',
                    'Apuração': '01-30',
                    'Vencimento': '23/01/2024',
                    'Documento': 'STDA C/ICMS RECOLHER DIF AL',
                    'Nº Guia': '',
                    'Nº Documento': '17148305', 'Pagamento': '', 'Ciência': '', 'Valor': '0,00', 'Saldo': ''},
                {
                    'Referência': '', 'Apuração': '', 'Vencimento': '', 'Documento': '', 'Nº Guia': '', 'Nº Documento': '',
                    'Pagamento': '', 'Ciência': '', 'Valor': 'Saldo em 11/2023 ==>', 'Saldo': '0,00'
                },
                {'Referência': '12/2023', 'Apuração': '01-31', 'Vencimento': '23/02/2024', 'Documento': 'STDA C/ICMS RECOLHER DIF AL',
                 'Nº Guia': '', 'Nº Documento': '17236026', 'Pagamento': '', 'Ciência': '', 'Valor': '0,00', 'Saldo': ''
                 },
                {'Referência': '', 'Apuração': '', 'Vencimento': '', 'Documento': '', 'Nº Guia': '', 'Nº Documento': '', 'Pagamento': '',
                 'Ciência': '', 'Valor': 'Saldo em 12/2023 ==>', 'Saldo': '0,00'
                 }
            ],
            2024: [
                {},
                {
                    'Referência': '01/2024', 'Apuração': '01-31', 'Vencimento': '23/03/2024', 'Documento': 'STDA C/ICMS RECOLHER DIF AL',
                    'Nº Guia': '', 'Nº Documento': '17356630', 'Pagamento': '', 'Ciência': '', 'Valor': '0,00', 'Saldo': ''
                },
                {
                    'Referência': '', 'Apuração': '', 'Vencimento': '', 'Documento': '', 'Nº Guia': '', 'Nº Documento': '', 'Pagamento': '',
                    'Ciência': '', 'Valor': 'Saldo em 01/2024 ==>', 'Saldo': '0,00'
                },
                {
                    'Referência': '02/2024', 'Apuração': '01-29', 'Vencimento': '23/04/2024', 'Documento': 'STDA C/ICMS RECOLHER DIF AL', 'Nº Guia': '',
                    'Nº Documento': '17441278', 'Pagamento': '', 'Ciência': '', 'Valor': '0,00', 'Saldo': ''
                },
                {
                    'Referência': '', 'Apuração': '', 'Vencimento': '', 'Documento': '', 'Nº Guia': '', 'Nº Documento': '', 'Pagamento': '', 'Ciência': '',
                    'Valor': 'Saldo em 02/2024 ==>', 'Saldo': '0,00'
                },
                {
                    'Referência': '03/2024', 'Apuração': '01-31', 'Vencimento': '23/05/2024', 'Documento': 'Guia de Arrecadacao', 'Nº Guia': '82224040834198',
                    'Nº Documento': '342176765', 'Pagamento': '23/05/2024', 'Ciência': '', 'Valor': '10.674,46', 'Saldo': ''
                },
                {
                    'Referência': '', 'Apuração': '', 'Vencimento': '23/05/2024', 'Documento': 'STDA C/ICMS RECOLHER DIF AL', 'Nº Guia': '', 'Nº Documento': '17594690',
                    'Pagamento': '', 'Ciência': '', 'Valor': '0,00', 'Saldo': ''
                },
                    {
                        'Referência': '', 'Apuração': '', 'Vencimento': '', 'Documento': '', 'Nº Guia': '', 'Nº Documento': '', 'Pagamento': '', 'Ciência': '',
                        'Valor': 'Saldo em 03/2024 ==>', 'Saldo': '10.674,46'
                    }
            ]
        }

        resultados_para_planilha = get_resultados_formato_planilha(
            resultados, '12345678901234')
        
        test_create_planilha(resultados_para_planilha)

    elif tipo_teste == '3':
        pass
