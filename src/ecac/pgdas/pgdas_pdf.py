
import re
from pdfquery import PDFQuery

def get_periodo_apuracao(text: str) -> str:
    periodo_apuracao = re.search(r'Período de Apuração: (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})', text)
    periodo_apuracao = periodo_apuracao.group(1) if periodo_apuracao else None
    if periodo_apuracao:
        periodo_apuracao = periodo_apuracao[3:]
    
    return periodo_apuracao

def get_numero_declaracao(text: str) -> str:
    numero_declaracao = re.search(r'Competência\n(\d*)', text)
    numero_declaracao = numero_declaracao.group(1) if numero_declaracao else None
    return numero_declaracao

def get_receitas(text: str) -> tuple:
    receita_sem_st = 0
    receita_com_st = 0
    
    receitas = re.findall(r"Valor do Débito por Tributo para a Atividade [\D\n]*?Receita Bruta Informada: R\$ \d{1,3}\.?\d{1,3},\d{2}", text)
    if receitas:
        for receita in receitas:
            valor_receita = re.findall(r"Receita Bruta Informada: R\$ (\d{1,3}\.?\d{1,3},\d{2})", receita)
            if not valor_receita:
                continue
            
            valor_receita = valor_receita[0]
            
            if 'Sem substituição tributária' in receita and receita_sem_st == 0:
                receita_sem_st += float(valor_receita.replace('.', '').replace(',', '.'))
            elif 'Com substituição tributária' in receita and receita_com_st == 0:
                receita_com_st += float(valor_receita.replace('.', '').replace(',', '.'))
        
    return receita_sem_st, receita_com_st

def get_dados_pdf(pdf_path: str, is_salvar_em_arquivo_de_texto: bool = False) -> dict:
    if not pdf_path.endswith('.pdf'):
        raise Exception('O arquivo precisa ser um arquivo PDF')
    
    pdf = PDFQuery(pdf_path)
    pdf.load()
    
    full_text = pdf.pq('LTPage').text()
    
    #text_elements = pdf.pq('LTTextLineHorizontal')
    #text = [t.text for t in text_elements].join('\n')
    text = full_text
    
    if is_salvar_em_arquivo_de_texto:
        with open(pdf_path + '.txt', 'w') as f:
            f.write(text)
    
    periodo_apuracao = get_periodo_apuracao(text)
    numero_declaracao = get_numero_declaracao(text)
    receita_sem_st, receita_com_st = get_receitas(text)

    dados = {
        'periodo_apuracao': periodo_apuracao,
        'numero_declaracao': numero_declaracao,
        'receita_sem_st': receita_sem_st,
        'receita_com_st': receita_com_st
    }
    print(dados)
    
    return dados