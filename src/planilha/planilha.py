import openpyxl

def get_number_for_letter(letter):
    normalized_letter = letter.upper()
    return ord(normalized_letter) - 64

mesesstr = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
mesesInt = {mes: i + 1 for i, mes in enumerate(mesesstr)}
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
    
    def inserir_colunas_mes_aba_dados(self, mesInicio: int, anoInicio: int, mesFim: int, anoFim: int):
        aba_dados = self.workbook['Dados']
        
        coluna_inicio = get_number_for_letter('B')        
        
        for ano in range(anoInicio, anoFim + 1):
            for mes in range(mesInicio, mesFim + 1):
                coluna = coluna_inicio + (ano - anoInicio) * 12 + mes - mesInicio
                aba_dados.insert_cols(coluna)
                
                messtr = mesesstr[mes - 1]
                aba_dados.cell(row=1, column=coluna, value=f'{messtr}/{ano}')
                
        coluna_total = coluna + 1
        aba_dados.insert_cols(coluna_total)
        aba_dados.cell(row=1, column=coluna_total, value='Total')
        
        self.ajustar_width_colunas_aba('Dados')
                
    
    def ajustar_width_colunas_aba(self, nome_aba):
        aba = self.workbook[nome_aba]
        
        for col in aba.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            aba.column_dimensions[column].width = adjusted_width

    def insert_dados_aba_dados(self, lista_de_dados: list[dict[str, str | float]]):   
        aba_dados = self.workbook['Dados']
        
        ultima_linha_preenchida = aba_dados.max_row
        
        linha = ultima_linha_preenchida
        for dado in lista_de_dados:
            linha += 1
            
            aba_dados.cell(row=linha, column=1, value=dado['descricao'])
            
            ultima_coluna = aba_dados.max_column
            
            for coluna in range(2, ultima_coluna + 1):
                header = aba_dados.cell(row=1, column=coluna).value
                is_coluna_total = header == 'Total'
                if is_coluna_total:
                    formula_sum = f'=SUM({openpyxl.utils.get_column_letter(2)}{linha}:{openpyxl.utils.get_column_letter(ultima_coluna - 1)}{linha})'
                    aba_dados.cell(row=linha, column=coluna, value=formula_sum)
                    break
                
                mes, ano = header.split('/')
                mes = mesesInt[mes]
                    
                mes_MM = str(mes).zfill(2)
                valor_mes = dado[f'{ano}-{mes_MM}'] if f'{ano}-{mes_MM}' in dado else None
                aba_dados.cell(row=linha, column=coluna, value=valor_mes)
                               
    def get_linha_tributos_sobre_vendas(self):
        aba_apresentacao = self.workbook['Apresentação']
        
        linha_TRIBUTOS_SOBRE_VENDAS = None
        linha_verificacao = 12
        ultima_linha = aba_apresentacao.max_row
        for linha in range(1, ultima_linha + 1):
            valor_celula = aba_apresentacao.cell(row=linha, column=2).value
            if valor_celula is None:
                continue
            
            if 'TRIBUTOS SOBRE VENDAS' in aba_apresentacao.cell(row=linha, column=2).value:
                linha_TRIBUTOS_SOBRE_VENDAS = linha
                break
        
        return linha_TRIBUTOS_SOBRE_VENDAS

    def inserir_linha_dados_na_apresentacao(self, linha: int):
        aba_dados = self.workbook['Dados']
        
        descricao = aba_dados.cell(row=linha, column=1).value
        formula_total = f'=Dados!{openpyxl.utils.get_column_letter(aba_dados.max_column)}{linha}'
        formula_quantidade_meses_com_valor = f'=COUNTIF(Dados!B{linha}:{openpyxl.utils.get_column_letter(aba_dados.max_column - 1)}{linha}, "<>")'
    
        aba_apresentacao = self.workbook['Apresentação']
        linha_TRIBUTOS_SOBRE_VENDAS = self.get_linha_tributos_sobre_vendas()
        
        #insere linha acima da linha de tributos sobre vendas
        if linha_TRIBUTOS_SOBRE_VENDAS is None:
            return
        
        aba_apresentacao.insert_rows(linha_TRIBUTOS_SOBRE_VENDAS)
        
        celula_faturamento = "$F$14"
        formula_porcentagem_total_sobre_faturamento = f'=F{linha_TRIBUTOS_SOBRE_VENDAS}/{celula_faturamento}'
        
        coluna_B = get_number_for_letter('B')
        coluna_F = get_number_for_letter('F')
        coluna_G = get_number_for_letter('G')
        coluna_H = get_number_for_letter('H')
        
        #borda espessa esquerda na "B" e borda espessa direita ta "H"
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_B).border = openpyxl.styles.Border(left=openpyxl.styles.Side(style='medium'))
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_H).border = openpyxl.styles.Border(right=openpyxl.styles.Side(style='medium'))
        
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_B, value=descricao)
        
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_F, value=formula_total).number_format = '#,##0.00'
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_F).alignment = openpyxl.styles.Alignment(horizontal='center')
        
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_G, value=formula_porcentagem_total_sobre_faturamento).number_format = '0.00%'
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_G).alignment = openpyxl.styles.Alignment(horizontal='center')
        
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_H, value=formula_quantidade_meses_com_valor)
        aba_apresentacao.cell(row=linha_TRIBUTOS_SOBRE_VENDAS, column=coluna_H).alignment = openpyxl.styles.Alignment(horizontal='center')
        
            
                                      
if __name__ == '__main__':
    planilha_path = 'template.xlsx'
    
    planilha = Planilha(planilha_path)
    
    planilha.set_CNPJ('123456789')
    planilha.set_EMPRESA('Empresa ABC')
    planilha.inserir_colunas_mes_aba_dados(1, 2019, 12, 2021)
    planilha.insert_dados_aba_dados([
        {
            'descricao': 'Receita',
            '2019-01': 100,
            '2019-02': 200,
        },
        {
            'descricao': 'Despesa',
            '2019-01': 50,
            '2019-02': 100,
        }
    ])
    planilha.inserir_linha_dados_na_apresentacao(2)
    
    planilha.save('output.xlsx')