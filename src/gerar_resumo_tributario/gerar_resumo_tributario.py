import os
import re
from easygui import msgbox
from src.ecac.ecac import get_driver_ecac_logado
from src.ecac.pgdas.ecac_pgdas import get_pgdas, limpar_downloads_pgdas
from src.ecac.relacao_pgtos.ecac_relacao_pgtos import converter_relacao_pgtos_lista_planilha, ecac_get_relacao_pgtos
from src.esocial.contribuicaoFolha.contribuicaoFolha import get_contribuicao_folha
from src.esocial.esocial import get_driver_esocial_logado
from src.planilha.planilha import Planilha
from src.sefaz.compras.compras import get_compras_sefaz
from src.sefaz.faturamento.faturamento import get_faturamento_sefaz
from src.sefaz.sefaz import get_driver_sefaz_logado


def gerar_resumo_tributario(cnpj, anos, razao_social):
    driver = get_driver_ecac_logado()
    if not driver:
        msgbox('Erro ao tentar fazer login no ECAC')
        return False
    
    driver = get_driver_esocial_logado(driver)
    if not driver:
        msgbox('Erro ao tentar fazer login no eSocial')
        return False
    
    driver = get_driver_sefaz_logado(driver)
    if not driver:
        msgbox('Erro ao tentar fazer login no Sefaz')
        return False
    
    try:
        anos = sorted(anos, reverse=True)
        ano_final = anos[0]
        ano_inicial = anos[-1]
        
        data_inicial = f'01/01/{ano_inicial}'
        data_final = f'31/12/{ano_final}'
        
        ### SITES
        faturamento = get_faturamento_sefaz(driver=driver, cnpj=cnpj, anos=anos)
        compras = get_compras_sefaz(driver=driver, cnpj=cnpj, anos=anos)     
                
        relacao_pgtos, total_pgtos = ecac_get_relacao_pgtos(driver, data_inicial=data_inicial, data_final=data_final)
        relacao_pgtos_para_planilha = converter_relacao_pgtos_lista_planilha(relacao_pgtos)
        
        limpar_downloads_pgdas()
        das_para_planilha = get_pgdas(driver, anos)
        limpar_downloads_pgdas()
        
        contribuicao_folha = get_contribuicao_folha(driver, anos)    
        driver.quit()   
        
        ### PLANILHA
        template_path = 'template.xlsx'
        
        planilha = Planilha(template_path)
        planilha.set_CNPJ(cnpj)
        planilha.set_EMPRESA(razao_social)
        
        planilha.inserir_colunas_mes_aba_dados(1, int(ano_inicial), 12, int(ano_final))
        planilha.insert_dados_aba_dados(relacao_pgtos_para_planilha, True)
        planilha.insert_dados_aba_dados(das_para_planilha, True)
        
        planilha.insert_dados_aba_dados(contribuicao_folha['base_calculo'], False)
        planilha.inserir_valor_dado_na_apresentacao_pela_descricao('FOLHA (Total Período)', contribuicao_folha['base_calculo'][0]['descricao'])
        
        planilha.insert_dados_aba_dados(contribuicao_folha['valor_contribuicao'], True)
        
        planilha.insert_dados_aba_dados(faturamento, False)
        planilha.inserir_valor_dado_na_apresentacao_pela_descricao(faturamento[0]['descricao'], faturamento[0]['descricao'])
        planilha.insert_dados_aba_dados(compras, False)
        planilha.inserir_valor_dado_na_apresentacao_pela_descricao(compras[0]['descricao'], compras[0]['descricao'])
        
        planilha.ajustar_width_colunas_aba('Dados')
        
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        desktop_path = os.path.expanduser('~') + '\\Desktop'
        output_path = f'{desktop_path}\\{cnpj_numeros} resumo tributario {ano_inicial}_{ano_final}.xlsx'
        planilha.save(output_path)
                
        msgbox(f'Planilha gerada com sucesso em {output_path}')
        return output_path
        
    except Exception as e:
        print(e)
        print('Erro ao gerar resumo tributário:', e)
        msgbox('Erro ao gerar resumo tributário: '+ str(e))
        
    driver.quit()

if __name__ == '__main__':
    #46.540.315/0003-94
    #46.540.315/0006-37
    cnpj = '46.540.315/0003-94'
    razao_social = 'BAZAR TOTAL'
    anos = ['2024', '2023', '2022', '2021']
    
    gerar_resumo_tributario(cnpj, anos, razao_social)