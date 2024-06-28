import time
from src.esocial.esocial import get_driver_esocial_logado
from src.planilha.planilha import Planilha
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss
from selenium.webdriver.common.by import By


def get_contribuicao_folha(driver, anos: list) -> dict[str, list[dict[str, str | float]]]:
    url = 'https://www.esocial.gov.br/portal/Home/Inicial?tipoEmpregador=EMPREGADOR_GERAL'
    
    is_already_on_url = driver.current_url == url
    if not is_already_on_url:
        driver.get(url)
        
        
    selector_contribuicao_folha = 'a#menuContribuicaoPrevidenciariaEmpregador'
    waitCss(driver, selector_contribuicao_folha)
    element_link_contribuicao_folha = driver.find_element(By.CSS_SELECTOR, selector_contribuicao_folha)
    link_contribuicao_folha = element_link_contribuicao_folha.get_attribute('href')    
    
    base_calculo_planilha = {
        'descricao': 'Folha'
    }
    
    valor_contribuicao_planilha = {
        'descricao': 'INSS - Esocial'
    }
    
    anos_ordenados = sorted(anos, reverse=True)
    meses = range(12, 1, -1)
    
    ano_atual = time.localtime().tm_year
    mes_atual = time.localtime().tm_mon
    
    is_break_meses_anteriores_indisponiveis = False
    for ano in anos_ordenados:
        for mes in meses:
            if int(ano) == int(ano_atual) and int(mes) >= int(mes_atual):
                continue            
            
            mes = str(mes).zfill(2)
            competencia = f'{mes}/{ano}'
            
            driver.get(link_contribuicao_folha)
            
            selector_input_competencia = 'input#PeriodoApuracaoPesquisa'
            waitCss(driver, selector_input_competencia)
            driver.find_element(By.CSS_SELECTOR, selector_input_competencia).clear()
            driver.execute_script(f'document.querySelector("{selector_input_competencia}").value = "{competencia}"')
            
            selctor_button_submit = 'form button[onclick*="submit()"]'
            waitAndClick(driver, selctor_button_submit)            
            
            selector_aviso_erro = 'div.fade-alert.alert.alert-danger.retornoServidor'
            try:
                waitCss(driver, selector_aviso_erro, 3)
                print(f'Competência {competencia} indisponível')
                
                selector_span_aviso_erro = 'div.fade-alert.alert.alert-danger.retornoServidor span'
                element_span_aviso_erro = driver.find_element(By.CSS_SELECTOR, selector_span_aviso_erro)
                texto_aviso_erro = element_span_aviso_erro.text
                
                if 'deve ser superior ao mês/ano de início do empregador no eSocial.' in texto_aviso_erro:
                    is_break_meses_anteriores_indisponiveis = True
                    print(f'Meses anteriores a partir de {competencia} indisponíveis')
                    break
                                
                continue
            except:
                pass
            
            try:
                selector_tabela_resumo_linhas = 'td[data-col="Bases de Cálculo"] tbody tr'
                try:
                    waitCss(driver, selector_tabela_resumo_linhas, 5)                
                except:
                    print(f'Competência {competencia} sem dados')
                    continue
                
                
                elementos_linhas = driver.find_elements(By.CSS_SELECTOR, selector_tabela_resumo_linhas)
                
                base_calculo = None
                valor_contribuicao_descontado = None
                valor_contribuicao = None
                
                for elemento_linha in elementos_linhas:
                    quantidade_colunas = len(elemento_linha.find_elements(By.CSS_SELECTOR, 'td'))
                    
                    tem_mais_de_duas_colunas = quantidade_colunas >= 2
                    if not tem_mais_de_duas_colunas:
                        continue
                    
                    colunas = elemento_linha.find_elements(By.CSS_SELECTOR, 'td')
                    
                    is_primeira_coluna_base_calculo = colunas[0].get_attribute('data-col') == 'Bases de Cálculo'
                    if is_primeira_coluna_base_calculo:
                        ultima_coluna = colunas[-1]
                        base_calculo = ultima_coluna.text
                        continue

                    is_primeira_coluna_valor_contribuicao = colunas[0].get_attribute('data-col') == 'Contribuições do Segurado'
                    if is_primeira_coluna_valor_contribuicao:
                        valor_contribuicao_descontado = colunas[1].text
                        valor_contribuicao = colunas[2].text
                        continue
                
                
                print(f'Competência: {competencia}')
                print(f'Base de cálculo: {base_calculo}')
                print(f'Valor da contribuição descontado: {valor_contribuicao_descontado}')
                print(f'Valor da contribuição: {valor_contribuicao}\n\n')
                
                base_calculo_planilha[f'{ano}-{mes}'] = float(base_calculo.replace('.', '').replace(',', '.')) if base_calculo else 0
                valor_contribuicao_planilha[f'{ano}-{mes}'] = float(valor_contribuicao.replace('.', '').replace(',', '.')) if valor_contribuicao else 0
                
            except Exception as e:
                is_break_meses_anteriores_indisponiveis = True
                print(f'ESOCIAL - Ocorreu erro na {competencia}, os meses seguintes serão ignorados.\n O erro foi: '+ str(e))
                break

        if is_break_meses_anteriores_indisponiveis:
            break
        
    return {
        'base_calculo': [base_calculo_planilha],
        'valor_contribuicao': [valor_contribuicao_planilha]
    }


if __name__ == '__main__':    
    tipo_teste = input('Tipo de teste:\n1 - Teste webdriver\n2 - Teste planilha\n3 - Teste completo\n')
    
    if tipo_teste == '1':
        driver = get_driver_esocial_logado()
        if driver:
            anos = [2024]
            contribuicao_folha = get_contribuicao_folha(driver, anos)
            print(contribuicao_folha)
            
            driver.quit()
    elif tipo_teste == '2':
        contribuicao_folha = {
            'base_calculo': [{
                'descricao': 'Folha',
                '2022-01': 100.0,
                '2022-02': 200.0,
                '2022-03': 300.0,
                '2022-04': 400.0,
                '2022-05': 500.0,
                '2022-06': 600.0,
                '2022-07': 700.0,
            }],
            'valor_contribuicao': [{
                'descricao': 'INSS - Esocial',
                '2022-01': 10.0,
                '2022-02': 20.0,
                '2022-03': 30.0,
                '2022-04': 40.0,
                '2022-05': 50.0,
                '2022-06': 60.0,
                '2022-07': 70.0,
            }]
        }
        
        planilha_path = 'template.xlsx'
    
        planilha = Planilha(planilha_path)
        planilha.inserir_colunas_mes_aba_dados(1, 2019, 12, 2023)
        planilha.insert_dados_aba_dados(contribuicao_folha['base_calculo'], False)
        planilha.inserir_valor_dado_na_apresentacao_pela_descricao('FOLHA (Total Período)', contribuicao_folha['base_calculo'][0]['descricao'])
        
        planilha.insert_dados_aba_dados(contribuicao_folha['valor_contribuicao'], True)
        
        planilha.save('output.xlsx')
    elif tipo_teste == '3':
        driver = get_driver_esocial_logado()
        if driver:
            anos = [2024]
            contribuicao_folha = get_contribuicao_folha(driver, anos)
            
            planilha_path = 'template.xlsx'
            
            planilha = Planilha(planilha_path)
            planilha.inserir_colunas_mes_aba_dados(1, 2024, 12, 2024)
            planilha.insert_dados_aba_dados(contribuicao_folha['base_calculo'], False)
            planilha.inserir_valor_dado_na_apresentacao_pela_descricao('FOLHA (Total Período)', contribuicao_folha['base_calculo'][0]['descricao'])
            
            planilha.insert_dados_aba_dados(contribuicao_folha['valor_contribuicao'], True)
            
            planilha.save('output.xlsx')
            
    else:
        print('Tipo de teste inválido')
    
    