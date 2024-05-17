import re
import time
from easygui import msgbox, textbox, multchoicebox

def get_cnpj():
    msg = 'Digite o CNPJ da empresa:'
    title = 'Resumo Tributário Menu'
    cnpj = textbox(msg, title)
    
    is_valid_cnpj = re.match(r'\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}', cnpj) or re.match(r'\d{14}', cnpj)
    if not is_valid_cnpj:
        raise ValueError('CNPJ inválido')
    
    return cnpj

def get_anos():
    ano_atual = time.localtime().tm_year
    
    ultimos_5_anos_sem_contar_o_ano_atual = [ano for ano in range(ano_atual, ano_atual - 6, -1)]
    
    mensagem = 'Escolha os anos clicando neles:\nVocê também pode clicar em "Select All" para selecionar todos os anos disponiveis'
    anos_escolhidos = multchoicebox(mensagem, 'Resumo Tributário Menu', ultimos_5_anos_sem_contar_o_ano_atual, ultimos_5_anos_sem_contar_o_ano_atual)
    if not anos_escolhidos:
        raise ValueError('Você deve selecionar pelo menos um ano')
    
    return anos_escolhidos

if __name__ == '__main__':
    tipo_teste = input('Tipo de teste:\n1 - Teste de CNPJ\n2 - Teste de Anos\n')
    
    if tipo_teste == '1':    
        cnpj = get_cnpj()
        msgbox(f'CNPJ digitado: {cnpj}')
    elif tipo_teste == '2':
        anos = get_anos()
        msgbox(f'Anos escolhidos: {anos}')
    else:
        msgbox('Nenhuma opção selecionada')