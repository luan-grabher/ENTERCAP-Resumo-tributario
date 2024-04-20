#atualiza pip e instala as dependencias
import os

os.system('python -m pip install --upgrade pip')
os.system('pip install -r requirements.txt')
os.system('cls')

from src.menu.menu import main

main()
exit(0)