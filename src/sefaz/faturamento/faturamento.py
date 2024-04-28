
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from src.sefaz.extratosNotas.extratosNotas import TIPOS_OPERACAO, get_sefaz_extrato_notas
from src.sefaz.sefaz import get_driver_sefaz_logado, acessar_painel_usuario
from src.seleniumHelper.seleniumHelper import waitAndClick, waitAndSendKeys, waitCss

def get_faturamento_sefaz(driver, cnpj, anos: list):
    faturamento = get_sefaz_extrato_notas(driver, cnpj, anos, TIPOS_OPERACAO['emissao'])

if __name__ == '__main__':
    driver = get_driver_sefaz_logado()
    if driver:
        cnpj = '46.540.315/0003-94'        
        anos = [2019, 2020, 2021, 2022, 2023]
        faturamento = get_faturamento_sefaz(driver, cnpj, anos)
        print(faturamento)
        
        driver.close()