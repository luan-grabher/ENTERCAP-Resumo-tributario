
from src.sefaz.extratosNotas.extratosNotas import TIPOS_OPERACAO, get_sefaz_extrato_notas
from src.sefaz.sefaz import get_driver_sefaz_logado

def get_compras_sefaz(driver, anos: list):
    compras = get_sefaz_extrato_notas(driver, anos, TIPOS_OPERACAO['recebimento'])
    
    return compras

if __name__ == '__main__':
    driver = get_driver_sefaz_logado()
    if driver:      
        anos = [2019, 2020, 2021, 2022, 2023]
        compras = get_compras_sefaz(driver, anos)
        print(compras)
        
        driver.close()