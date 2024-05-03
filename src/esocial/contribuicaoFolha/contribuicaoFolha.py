from src.esocial.esocial import get_driver_esocial_logado
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss
from selenium.webdriver.common.by import By


def get_contribuicao_folha(driver, anos: list):
    url = 'https://www.esocial.gov.br/portal/Home/Inicial?tipoEmpregador=EMPREGADOR_GERAL'
    
    is_already_on_url = driver.current_url == url
    if not is_already_on_url:
        driver.get(url)
        
        
    selector_contribuicao_folha = 'a#menuContribuicaoPrevidenciariaEmpregador'
    waitCss(driver, selector_contribuicao_folha)
    element_link_contribuicao_folha = driver.find_element(By.CSS_SELECTOR, selector_contribuicao_folha)
    link_contribuicao_folha = element_link_contribuicao_folha.get_attribute('href')    
    
    contribuicao_folha = {}
    
    meses = range(1, 13)    
    for ano in anos:
        for mes in meses:
            mes = str(mes).zfill(2)
            competencia = f'{mes}{ano}'
            
            driver.get(link_contribuicao_folha)
            
            selector_input_competencia = 'input#PeriodoApuracaoPesquisa'
            waitAndSendKeys(driver, selector_input_competencia, competencia)
            
            selctor_button_submit = 'form button[onclick*="submit()"]'
            waitAndClick(driver, selctor_button_submit)
            
            selector_avisp_erro = 'div.fade-alert.alert.alert-danger.retornoServidor'
            try:
                waitCss(driver, selector_avisp_erro, 3)
                print(f'Competência {competencia} indisponível')
                continue
            except:
                pass
            
            
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
            
            contribuicao_folha[competencia] = {
                'base_calculo': base_calculo,
                'valor_contribuicao': valor_contribuicao,
                'valor_contribuicao_descontado': valor_contribuicao_descontado
            }
        
    
    return contribuicao_folha

if __name__ == '__main__':
    driver = get_driver_esocial_logado()
    if driver:
        anos = [2022, 2023]
        contribuicao_folha = get_contribuicao_folha(driver, anos)
        print(contribuicao_folha)
        
        driver.quit()