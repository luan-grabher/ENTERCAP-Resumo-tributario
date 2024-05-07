import xlsxwriter
import openpyxl

def get_number_for_letter(letter):
    normalized_letter = letter.upper()
    return ord(normalized_letter) - 64

class Planilha:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.workbook = xlsxwriter.Workbook(self.arquivo)

        
    def set_CNPJ(self, cnpj):
        aba = self.workbook.get_worksheet_by_name('Apresentação')
        if aba is None:
            return False
        
        aba.write('D7', 'CNPJ: ' + cnpj)
        
    def save(self):
        self.workbook.close()

if __name__ == '__main__':
    planilha_path = 'template.xlsx'
    
    planilha = openpyxl.load_workbook(planilha_path)
    
    planilha['Apresentação']['D7'] = 'CNPJ: 12345678901234'
    planilha['Apresentação']['B7'] = 'EMPRESA: Teste'
    
    planilha.save('output.xlsx')