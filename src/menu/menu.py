from easygui import buttonbox, choicebox, msgbox

from src.ecac.ecac import get_driver_ecac_logado
from src.ecac.relacao_pgtos.ecac_relacao_pgtos import ecac_get_relacao_pgtos
from src.menu.pre_run import pre_run

MENU = {
    'teste': '🎮 Realizar um teste',
    'sair': '🚪 Sair do programa'
}

def main():
    pre_run()    
    
    msg = 'Selecione uma opção:'
    title = 'Resumo Tributário Menu'
    
    is_sair_do_programa = False
    while not is_sair_do_programa:
        opcoes_disponiveis_list = list(MENU.values())
        opcao_escolhida = choicebox(msg, title, opcoes_disponiveis_list)
        
        
        if opcao_escolhida == MENU['teste']:
            driver = get_driver_ecac_logado()
            ecac_get_relacao_pgtos(driver=driver, data_inicial='01/03/2019', data_final='31/03/2023')
        else:
            msgbox('Nenhuma opção selecionada')
                        
        is_sair_do_programa = buttonbox('Deseja realizar outra operação?', 'Sair do programa', ['Sim', 'Não']) == 'Não'


if __name__ == '__main__':
    main()

    exit(0)