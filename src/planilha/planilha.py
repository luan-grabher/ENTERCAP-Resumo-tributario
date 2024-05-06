import xlsxwriter

def get_number_for_letter(letter):
    normalized_letter = letter.upper()
    return ord(normalized_letter) - 64

class Planilha:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.workbook = xlsxwriter.Workbook(self.arquivo)

if __name__ == '__main__':
    planilha = Planilha('template_apresentacao.xlsx')
    
    print(planilha.workbook)