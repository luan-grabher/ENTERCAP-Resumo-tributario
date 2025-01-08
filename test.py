'''
    Como solicitar os Tokens de Acesso Bearer e JWT token
    Para solicitar os tokens temporários, é necessário realizar uma requisição HTTP POST para o endpoint authenticate https://autenticacao.sapi.serpro.gov.br/authenticate, com as seguintes características:

    a) Certificado Digital e-CNPJ padrão ICP-Brasil válido;

    b) HTTP Header:

    - "Authorization": "Basic (base64(consumerKey:consumerSecret))"
    - "role-type": "TERCEIROS"
    - "content-type": "application/x-www-form-urlencoded"
    Para utilização no parâmetro Authorization, é necessário concatenar os códigos Consumer Key e Consumer Secret, separados pelo caracter :, e converter o resultado em BASE64. No exemplo a seguir, é retornada a string ZGphUjIx[...]IzT3RlCg:

    echo -n "djaR21PGoYp1iyK2n2ACOH9REdUb:ObRsAJWOL4fv2Tp27D1vd8fB3Ote" | base64
    Resultado:

    ZGphUjIxUEdvWXAxaXlLMm4yQUNPSDlSRWRVYjpPYlJzQUpXT0w0ZnYyVHAyN0QxdmQ4ZkIzT3RlCg
    Abaixo segue um exemplo de chamada via cUrl:

    curl -i -X POST \
    -H "Authorization:Basic ZGphUjIxUEdvWXAxaXlLMm4yQUNPSDlSRWRVYjpPYlJzQUpXT0w0ZnYyVHAyN0QxdmQ4ZkIzT3RlCg" \
    -H "Role-Type:TERCEIROS" \
    -H "Content-Type:application/x-www-form-urlencoded" \
    -d 'grant_type=client_credentials' \
    --cert-type P12 \
    --cert arquivo_certificado.p12:senha_certificado \
    'https://autenticacao.sapi.serpro.gov.br/authenticate'
    API protegida com Certificado Digital SSL

    Toda requisição de autenticação na loja do Serpro deverá ser informado o arquivo do certificado digital do tipo .p12 ou .pfx acompanhado da senha do certificado.
    Para executar esse script via curl, é necessário mudar para a pasta do arquivo do certificado.

    Content-type

    Caso experiencie erros de 415 Unsupported Media Type na chamada de solicitação do Token, utilize o campo do Header Content-Type com o valor application/x-www-form-urlencoded

    [HEADER] Content-type: "application/x-www-form-urlencoded"
    
    
    
    
CÓDIGO QUE FUNCIONA:

curl -i -X POST `
-H "Authorization: Basic SERJMTQ2ejBWemN4dF9iRHJrSDhpbngzVDljYTpsbnhmVHhoWV9ZV1dFaTV5ZWZ5X3M0eTRvR3dh" `
-H "Role-Type: TERCEIROS" `
-H "Content-Type: application/x-www-form-urlencoded" `
-d 'grant_type=client_credentials' `
--cert "downloads/Arquivos teste Entercap/Certificado/MARKETSWY.pfx:Mrf222122" `
"https://autenticacao.sapi.serpro.gov.br/authenticate"



'''
# Configurações
consumer_key = 'HDI146z0Vzcxt_bDrkH8inx3T9ca'
consumer_secret = 'lnxfTxhY_YWWEi5yefy_s4y4oGwa'

import subprocess

# Comando curl
curl_command = [
    "curl", "-i", "-X", "POST",
    "-H", "Authorization: Basic SERJMTQ2ejBWemN4dF9iRHJrSDhpbngzVDljYTpsbnhmVHhoWV9ZV1dFaTV5ZWZ5X3M0eTRvR3dh",
    "-H", "Role-Type: TERCEIROS",
    "-H", "Content-Type: application/x-www-form-urlencoded",
    "-d", "grant_type=client_credentials",
    "--cert", "downloads/Arquivos teste Entercap/Certificado/MARKETSWY.pfx:Mrf222122",
    "https://autenticacao.sapi.serpro.gov.br/authenticate"
]

# Executar o comando curl
try:
    result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
    print("Status Code:", result.returncode)
    print("Resposta:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Erro na execução do comando curl:", e)
