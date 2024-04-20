import json
import os

default_config = {
    "variavel": "valor",
}

config_path = "config.json"

def getConfig():
    is_exists_config_file = os.path.exists(config_path)
    
    if not is_exists_config_file:
        setConfig(default_config)
    
    config = {}
    with open(config_path, encoding='utf-8') as json_file:
        config = json.load(json_file)
    
    
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    setConfig(config)

    # Substitui "%USERNAME%" pelo nome de usuário nos caminhos
    for key, value in config.items():
        if isinstance(value, str):
            config[key] = value.replace("%USERNAME%", os.getlogin())

    return config

def setConfig(config):
    with open(config_path, "w", encoding='utf-8') as json_file:
        json.dump(config, json_file, ensure_ascii=False, indent=4)
        
    return config
    
if __name__ == "__main__":
    config = getConfig()
    print(config)