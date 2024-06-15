
from src.planilha.planilha import Planilha
from src.sefaz.extratosNotas.extratosNotas import TIPOS_OPERACAO, get_sefaz_extrato_notas
from src.sefaz.sefaz import get_driver_sefaz_logado

def get_faturamento_sefaz(driver, anos: list):
    faturamento = get_sefaz_extrato_notas(driver, anos, TIPOS_OPERACAO['emissao'])
    
    return [faturamento]

if __name__ == '__main__':
    tipo_teste = input('Tipo de teste:\n1 - Teste webdriver\n2 - Teste planilha\n3 - Teste completo\n')
    
    if tipo_teste == '1':    
        driver = get_driver_sefaz_logado()
        if driver:
            cnpj = '46.540.315/0003-94'        
            anos = ['2023', '2022', '2021']
            faturamento = get_faturamento_sefaz(driver, cnpj, anos)
            print(faturamento)
            
            driver.close()
    elif tipo_teste == '2':
        pass
    elif tipo_teste == '3':
        driver = get_driver_sefaz_logado()
        if driver:
            cnpj = '46.540.315/0003-94'        
            anos = ['2023', '2022', '2021']
            faturamento = get_faturamento_sefaz(driver, cnpj, anos)
            print('faturamento', faturamento)
            
            driver.close()
            
            template_path = 'template.xlsx'
        
            planilha = Planilha(template_path)
            planilha.set_CNPJ(cnpj)
            
            planilha.inserir_colunas_mes_aba_dados(1, 2021, 12, 2023)
            planilha.insert_dados_aba_dados(faturamento, False)
            planilha.inserir_valor_dado_na_apresentacao_pela_descricao(faturamento[0]['descricao'], faturamento[0]['descricao'])
            
            planilha.ajustar_width_colunas_aba('Dados')
            planilha.save('output.xlsx')