import json
import subprocess
import base64

from src.config import getConfig, setConfig

api_url_servicos_consultar = "https://gateway.apiserpro.serpro.gov.br/integra-contador/v1/Consultar"
numero_contratante = "13676599000120"

def apiRequest(curl_command):
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        
        json_string = result.stdout.split("\n\n")[1]
        result_infos = result.stdout.split("\n\n")[0].split('\n')
        status_code = result_infos[0].split(' ')[1]
        
        result.json = json.loads(json_string)
        result.status_code = status_code
    except subprocess.CalledProcessError as e:
        result = e
        result.json = {}
        result.status_code = "500"
    
    return result

def apiLogin(certificado_path, certificado_senha):
    config = getConfig()
    
    consumer_key = config['api_serpro']['consumer_key']
    consumer_secret = config['api_serpro']['consumer_secret']
    
    consumer_key_secret = f"{consumer_key}:{consumer_secret}"
    consumer_key_secret_base64 = base64.b64encode(consumer_key_secret.encode()).decode()
    
    
    curl_command = [
        "curl", "-i", "-X", "POST",
        "-H", f"Authorization: Basic {consumer_key_secret_base64}",
        "-H", "Role-Type: TERCEIROS",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-d", "grant_type=client_credentials",
        "--cert", f"{certificado_path}:{certificado_senha}",
        "https://autenticacao.sapi.serpro.gov.br/authenticate"
    ]
    
    resultado = apiRequest(curl_command)
    if resultado.returncode != 0:
        print("Erro ao autenticar na API do Serpro:", resultado.stderr)
        config['api_serpro']['bearer_token'] = ""
        config['api_serpro']['ultimo_ceritifcado'] = {
            "path": "",
            "senha": ""
        }
        setConfig(config)
        return False
    
    if resultado.status_code != "200":
        print("Erro ao autenticar na API do Serpro:", resultado.json)
        config['api_serpro']['bearer_token'] = ""
        config['api_serpro']['ultimo_ceritifcado'] = {
            "path": "",
            "senha": ""
        }
        setConfig(config)
        return False
    
    bearer_token = resultado.json['access_token']
    config['api_serpro']['bearer_token'] = bearer_token
    config['api_serpro']['ultimo_ceritifcado'] = {
        "path": certificado_path,
        "senha": certificado_senha
    }
    setConfig(config)
    
    return bearer_token

def get_pgdasd(ano, mes):
    mes_string = str(mes).zfill(2)
    
    dados = { 
        "periodoApuracao": f"{ano}{mes_string}",
    }
    
    dados_json = json.dumps(dados)
    
    body = {
      "contratante": {
        "numero": f"{numero_contratante}",
        "tipo": 2
      },
      "autorPedidoDados": {
        "numero": "00000000000000",
        "tipo": 2
      },
      "contribuinte": {
        "numero": "00000000000000",
        "tipo": 2
      },         
      "pedidoDados": {
        "idSistema": "PGDASD",
        "idServico": "CONSDECLARACAO13",
        "versaoSistema": "1.0",
        "dados": dados_json
      }
    }
    
    body_json = json.dumps(body)
    
    config = getConfig()
    bearer_token = config['api_serpro']['bearer_token']
    if not bearer_token:
        certificado_path = config['api_serpro']['ultimo_ceritifcado']['path']
        certificado_senha = config['api_serpro']['ultimo_ceritifcado']['senha']
        bearer_token = apiLogin(certificado_path, certificado_senha)
        
    if not bearer_token:
        return False
        
    curl_command = [
        "curl", "-i", "-X", "POST",
        "-H", f"Authorization: Bearer {bearer_token}",
        "-H", "Content-Type: application/json",
        "-d", body_json,
        api_url_servicos_consultar
    ]
    
    resultado = apiRequest(curl_command)
    if resultado.returncode != 0:
        print(f"Erro ao consultar PGDASD do periodo {ano}/{mes}:", resultado.stderr)
        return False
    
    if resultado.status_code != "200":
        is_bearer_token_invalid = resultado.status_code == "401"
        
        if not is_bearer_token_invalid:
            print(f"Erro ao consultar PGDASD do periodo {ano}/{mes}:", resultado.json)
            
            return False
        
        certificado_path = config['api_serpro']['ultimo_ceritifcado']['path']
        certificado_senha = config['api_serpro']['ultimo_ceritifcado']['senha']
    
        bearer_token = apiLogin(certificado_path, certificado_senha)
        if not bearer_token:
            return False
        
        resultado = apiRequest(curl_command)
        if resultado.returncode != 0:
            print(f"(Bearer Token Invalido) Erro ao consultar PGDASD do periodo {ano}/{mes}:", resultado.stderr)
            return False
        
        if resultado.status_code != "200":
            print(f"(Bearer Token Invalido) Erro ao consultar PGDASD do periodo {ano}/{mes}:", resultado.json)
            
            return False
    
    return resultado.json
    
    
    
if __name__ == "__main__":
    certificado_path = "downloads/Arquivos teste Entercap/Certificado/MARKETSWY.pfx"
    certificado_senha = "Mrf222122"
    
    bearer_token = apiLogin(certificado_path, certificado_senha)
    print(bearer_token)
    
    resultado = get_pgdasd(2024, 11)
    print(resultado)