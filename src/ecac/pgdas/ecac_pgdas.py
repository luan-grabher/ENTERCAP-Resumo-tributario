import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
from tqdm import tqdm

from src.ecac.ecac import get_driver_ecac_logado
from src.ecac.pgdas.pgdas_pdf import get_dados_pdf


filtro_arquivo_download_regex = "PGDASD-.*\\.pdf"

def get_pgdas(driver, anos: list):
    baixar_pgdas(driver, anos)
    
    return get_dados_dos_arquivos_downloads()

def get_quantidade_downloads():
    user_download_path = os.path.expanduser('~') + '\\Downloads'
    downloads = os.listdir(user_download_path)
    quantidade_arquivos = 0
    for download in downloads:
        if re.match(filtro_arquivo_download_regex, download):
            quantidade_arquivos += 1
    return quantidade_arquivos

def baixar_pgdas(driver, anos: list):
    url = 'https://sinac.cav.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgdasd2018.app/Consulta'        
    driver.get(url)
    
    url_captcha = "/Captcha"
    while True:
        time.sleep(1)
        if url_captcha not in driver.current_url:
            break
        
    if url not in driver.current_url:
        driver.get(url)
    
    quantidade_arquivos_antes = get_quantidade_downloads()
    
    selector_input_ano = 'form input#ano'
    selector_button_submit = 'form button[type=submit]'
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_input_ano)))
    
    selector_botoes_download_pdf = "a[data-content='Imprimir Declaração']"
    for ano in anos:
        driver.find_element(By.CSS_SELECTOR, selector_input_ano).send_keys(ano)
        driver.find_element(By.CSS_SELECTOR, selector_button_submit).click()
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_botoes_download_pdf)))
        except:
            continue
        
        botoes_dowload = driver.find_elements(By.CSS_SELECTOR, selector_botoes_download_pdf)
        for botao in botoes_dowload:
            botao.click()

        tentativas_maximas = 30
        tentativas = 0
        while True:
            tentativas += 1
            
            quantidade_arquivos_depois = get_quantidade_downloads()
            if quantidade_arquivos_depois == quantidade_arquivos_antes + len(botoes_dowload):
                break
            
            if tentativas > tentativas_maximas:
                break
        
            time.sleep(1)
    
    return True

def get_dados_dos_arquivos_downloads(is_salvar_em_arquivo_de_texto=False):
    user_download_path = os.path.expanduser('~') + '\\Downloads'
    downloads = os.listdir(user_download_path)
    dados = {}
    for download in tqdm(downloads, desc='Extraindo dados dos arquivos PDF'):
        if re.match(filtro_arquivo_download_regex, download) and download.endswith('.pdf'):
            pdf_path = user_download_path + '\\' + download
            try:
                dados[download] = get_dados_pdf(pdf_path, is_salvar_em_arquivo_de_texto=is_salvar_em_arquivo_de_texto)                
            except Exception as e:
                print('Erro ao tentar extrair dados do arquivo ' + pdf_path)
                print(e)
                
    dados_sem_duplicados = {}
    for nome_arquivo, dado in dados.items():
        if dado['periodo_apuracao'] not in dados_sem_duplicados:
            dados_sem_duplicados[dado['periodo_apuracao']] = dado
            continue
        
        if dado['periodo_apuracao'] in dados_sem_duplicados:
            is_mais_recente = dado['numero_declaracao'] > dados_sem_duplicados[dado['periodo_apuracao']]['numero_declaracao']
            if is_mais_recente:
                print('Dado mais recente encontrado para o período de apuração ' + dado['periodo_apuracao'])
                dados_sem_duplicados[dado['periodo_apuracao']] = dado
    
    return dados_sem_duplicados

def limpar_downloads_pgdas():
    user_download_path = os.path.expanduser('~') + '\\Downloads'
    downloads = os.listdir(user_download_path)
    for download in downloads:
        if re.match(filtro_arquivo_download_regex, download):
            os.remove(user_download_path + '\\' + download)
    return True

if __name__ == '__main__':
    tipo_teste = input('Tipo de teste:\n1 - Teste de download\n2 - Teste de extração de dados:\n')
    
    if tipo_teste == '1':    
        driver = get_driver_ecac_logado()
        if not driver:
            exit(1)
    
        get_pgdas(driver=driver, anos=[2019, 2020, 2021, 2022, 2023])
        driver.close()
        
    else:
        dados = get_dados_dos_arquivos_downloads(is_salvar_em_arquivo_de_texto=False)
    
    print('Fim do programa')
    
    exit(0)