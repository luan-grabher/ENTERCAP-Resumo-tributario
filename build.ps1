pyinstaller main.py --noconfirm --onefile --add-data "./src;src/" --paths "./venv/Lib/site-packages"
New-Item -ItemType Directory -Path "./dist/src/ecac/relacao_pgtos/" -Force
Copy-Item -Path "./src/ecac/relacao_pgtos/codigos_receita.json" -Destination "./dist/src/ecac/relacao_pgtos/"
Copy-Item -Path "./template.xlsx" -Destination "./dist/"
Copy-Item -Path "./entercap_banner.jpg" -Destination "./dist/"
clear
Write-Host "Build concluído com sucesso!"