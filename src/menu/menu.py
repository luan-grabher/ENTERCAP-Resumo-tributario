from easygui import buttonbox, choicebox, msgbox

from src.gerar_resumo_tributario.gerar_resumo_tributario import gerar_resumo_tributario
from src.menu.inputs_usuario import get_anos, get_cnpj, get_razao_social
from src.menu.pre_run import pre_run

MENU = {
    'gerar_resumo_tributario': '📄 Gerar Planilha Excel Resumo tributário',
    'sair': '🚪 Sair do programa'
}

def main():
    pre_run()    
    
    msg = 'Selecione uma opção:'
    title = 'Resumo Tributário Menu'
    
    is_sair_do_programa = False
    while not is_sair_do_programa:
        try:
            opcoes_disponiveis_list = list(MENU.values())
            opcao_escolhida = choicebox(msg, title, opcoes_disponiveis_list)
            
            
            if opcao_escolhida == MENU['gerar_resumo_tributario']:
                cnpj = get_cnpj()
                anos = get_anos()
                razao_social = get_razao_social()
                                
                gerar_resumo_tributario(cnpj, anos, razao_social)
                
            elif opcao_escolhida == MENU['sair']:
                break
            else:
                msgbox('Nenhuma opção selecionada')
                            
            is_sair_do_programa = buttonbox('Deseja realizar outra operação?', 'Sair do programa', ['Sim', 'Não']) == 'Não'
            if is_sair_do_programa:
                break
        except Exception as e:
            msgbox(f'Erro: {e}')
            break


if __name__ == '__main__':
    main()

    exit(0)