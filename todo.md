# ECAC - RELACAO PGTOS

LISTAGEM DE CODIGOS da arrecadação:

https://siefreceitas.receita.economia.gov.br/codigos-de-receita-de-tributos-e-contribuicoes-darf-e-dje

Com base na tabela extraida:
- [x] Colocar em alguma aba os código de receita para DE-PARA
- [x] Normalizar a tabela agrupando por codigo de receita
- [x] Inserir no array as denominações de receita com base no 'código de receita'. Pegar pela coluna 'denominação da receita'
- [x] Somar o valor total agrupado pelo codigo
- [x] Inserir na aba dados a relação de pagamentos, no nome utilizar o código + a denominação
- [x] Na aba 'apresentação' colocar os valores somados por código abaixo de 'compras, vendas e 'folha' e deixar uma linha em branco
- [x] Em qtd colocar a quantidade de meses que tem valor


# ECAC PGDAS

* Apenas o ultimo arquivo enviado de cada mes (pode ter mais de um no mesmo mes)

### PDFs de PGDAS (Cada pdf é um mes)


- Caixas "Valor do Débito por Tributo para a Atividade"
  - "Receita Bruta informada"
  	
	Com base no texto entre o titulo e 'receita bruta informada' é possivel validar se é com ou sem substituição tributária
	- [x] Extrair receita com substituição tributária
	- [x] Extrair receita sem substituição tributária
	- [ ] Na planilha colocar por mês na aba 'dados' os valores
	- [ ] Na aba 'apresentação' colocar o total somado como 'Receita com ST' e 'Receita sem ST'
	- [ ] Em qtd colocar a quantidade de meses que tem valor

	- [ ] Verificar com Regis o que fazer quando existem várias empresas


- Caixa "Total geral empresa"
	- [ ] Extrair 'Total debito Exigivel -> total (bem no canto direito ao lado dos impostos)'
	- [ ] Na planilha colocar como 'DAS' por mês na aba 'dados' os valores de cada mês
	- [ ] Na aba 'apresentação' colocar o total somado como 'Simples Nacional' se houver valor em pelo menos 1 mês
	- [ ] Em qtd colocar a quantidade de meses que tem valor


# ESOCIAL contribuicao folha

### Para cada mês:
 - [x] Extrair 'Base de Calculo' como 'Folha' na aba 'dados'
 - [x] Extrair 'Valor Contribuição' como 'INSS - Esocial' na aba 'dados'
 - [x] Na aba 'apresentação' colocar o total somado como 'Folha'
 - [x] Em qtd colocar a quantidade de meses que tem valor
 - [x] Na aba 'apresentação' colocar o total somado como 'INSS - Esocial' junto com os outros impostos