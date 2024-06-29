
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.sefaz.sefaz import get_driver_sefaz_logado, acessar_painel_usuario
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss, waitDisappear
from src.planilha.planilha import Planilha


TIPOS_OPERACAO = {
    'emissao': 'Emissão',
    'recebimento': 'Recebimento'
}


def get_dict_list_from_driver_table_element(tableElement) -> list[dict[str, str]]:
    try:
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

                row_dict[headers_text[index_coluna]
                        ] = elemento_coluna.get_attribute('textContent')

            lista.append(row_dict)
    except Exception as e:
        raise Exception(
            'SEFAZ - Erro ao tentar extrair dados da tabela de extrato de notas - ' + str(e))

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


def get_sefaz_extrato_notas_from_cnpj(driver, url_painel_contribuinte: str, anos: list, tipo_operacao: str, cnpj: str):
    try:
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
            is_already_checked = driver.find_element(
                By.CSS_SELECTOR, selector_checkbox_nfce).is_selected()
            if not is_already_checked:
                driver.find_element(
                    By.CSS_SELECTOR, selector_checkbox_nfce).click()

            selector_checkox_totalizando_por_mes = 'input#PorCFOP'
            is_already_checked = driver.find_element(
                By.CSS_SELECTOR, selector_checkox_totalizando_por_mes).is_selected()
            if not is_already_checked:
                driver.find_element(
                    By.CSS_SELECTOR, selector_checkox_totalizando_por_mes).click()

            data_inicio = '01/01/' + str(ano)
            data_fim = '31/12/' + str(ano)

            selector_data_inicial = 'input#DtPeriodoInicio'
            driver.find_element(By.CSS_SELECTOR, selector_data_inicial).clear()
            driver.find_element(
                By.CSS_SELECTOR, selector_data_inicial).send_keys(data_inicio)

            selector_data_final = 'input#DtPeriodoFim'
            driver.find_element(By.CSS_SELECTOR, selector_data_final).clear()
            driver.find_element(
                By.CSS_SELECTOR, selector_data_final).send_keys(data_fim)

            selector_emissao_emitente = 'input#SaidaEmitente'
            selector_emissao_terceiros = 'input#SaidaDestinatario'
            selector_tipo_operacao = selector_emissao_emitente if tipo_operacao == TIPOS_OPERACAO[
                'emissao'] else selector_emissao_terceiros
            is_already_checked = driver.find_element(
                By.CSS_SELECTOR, selector_tipo_operacao).is_selected()
            if not is_already_checked:
                driver.find_element(
                    By.CSS_SELECTOR, selector_tipo_operacao).click()

            selector_checkbox_nfe_canceladas = 'input#NFeCancelada'
            is_already_checked = driver.find_element(
                By.CSS_SELECTOR, selector_checkbox_nfe_canceladas).is_selected()
            if not is_already_checked:
                driver.find_element(
                    By.CSS_SELECTOR, selector_checkbox_nfe_canceladas).click()

            selector_botam_consultar = 'input[onclick="preencheParametros();"]'
            driver.find_element(
                By.CSS_SELECTOR, selector_botam_consultar).click()

            try:
                selector_carregando = 'div#areaExtNfeProcessando'
                waitDisappear(driver, selector_carregando)
            except:
                raise Exception(
                    'SEFAZ - Não foi possivel localizar o elemento de carregamento')

            try:
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()

                print('SEFAZ - ALERT nenhum resultado encontrado no ano', ano)
                continue
            except:
                pass

            try:
                selector_tabela_resultados = '#aba_extrato_5 table.painel'
                waitCss(driver, selector_tabela_resultados)
                elemento_tabela = driver.find_element(
                    By.CSS_SELECTOR, selector_tabela_resultados)
            except:
                print('SEFAZ - nenhum resultado encontrado no ano', ano)
                continue

            dados_tabela = get_dict_list_from_driver_table_element(
                elemento_tabela)
            resultados[ano] = dados_tabela

        return get_resultados_formato_planilha(resultados, tipo_operacao, cnpj=cnpj)
    except Exception as e:
        raise Exception(
            f'SEFAZ: Erro ao tentar pegar extrato de notas do cnpj {cnpj} - {e}')


def get_resultados_formato_planilha(resultados: dict[str, list[dict[str, str]]], tipo_operacao, cnpj) -> dict[str, str | float]:
    resultados_formatados = {
        'descricao': ('FATURAMENTO' if tipo_operacao == TIPOS_OPERACAO['emissao'] else 'COMPRAS') + ' - ' + cnpj
    }

    for ano in resultados:

        for dado_mensal in resultados[ano]:
            if 'Mês Emit' not in dado_mensal or 'Total NF-e' not in dado_mensal:
                continue

            mes = dado_mensal['Mês Emit'].split('/')[0]
            mes = str(mes).zfill(2)

            resultados_formatados[f'{ano}-{mes}'] = float(dado_mensal['Total NF-e'].replace(
                '.', '').replace(',', '.')) if dado_mensal['Total NF-e'] else 0

    return resultados_formatados


def get_sefaz_extrato_notas(driver, anos: list, tipo_operacao) -> list[dict[str, dict[str, str | float]]]:
    cnpjs_urls = get_cnpjs_painel_contribuinte_urls(driver)

    resultados = []

    for cnpj in cnpjs_urls:
        cnpj_url = cnpjs_urls[cnpj]
        resultado = get_sefaz_extrato_notas_from_cnpj(
            driver, cnpj_url, anos, tipo_operacao, cnpj)
        resultados.append(resultado)

    return resultados


def test_webdriver():
    driver = get_driver_sefaz_logado()
    if driver:
        anos = [2022, 2023]
        compras = get_sefaz_extrato_notas(
            driver, anos, TIPOS_OPERACAO['recebimento'])
        faturamento = get_sefaz_extrato_notas(
            driver, anos, TIPOS_OPERACAO['emissao'])
        print('faturamento', faturamento)
        print('compras', compras)

        driver.close()

        return faturamento, compras

    return False, False


def test_create_planilha(faturamento: list[dict[str, dict[str, str | float]]], compras: list[dict[str, dict[str, str | float]]]):
    resultados_mesclados = faturamento + compras

    planilha_path = 'template.xlsx'

    planilha = Planilha(planilha_path)
    planilha.inserir_colunas_mes_aba_dados(1, 2022, 12, 2023)
    planilha.insert_dados_aba_dados(resultados_mesclados, False)
    planilha.inserir_soma_dados_na_apresentacao_por_regex(
        descricao_contains='FATURAMENTO - *', descricao_apresentacao='FATURAMENTO')
    planilha.inserir_soma_dados_na_apresentacao_por_regex(
        descricao_contains='COMPRAS - *', descricao_apresentacao='COMPRAS')
    planilha.ajustar_width_colunas_aba('Dados')

    planilha.save('output.xlsx')


if __name__ == '__main__':
    tipo_teste = input(
        'Tipo de teste:\n1 - Teste webdriver\n2 - Teste planilha\n3 - Teste completo\n')

    if tipo_teste == '1':
        test_webdriver()

    elif tipo_teste == '2':
        resultados_sefaz = {
            '2023': [
                {
                    'Mês Emit': '11',
                    'Total NF-e': '93.352,92'
                },
                {
                    'Mês Emit': '12',
                    'Total NF-e': '93.352,92'
                }
            ]
        }
        tipo_operacao_faturamento = TIPOS_OPERACAO['emissao']
        tipo_operacao_compras = TIPOS_OPERACAO['recebimento']

        cnpj1 = '12345678901234'
        cnpj2 = '12345678901235'

        faturamento_1 = get_resultados_formato_planilha(
            resultados_sefaz, tipo_operacao_faturamento, cnpj1)
        faturamento_2 = get_resultados_formato_planilha(
            resultados_sefaz, tipo_operacao_faturamento, cnpj2)
        compras_1 = get_resultados_formato_planilha(
            resultados_sefaz, tipo_operacao_compras, cnpj1)
        compras_2 = get_resultados_formato_planilha(
            resultados_sefaz, tipo_operacao_compras, cnpj2)

        print('faturamento', [faturamento_1, faturamento_2])
        print('compras', [compras_1, compras_2])

        test_create_planilha([faturamento_1, faturamento_2], [
                             compras_1, compras_2])

    elif tipo_teste == '3':
        faturamento, compras = test_webdriver()
        test_create_planilha(faturamento, compras)
