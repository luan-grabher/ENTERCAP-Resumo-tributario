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
from src.sefaz.contaCorrenteFiscal.contaCorrenteFiscal import get_conta_corrente_fiscal
from src.sefaz.faturamento.faturamento import get_faturamento_sefaz
from src.sefaz.sefaz import get_driver_sefaz_logado


def create_planilha(cnpj, razao_social, faturamento, compras, relacao_pgtos_para_planilha, das_para_planilha, contribuicao_folha, ano_inicial, ano_final, conta_corrente_fiscal, is_test=False):
    template_path = 'template.xlsx'

    planilha = Planilha(template_path)
    planilha.set_CNPJ(cnpj)
    planilha.set_EMPRESA(razao_social)

    dados_para_inserir_com_aba_apresentacao = relacao_pgtos_para_planilha + \
        [das_para_planilha[2]] + contribuicao_folha['valor_contribuicao']
    dados_para_inserir_somente_aba_dados = faturamento + \
        compras + contribuicao_folha['base_calculo'] + conta_corrente_fiscal + [das_para_planilha[0], das_para_planilha[1]]

    planilha.inserir_colunas_mes_aba_dados(
        1, int(ano_inicial), 12, int(ano_final))

    planilha.insert_dados_aba_dados(
        dados_para_inserir_com_aba_apresentacao, True)
    planilha.insert_dados_aba_dados(
        dados_para_inserir_somente_aba_dados, False)

    planilha.inserir_valor_dado_na_apresentacao_pela_descricao(
        'FOLHA (Total Período)', contribuicao_folha['base_calculo'][0]['descricao'])
    planilha.inserir_valor_dado_na_apresentacao_pela_descricao(
        'Receita sem ST', das_para_planilha[0]['descricao'])
    planilha.inserir_valor_dado_na_apresentacao_pela_descricao(
        'Receita com ST', das_para_planilha[1]['descricao'])

    planilha.inserir_soma_dados_na_apresentacao_por_regex(
        descricao_contains='FATURAMENTO', descricao_apresentacao='FATURAMENTO')
    planilha.inserir_soma_dados_na_apresentacao_por_regex(
        descricao_contains='COMPRAS', descricao_apresentacao='COMPRAS')
    
    
    planilha.inserir_soma_dados_na_apresentacao_por_regex(
        descricao_contains='ICMS Mensal',
        descricao_apresentacao='ICMS Mensal'
    )    
    
    planilha.inserir_soma_dados_na_apresentacao_por_regex_acima_de_X(
        descricao_contains='ICMS DIF AL',
        descricao_apresentacao='ICMS DIF AL',
        descricao_x='MARGENS DE LUCRO E CUSTO'
    )
    
    planilha.inserir_soma_dados_na_apresentacao_por_regex_acima_de_X(
        descricao_contains='ICMS - Fundo Combate a Pobresa',
        descricao_apresentacao='ICMS FCP',
        descricao_x='MARGENS DE LUCRO E CUSTO'
    )        
    planilha.inserir_soma_dados_na_apresentacao_por_regex_acima_de_X(
        descricao_contains='GIA Mensal',
        descricao_apresentacao='ICMS - Saldo Credor',
        descricao_x='MARGENS DE LUCRO E CUSTO'
    )

    if is_test:
        output_path = 'output.xlsx'
    else:
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        desktop_path = os.path.expanduser('~') + '\\Desktop'
        output_path = f'{desktop_path}\\{cnpj_numeros} resumo tributario {
            ano_inicial}_{ano_final}.xlsx'
        
        
    planilha.save(output_path)

    return output_path


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

        # SITES
        faturamento = get_faturamento_sefaz(driver=driver, anos=anos)
        compras = get_compras_sefaz(driver=driver, anos=anos)
        conta_corrente_fiscal = get_conta_corrente_fiscal(driver, anos)

        relacao_pgtos, total_pgtos = ecac_get_relacao_pgtos(
            driver, data_inicial=data_inicial, data_final=data_final)
        relacao_pgtos_para_planilha = converter_relacao_pgtos_lista_planilha(
            relacao_pgtos)

        limpar_downloads_pgdas()
        das_para_planilha = get_pgdas(driver, anos)
        limpar_downloads_pgdas()

        contribuicao_folha = get_contribuicao_folha(driver, anos)
        driver.quit()

        # PLANILHA
        output_path = create_planilha(cnpj, razao_social, faturamento, compras, relacao_pgtos_para_planilha,
                                      das_para_planilha, contribuicao_folha, ano_inicial, ano_final, conta_corrente_fiscal)

        msgbox(f'Planilha gerada com sucesso em {output_path}')
        return output_path

    except Exception as e:
        print(e)
        print('Erro ao gerar resumo tributário:', e)
        msgbox('Erro ao gerar resumo tributário: ' + str(e))

    driver.quit()


if __name__ == '__main__':
    tipo_teste = input(
        'Tipo de teste:\n1 - Teste completo\n2 - Teste Create Planilha\n')

    if tipo_teste == '1':
        # 46.540.315/0003-94
        # 46.540.315/0006-37
        cnpj = '46.540.315/0003-94'
        razao_social = 'BAZAR TOTAL'
        anos = ['2024', '2023', '2022', '2021', '2020', '2019']

        gerar_resumo_tributario(cnpj, anos, razao_social)

    elif tipo_teste == '2':
        cnpj = '46.540.315/0003-94'
        razao_social = 'BAZAR TOTAL'
        
        faturamento = [
            {
                'descricao': 'FATURAMENTO - 12345678901234', '2023-11': 93352.92, '2023-12': 93352.92
            },
            {
                'descricao': 'FATURAMENTO - 12345678901235',
                '2023-11': 93352.92,
                '2023-12': 93352.92
            }
        ]
        compras = [
                {'descricao': 'COMPRAS - 12345678901234', '2023-11': 10000.92, '2023-12': 20000.92},
                {'descricao': 'COMPRAS - 12345678901235', '2023-11': 17000.92, '2023-12': 15000.92}
        ]
        relacao_pgtos_para_planilha = [
            {'descricao': '0211 - IRPF - Carnê-Leão', '2023-03': 100.0, '2023-04': 200.0},
            {'descricao': '1410 - INSS', '2023-03': 123.0, '2023-04': 456.0},
        ]
        das_para_planilha = [
            {
                'descricao': 'Receita sem ST',
                '2022-11': 100.0,
                '2022-12': 200.0,
            },
            {
                'descricao': 'Receita com ST',
                '2022-11': 100.0,
                '2022-12': 400.0,
            },
            {
                'descricao': 'Simples Nacional',
                '2022-11': 100.0,
                '2022-12': 200.0,
            }
        ]
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
        
        conta_corrente_fiscal = [
            {
                'descricao': 'ICMS DIF AL - 46.540.315/0003-94', '2023-11': 0.0, '2023-12': 0.0, '2024-01': 0.0, '2024-02': 0.0, '2024-03': 0.0
            },
            {
                'descricao': 'ICMS Mensal - 46.540.315/0003-94', '2024-03': 10674.46, '2023-01': 1000.0, '2023-02': 2000.0, '2023-03': 3000.0, '2023-04': 4000.0,
            },
            {
                'descricao': 'ICMS - Fundo Combate a Pobresa - 46.540.315/0003-94', '2023-01': 1000.0, '2023-02': 2000.0, '2023-03': 3000.0, '2023-04': 4000.0,
            },
            {
                'descricao': 'GIA Mensal - 46.540.315/0003-94', '2023-01': 1000.0, '2023-02': 2000.0, '2023-03': 3000.0, '2023-04': 4000.0,
            },
            {
                'descricao': 'ICMS DIF AL - 46.540.315/0006-37', '2023-12': 0.0, '2024-01': 0.0, '2024-02': 0.0, '2024-03': 0.0
            },
            {
                'descricao': 'ICMS Mensal - 46.540.315/0006-37'
            },
            {
                'descricao': 'ICMS - Fundo Combate a Pobresa - 46.540.315/0006-37'
            },
            {
                'descricao': 'GIA Mensal - 46.540.315/0006-37'
            }
        ]

        ano_inicial = '2022'
        ano_final = '2024'

        create_planilha(cnpj, razao_social, faturamento, compras, relacao_pgtos_para_planilha,
                        das_para_planilha, contribuicao_folha, ano_inicial, ano_final, conta_corrente_fiscal, is_test=True)
