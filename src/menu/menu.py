import os
import re
from easygui import buttonbox, msgbox, fileopenbox

from src.gerar_resumo_tributario.gerar_resumo_tributario import gerar_resumo_tributario
from src.menu.inputs_usuario import get_anos, get_cnpj, get_razao_social
from src.menu.pre_run import pre_run
import pandas

def main():
    pre_run()
    
    um_ou_varios_cnpj = buttonbox(
        'Você deseja gerar o resumo tributário de UM CNPJ ou de VÁRIOS CNPJs?',
        'Resumo tributário',
        ['🟢   Apenas 1 CNPJ', '🟦    Vários CNPJs']        
    )
    
    if um_ou_varios_cnpj == '🟢   Apenas 1 CNPJ':
        cnpj = get_cnpj()        
        razao_social = get_razao_social()
        anos = get_anos()
        
        gerar_resumo_tributario(cnpj, anos, razao_social)
    else:
        ja_esta_com_a_planilha = buttonbox(
            'Você já tem o arquivo Excel com os CNPJs e razões sociais ou precisa do template?',
            'Resumo tributário',
            ['Já possuo o Excel com os CNPJs Preenchidos', 'Preciso de um template']
        )
        
        if ja_esta_com_a_planilha == 'Preciso de um template':
            path_template = 'template_lista_cnpj.xlsx'
            
            desktop_path = os.path.expanduser('~') + '\\Desktop'
            template_desktop_path = f'{desktop_path}\\template_lista_cnpj.xlsx'
            
            os.system(f'copy "{path_template}" "{template_desktop_path}"')
            
            msgbox(f'Template gerado com sucesso em {template_desktop_path}')

            exit(0)
        else:
            msgbox('Selecione o arquivo Excel com os CNPJs e razões sociais')
            
            arquivo_com_cnpjs = fileopenbox('Selecione o arquivo Excel com os CNPJs e razões sociais', 'Escolha o arquivo Excel', '*.xlsx')

            try:
                anos = get_anos()
                
                workbook = pandas.read_excel(arquivo_com_cnpjs, usecols=['CNPJ', 'RAZAO SOCIAL'])

                for index, row in workbook.iterrows():
                    cnpj = row['CNPJ']
                    razao_social = row['RAZAO SOCIAL']
                    
                    
                    is_valid_cnpj = re.match(r'\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}', cnpj) #or re.match(r'\d{14}', cnpj)
                    if not is_valid_cnpj:
                        cnpj_so_numeros = re.sub(r'\D', '', cnpj)
                        is_valid_cnpj_so_numeros = len(cnpj_so_numeros) == 14
                        if not is_valid_cnpj_so_numeros:
                            msgbox(f'CNPJ inválido: {cnpj}')
                            continue
                        
                        cnpj = f'{cnpj_so_numeros[:2]}.{cnpj_so_numeros[2:5]}.{cnpj_so_numeros[5:8]}/{cnpj_so_numeros[8:12]}-{cnpj_so_numeros[12:]}'

                    gerar_resumo_tributario(cnpj, anos, razao_social)
                
            except Exception as e:
                msgbox(f'Erro ao ler o arquivo Excel: {e}')
                exit(1)

if __name__ == '__main__':
    main()

    exit(0)