
from src.sefaz.extratosNotas.extratosNotas import TIPOS_OPERACAO, get_sefaz_extrato_notas
from src.sefaz.sefaz import get_driver_sefaz_logado

def get_faturamento_sefaz(driver, cnpj, anos: list):
    faturamento = get_sefaz_extrato_notas(driver, cnpj, anos, TIPOS_OPERACAO['emissao'])
    
    return faturamento

if __name__ == '__main__':
    driver = get_driver_sefaz_logado()
    if driver:
        cnpj = '46.540.315/0003-94'        
        anos = [2019, 2020, 2021, 2022, 2023]
        faturamento = get_faturamento_sefaz(driver, cnpj, anos)
        print(faturamento)
        
        driver.close()