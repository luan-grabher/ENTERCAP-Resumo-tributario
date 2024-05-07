import openpyxl

def get_number_for_letter(letter):
    normalized_letter = letter.upper()
    return ord(normalized_letter) - 64

class Planilha:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.workbook = openpyxl.load_workbook(arquivo)

        
    def set_CNPJ(self, cnpj):
        self.workbook['Apresentação']['C7'] = 'CNPJ: ' + cnpj
        
    def set_EMPRESA(self, empresa):
        self.workbook['Apresentação']['B7'] = 'EMPRESA: ' + empresa
        
    def save(self, output_path = 'output.xlsx'):
        self.workbook.save(output_path)

if __name__ == '__main__':
    planilha_path = 'template.xlsx'
    
    planilha = Planilha(planilha_path)
    planilha.set_CNPJ('123456789')
    planilha.set_EMPRESA('Empresa ABC')
    
    planilha.save('output.xlsx')