import time
from src.esocial.esocial import get_driver_esocial_logado


def get_contribuicao_folha(driver):
    url = 'https://www.esocial.gov.br/portal/Home/Inicial?tipoEmpregador=EMPREGADOR_GERAL'
    
    driver.get(url)
    
    time.sleep(10)
    pass

if __name__ == '__main__':
    driver = get_driver_esocial_logado()
    if driver:
        contribuicao_folha = get_contribuicao_folha(driver)
        print(contribuicao_folha)
        
        driver.close()