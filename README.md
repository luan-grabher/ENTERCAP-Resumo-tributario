# ENTERCAP-Resumo-tributario
Busca informações nos sites da receita para criar uma planilha de resumo triutario para o cliente.

## Executavel

```bash
pyinstaller --noconfirm --onedir --console --paths "C:\Users\luan\Documents\Projetos\Entercap\ENTERCAP-Resumo-tributario\.venv\Lib\site-packages" --add-data "C:\Users\luan\Documents\Projetos\Entercap\ENTERCAP-Resumo-tributario\entercap_banner.jpg;." --add-data "C:\Users\luan\Documents\Projetos\Entercap\ENTERCAP-Resumo-tributario\requirements.txt;." --add-data "C:\Users\luan\Documents\Projetos\Entercap\ENTERCAP-Resumo-tributario\template.xlsx;." --add-data "C:\Users\luan\Documents\Projetos\Entercap\ENTERCAP-Resumo-tributario\src;src/"  "C:\Users\luan\Documents\Projetos\Entercap\ENTERCAP-Resumo-tributario\main.py"
```