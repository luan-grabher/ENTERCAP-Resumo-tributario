from easygui import buttonbox, choicebox, msgbox

from src.menu.pre_run import pre_run
from src.sefaz.faturamento.faturamento import get_faturamento_sefaz
from src.sefaz.sefaz import get_driver_sefaz_logado

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
            driver = get_driver_sefaz_logado()
            if driver:
                cnpj = '46.540.315/0003-94'        
                anos = [2019, 2020, 2021, 2022, 2023]
                faturamento = get_faturamento_sefaz(driver, cnpj, anos)
                
                driver.close()
        else:
            msgbox('Nenhuma opção selecionada')
                        
        is_sair_do_programa = buttonbox('Deseja realizar outra operação?', 'Sair do programa', ['Sim', 'Não']) == 'Não'


if __name__ == '__main__':
    main()

    exit(0)