from src.ecac.ecac import get_driver_ecac_logado
from src.ecac.pgdas.ecac_pgdas import get_pgdas
from src.ecac.relacao_pgtos.ecac_relacao_pgtos import converter_relacao_pgtos_lista_planilha, ecac_get_relacao_pgtos
from src.esocial.contribuicaoFolha.contribuicaoFolha import get_contribuicao_folha
from src.esocial.esocial import get_driver_esocial_logado
from src.planilha.planilha import Planilha


def gerar_resumo_tributario(cnpj, anos):
    driver = get_driver_ecac_logado()
    driver = get_driver_esocial_logado(driver)

    ano_final = anos[0]
    ano_inicial = anos[-1]
    
    data_inicial = f'01/01/{ano_inicial}'
    data_final = f'31/12/{ano_final}'

    relacao_pgtos, total_pgtos = ecac_get_relacao_pgtos(driver, data_inicial=data_inicial, data_final=data_final)
    relacao_pgtos_para_planilha = converter_relacao_pgtos_lista_planilha(relacao_pgtos)
    
    das_para_planilha = get_pgdas(driver, anos)
    
    contribuicao_folha = get_contribuicao_folha(driver, anos)
    
    
    
    template_path = 'template.xlsx'
    
    planilha = Planilha(template_path)
    planilha.set_CNPJ(cnpj)
    planilha.set_EMPRESA('Empresa ABC LTDA') # TODO: desenvolver get_razao_social(cnpj)
    
    planilha.inserir_colunas_mes_aba_dados(1, int(ano_inicial), 12, int(ano_final))
    planilha.insert_dados_aba_dados(relacao_pgtos_para_planilha, True)
    planilha.insert_dados_aba_dados(das_para_planilha, True)
    
    planilha.insert_dados_aba_dados(contribuicao_folha['base_calculo'], False)
    planilha.inserir_valor_dado_na_apresentacao_pela_descricao('FOLHA (Total Período)', 'Folha')
    
    planilha.insert_dados_aba_dados(contribuicao_folha['valor_contribuicao'], True)
    
    planilha.save('output.xlsx')

if __name__ == '__main__':
    cnpj = '46.540.315/0001-22'
    anos = ['2023', '2022', '2021']
    
    gerar_resumo_tributario(cnpj, anos)